import logging, sys

#logger_name = "arachnid"

# Logging colours
reset = "\033[0m"
green = "\033[32m"
yellow = "\033[33m"
blue = "\033[34m"
red = "\033[31m"
bold_red = "\033[1;31m"


class ColourFormatter(logging.Formatter):
    # specifies each logging level colour/format
    level_colours = {
        logging.INFO: green,
        logging.WARNING: yellow,
        logging.DEBUG: blue,
        logging.ERROR: red,
        logging.CRITICAL: bold_red
    }
    
    def format(self, record):
        colour = self.level_colours.get(record.levelno, reset)
        # sets record logging specs and patterns: COLOUR, LOGGING LEVEL, RESET TO DEFAULT
        record.levelname = f"{colour}{record.levelname}{reset}"
        record.msg = f"{colour}{record.msg}{reset}"

        return super().format(record)

# main function to call to initialise a new logger for each script
def get_logger(logger_name: str, level=logging.INFO):
    logger = logging.getLogger(logger_name)
    if logger.handlers:
        logger.setLevel(level)
        return logger
    logger.setLevel(logging.DEBUG)
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    formatter = ColourFormatter(
        # format: TIME | LOG LEVEL | FILENAME BEING RUN | MESSAGE
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False
    
    return logger
    