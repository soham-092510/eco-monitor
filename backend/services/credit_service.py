# =====================================================================
# ECO MONITOR — CREDIT_SERVICE.PY (SERVICE)
# Purpose: Manages carbon credit inventories, credit transfers, and retirement.
#          Integrates Redis caching to reduce database read loads and uses
#          double-entry ledger checks to ensure financial integrity.
# =====================================================================

# Import Session from SQLAlchemy ORM
from sqlalchemy.orm import Session

# Import models
from backend.models.carbon_credit import CarbonCredit
from backend.models.credit import CreditRetirement
from backend.models.account import Account
from backend.models.user import User

# Import ledger posting function
from backend.services.ledger_service import post_ledger_transaction

# Import Redis client
import redis

# Import JSON for cache serialization
import json

# Import logger
from backend.middleware.logger import logger

# Import settings
from backend.core.config import settings

# Import FastAPI exception components
from fastapi import HTTPException, status

# Import typing utilities
from typing import List, Optional
import uuid

# Initialize Redis client connection
# WHY:
# - Connects to the Redis container using URL defined in environment settings
# - Wrapped in try-except block to prevent app startup crashes if Redis is temporarily offline
try:
    redis_client = redis.from_url(settings.redis_url, decode_responses=True)
except Exception as redis_err:
    logger.error(f"Failed to connect to Redis cache layer: {str(redis_err)}")
    redis_client = None


def get_user_credits(db: Session, user_id: str) -> List[CarbonCredit]:
    # Retrieve user's carbon credit asset inventory
    # WHY:
    # - Serves carbon credit details from Redis cache if available
    # - Falls back to database query and updates cache on miss
    cache_key = f"user_credits:{user_id}"
    
    # 1. Try to read from Redis cache
    if redis_client:
        try:
            cached_data = redis_client.get(cache_key)
            if cached_data:
                logger.info(f"Cache Hit | Serving carbon credit listings for user: {user_id}")
                # Deserialize from JSON list back to dictionary representation
                raw_list = json.loads(cached_data)
                # Map standard dictionary elements to match attributes
                return raw_list
        except Exception as cache_err:
            logger.warning(f"Failed to read from Redis cache: {str(cache_err)}")
            
    # 2. Cache Miss: Query the database
    logger.info(f"Cache Miss | Querying database for carbon credits of user: {user_id}")
    credits = db.query(CarbonCredit).filter(CarbonCredit.user_id == user_id).all()
    
    # 3. Serialize and save to Redis for future requests
    if redis_client and credits:
        try:
            # Map SQLAlchemy models to standard dictionaries
            serialized_credits = [
                {
                    "id": c.id,
                    "user_id": c.user_id,
                    "credit_type": c.credit_type,
                    "amount": c.amount,
                    "source": c.source,
                    "vintage_year": c.vintage_year,
                    "serial_number": c.serial_number,
                    "status": c.status,
                    "created_at": c.created_at.isoformat() if c.created_at else None
                }
                for c in credits
            ]
            # Save into Redis with 60-second expiration TTL
            redis_client.setex(cache_key, 60, json.dumps(serialized_credits))
        except Exception as cache_err:
            logger.warning(f"Failed to write to Redis cache: {str(cache_err)}")
            
    return credits


def invalidate_user_cache(user_id: str):
    # Invalidate user cache on modifications
    # WHY:
    # - Ensures subsequent queries fetch fresh data from database after updates
    if redis_client:
        try:
            redis_client.delete(f"user_credits:{user_id}")
            logger.info(f"Cache Invalidated | Cleared cache for user: {user_id}")
        except Exception as cache_err:
            logger.warning(f"Failed to clear Redis key: {str(cache_err)}")


def mint_carbon_credit(
    db: Session,
    user_id: str,
    credit_type: str,
    amount: float,
    source: str,
    vintage_year: int
) -> CarbonCredit:
    # Mints a new Carbon Credit asset to a user
    # WHY:
    # - Creates the asset and records a balancing debit/credit transaction in the ledger
    
    # 1. Generate unique serial number for registry
    serial_number = f"GF-{vintage_year}-{credit_type[:3].upper()}-{uuid.uuid4().hex[:8].upper()}"
    
    # 2. Get user's Carbon Asset Account
    user_asset_account = db.query(Account).filter(
        Account.user_id == user_id,
        Account.name == "carbon_asset"
    ).first()
    
    if not user_asset_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User carbon asset account not found."
        )
        
    # Get/create virtual system issuance account to balance the ledger
    system_issuance_account = db.query(Account).filter(
        Account.user_id == "system",
        Account.name == "issuance"
    ).first()
    
    if not system_issuance_account:
        # Create system issuance account (normal balance type: liability/equity)
        system_issuance_account = Account(
            user_id="system",
            name="issuance",
            type="liability",
            balance=10000000.0  # Large initial pool
        )
        db.add(system_issuance_account)
        db.flush()
        
    # 3. Create CarbonCredit record
    new_credit = CarbonCredit(
        user_id=user_id,
        credit_type=credit_type,
        amount=amount,
        source=source,
        vintage_year=vintage_year,
        serial_number=serial_number,
        status="active"
    )
    db.add(new_credit)
    db.flush()
    
    # 4. Record the double-entry transaction
    # - Debit: User's Asset Account (increases user balance)
    # - Credit: System Issuance Account (decreases system balance)
    ledger_entries = [
        {"account_id": user_asset_account.id, "type": "debit", "amount": amount},
        {"account_id": system_issuance_account.id, "type": "credit", "amount": amount}
    ]
    post_ledger_transaction(
        db=db,
        description=f"Mint Carbon Credit: {serial_number}",
        entries=ledger_entries
    )
    
    # 5. Invalidate cache
    invalidate_user_cache(user_id)
    
    return new_credit


def transfer_carbon_credit(
    db: Session,
    sender_id: str,
    recipient_username: str,
    credit_id: str,
    transfer_amount: float
) -> CarbonCredit:
    # Transfers carbon credits from sender to recipient
    # WHY:
    # - Updates asset ownership and updates double-entry account balances
    
    # 1. Fetch credit details
    credit = db.query(CarbonCredit).filter(
        CarbonCredit.id == credit_id,
        CarbonCredit.user_id == sender_id,
        CarbonCredit.status == "active"
    ).with_for_update().first()
    
    if not credit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active carbon credit asset not found or access denied."
        )
        
    if credit.amount < transfer_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient credit amount. Available: {credit.amount}, Requested: {transfer_amount}"
        )
        
    # 2. Fetch recipient
    recipient = db.query(User).filter(User.username == recipient_username).first()
    if not recipient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipient user '{recipient_username}' not found."
        )
        
    # 3. Retrieve accounts
    sender_account = db.query(Account).filter(Account.user_id == sender_id, Account.name == "carbon_asset").first()
    recipient_account = db.query(Account).filter(Account.user_id == recipient.id, Account.name == "carbon_asset").first()
    
    if not sender_account or not recipient_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset accounts not found for transaction."
        )
        
    # 4. Post double-entry transaction
    # - Debit: Recipient's Carbon Asset (+ recipient balance)
    # - Credit: Sender's Carbon Asset (- sender balance)
    ledger_entries = [
        {"account_id": recipient_account.id, "type": "debit", "amount": transfer_amount},
        {"account_id": sender_account.id, "type": "credit", "amount": transfer_amount}
    ]
    post_ledger_transaction(
        db=db,
        description=f"Transfer Credit {credit.serial_number} to {recipient_username}",
        entries=ledger_entries
    )
    
    # 5. Split or reassign the CarbonCredit asset record
    if credit.amount == transfer_amount:
        # Full transfer: update ownership
        credit.user_id = recipient.id
        db.add(credit)
    else:
        # Partial transfer: decrease sender's amount and create a new credit record for recipient
        credit.amount -= transfer_amount
        db.add(credit)
        
        recipient_credit = CarbonCredit(
            user_id=recipient.id,
            credit_type=credit.credit_type,
            amount=transfer_amount,
            source=credit.source,
            vintage_year=credit.vintage_year,
            serial_number=f"GF-{credit.vintage_year}-{credit.credit_type[:3].upper()}-{uuid.uuid4().hex[:8].upper()}",
            status="active"
        )
        db.add(recipient_credit)
        
    db.commit()
    
    # 6. Invalidate caches for both users
    invalidate_user_cache(sender_id)
    invalidate_user_cache(recipient.id)
    
    return credit


def retire_carbon_credit(
    db: Session,
    user_id: str,
    credit_id: str,
    retire_amount: float,
    notes: Optional[str] = None
) -> CreditRetirement:
    # Permanently offset (burn) carbon credits
    # WHY:
    # - Reduces carbon asset balance, reduces carbon liability balance, and generates offset certificate
    
    # 1. Fetch active credit
    credit = db.query(CarbonCredit).filter(
        CarbonCredit.id == credit_id,
        CarbonCredit.user_id == user_id,
        CarbonCredit.status == "active"
    ).with_for_update().first()
    
    if not credit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active carbon credit asset not found or access denied."
        )
        
    if credit.amount < retire_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient credit amount to retire. Available: {credit.amount}"
        )
        
    # 2. Get user's Carbon Asset and Carbon Liability Accounts
    asset_account = db.query(Account).filter(Account.user_id == user_id, Account.name == "carbon_asset").first()
    liability_account = db.query(Account).filter(Account.user_id == user_id, Account.name == "carbon_liability").first()
    
    if not asset_account or not liability_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User accounts not found for retirement."
        )
        
    # 3. Post double-entry transaction
    # - Debit: Liability Account (reduces carbon liability debt)
    # - Credit: Asset Account (reduces carbon credit asset balance)
    ledger_entries = [
        {"account_id": liability_account.id, "type": "debit", "amount": retire_amount},
        {"account_id": asset_account.id, "type": "credit", "amount": retire_amount}
    ]
    post_ledger_transaction(
        db=db,
        description=f"Retire Carbon Credit: {credit.serial_number}",
        entries=ledger_entries
    )
    
    # 4. Generate Certificate Proof
    certificate_number = f"CERT-RET-{uuid.uuid4().hex[:12].upper()}"
    retirement = CreditRetirement(
        user_id=user_id,
        carbon_credit_id=credit_id,
        amount=retire_amount,
        certificate_number=certificate_number,
        notes=notes
    )
    db.add(retirement)
    
    # 5. Update the Credit Asset Row
    if credit.amount == retire_amount:
        credit.status = "retired"
        db.add(credit)
    else:
        # Split credit: decrease active pool, create new retired record
        credit.amount -= retire_amount
        db.add(credit)
        
        retired_split = CarbonCredit(
            user_id=user_id,
            credit_type=credit.credit_type,
            amount=retire_amount,
            source=credit.source,
            vintage_year=credit.vintage_year,
            serial_number=f"GF-{credit.vintage_year}-{credit.credit_type[:3].upper()}-{uuid.uuid4().hex[:8].upper()}",
            status="retired"
        )
        db.add(retired_split)
        
    db.commit()
    db.refresh(retirement)
    
    # 6. Invalidate cache
    invalidate_user_cache(user_id)
    
    return retirement
