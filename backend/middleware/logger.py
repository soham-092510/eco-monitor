# Import Python's built-in logging module
# WHY:
# - Provides a standard way to track events, errors, and debug info
# - Used instead of print() in real-world applications
import logging


# Configure global logging settings
# WHY:
# - Defines how logs will look and what level of logs will be captured
# - Applies to the entire application
logging.basicConfig(

    # Set minimum log level
    # WHY:
    # - INFO means:
    #   - INFO, WARNING, ERROR, CRITICAL will be shown
    #   - DEBUG will be ignored
    level=logging.INFO,

    # Define log message format
    # WHY:
    # - Makes logs structured and readable
    # - Helps debugging and monitoring
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)


# Create a logger instance for your app
# WHY:
# - "green-finance" is the name of your application/module
# - Helps identify where logs are coming from
# - You can create multiple loggers for different modules if needed
logger = logging.getLogger("green-finance")