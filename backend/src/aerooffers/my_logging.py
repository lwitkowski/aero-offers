import logging
import logging.config
import os

logging.config.fileConfig(
    os.path.dirname(os.path.abspath(__file__)) + os.sep + "logging.conf"
)


def remove_scrapy_handlers() -> None:
    """
    Remove handlers that Scrapy installs to prevent duplicate log messages.

    Scrapy installs its own logging handlers on all loggers (not just scrapy.* ones),
    which causes duplicate log messages when using a custom logging configuration.
    This function:
    1. Identifies and removes Scrapy's handler from the root logger by detecting
       its format pattern (contains '[' and ']' brackets)
    2. Keeps only our custom handler from logging.conf (format uses ' - ' separator)
    3. Removes all handlers from individual loggers to ensure they propagate to root
    4. Ensures proper propagation settings for all loggers

    This should be called after creating CrawlerProcess but before starting it,
    to catch all handlers that Scrapy might have installed during initialization.

    Our custom format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    Scrapy's format: "%(asctime)s [%(name)s] %(levelname)s: %(message)s"
    """
    root_logger = logging.getLogger()

    # Remove Scrapy's handler from root logger by identifying it via format
    # Our handler uses " - " separator, Scrapy's uses " [" and "] "
    for handler in root_logger.handlers[:]:
        if hasattr(handler, "formatter") and handler.formatter:
            if (
                hasattr(handler.formatter, "_fmt")
                and handler.formatter._fmt is not None
            ):
                fmt: str = handler.formatter._fmt
            else:
                fmt = str(handler.formatter)
            # Our format uses " - " separator, Scrapy's uses " [" and "] "
            if " - " not in fmt or "[" in fmt:
                # This is Scrapy's handler or an unknown handler, remove it
                root_logger.removeHandler(handler)
        else:
            # Handler without formatter, remove it
            root_logger.removeHandler(handler)

    # Remove handlers from all individual loggers to ensure they propagate to root
    # This ensures all log messages go through our single root handler
    for logger_name in list(logging.Logger.manager.loggerDict.keys()):
        logger_obj = logging.getLogger(logger_name)
        # Remove all handlers so messages propagate to root
        logger_obj.handlers = []
        # Ensure propagation to root (except root itself and azure which has propagate=0)
        if logger_name != "root" and not logger_name.startswith("azure"):
            logger_obj.propagate = True
