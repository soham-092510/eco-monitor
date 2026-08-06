# =====================================================================
# ECO MONITOR — LEDGER_SERVICE.PY (SERVICE)
# Purpose: Core double-entry ledger execution engine. Enforces balanced
#          journal entries (Debits = Credits) and handles atomic rollbacks
#          using row locking and database constraints.
# =====================================================================

# Import Session from SQLAlchemy ORM
from sqlalchemy.orm import Session

# Import models
from backend.models.transaction import Transaction
from backend.models.ledger_entry import LedgerEntry
from backend.models.account import Account

# Import HTTPException and status from FastAPI
from fastapi import HTTPException, status

# Import List and Dict types
from typing import List, Dict


def post_ledger_transaction(
    db: Session,
    description: str,
    entries: List[Dict]
) -> Transaction:
    # Executes an atomic double-entry transaction
    # WHY:
    # - Enforces Debits = Credits
    # - Uses row locking to prevent race conditions (concurrency safety)
    # - Triggers automatic database rollbacks if constraint checks fail
    
    # 1. Enforce double-entry balanced rule (Debits = Credits)
    # WHY:
    # - Bookkeeping integrity requires the total value of debits to equal credits
    debits = sum(e["amount"] for e in entries if e["type"] == "debit")
    credits = sum(e["amount"] for e in entries if e["type"] == "credit")
    
    # Allow a tiny float tolerance for precision
    if abs(debits - credits) > 1e-6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unbalanced ledger entry. Debits ({debits}) must equal Credits ({credits})"
        )
        
    try:
        # 2. Create the parent Transaction header
        # WHY:
        # - Acts as the parent journal entry grouping individual debits and credits
        transaction_header = Transaction(description=description)
        db.add(transaction_header)
        db.flush()  # Populates transaction_header.id UUID
        
        # 3. Process each entry individually
        for entry in entries:
            account_id = entry["account_id"]
            entry_type = entry["type"].lower()
            amount = entry["amount"]
            
            # Fetch the account with write-lock (SELECT FOR UPDATE)
            # WHY:
            # - Prevents concurrent transactions from reading stale balances
            account = db.query(Account).filter(Account.id == account_id).with_for_update().first()
            if not account:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Account with ID {account_id} not found."
                )
                
            # 4. Update the account balance depending on its accounting type
            # WHY:
            # - Asset: Debits increase (+), Credits decrease (-)
            # - Liability: Credits increase (+), Debits decrease (-)
            if account.type == "asset":
                if entry_type == "debit":
                    account.balance += amount
                elif entry_type == "credit":
                    account.balance -= amount
            elif account.type == "liability":
                if entry_type == "credit":
                    account.balance += amount
                elif entry_type == "debit":
                    account.balance -= amount
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported account type: {account.type}"
                )
                
            # Flush changes to trigger database CHECK constraints
            # WHY:
            # - Forces the database to check 'chk_positive_balance' immediately
            # - If balance drops below 0, it throws an IntegrityError, initiating a rollback
            db.add(account)
            db.flush()
            
            # 5. Record the LedgerEntry log
            ledger_entry = LedgerEntry(
                transaction_id=transaction_header.id,
                account_id=account.id,
                type=entry_type,
                amount=amount,
                running_balance=account.balance
            )
            db.add(ledger_entry)
            
        # 6. Commit the entire transaction atomically
        # WHY:
        # - Saves transaction header and all entries together
        # - If any step failed, rollback will run automatically in the except block
        db.commit()
        db.refresh(transaction_header)
        return transaction_header
        
    except Exception as err:
        # 7. Rollback transaction on failure
        # WHY:
        # - Restores DB to original state to prevent orphaned records or corrupted balances
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ledger transaction failed: {str(err)}"
        )


def get_user_ledger(db: Session, user_id: str) -> List[Dict]:
    # Retrieve ledger entries list for a specific user
    # WHY:
    # - Performs a query joining LedgerEntry and Transaction tables to return UI-ready logs
    results = db.query(
        LedgerEntry.id,
        LedgerEntry.type,
        LedgerEntry.amount,
        LedgerEntry.running_balance,
        LedgerEntry.created_at,
        Transaction.description
    ).join(
        Transaction, LedgerEntry.transaction_id == Transaction.id
    ).join(
        Account, LedgerEntry.account_id == Account.id
    ).filter(
        Account.user_id == user_id
    ).order_by(
        LedgerEntry.created_at.desc()
    ).all()
    
    # Format database rows into dictionaries matching our schema
    return [
        {
            "id": r.id,
            "type": r.type,
            "amount": r.amount,
            "balance": r.running_balance,
            "created_at": r.created_at,
            "description": r.description
        }
        for r in results
    ]
