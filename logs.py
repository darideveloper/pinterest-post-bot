import logging

# logs to file
logging.basicConfig(
    filename='.log',
    format='%(asctime)s - %(filename)s (%(lineno)s) - %(levelname)s - %(message)s',
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Add both stream handler and file handler
logger.addHandler(logging.StreamHandler())
logger.addHandler(logging.FileHandler('.log'))

if __name__ == '__main__':
    # Example log messages
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
