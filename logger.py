import logging, sys

logger = "arachnid"

def get_logger(level=logging.INFO):
    logger = logger.getLogger(logger)
    if logger.handlers:
        return logger
    logger.setLevel(level)
    
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "[%(levelname)s] %(asctime)s | %(name)s | %(message)s",
        datefmt="%H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False
    
    return logger
    