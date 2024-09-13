LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "access": {
            "format": "%(asctime)s - %(levelname)s - %(client_addr)s - %(request_line)s - %(status_code)s"
        }
    },
    "handlers": {
        "default": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stdout"
        },
        "access": {
            "class": "logging.StreamHandler",
            "formatter": "access",
            "stream": "ext://sys.stdout"
        }
    },
    "loggers": {
        "uvicorn": {
            "level": "INFO",
            "handlers": ["default"],
            "propagate": False
        },
        "uvicorn.error": {
            "level": "INFO",
            "handlers": ["default"],
            "propagate": False
        },
        "uvicorn.access": {
            "level": "INFO",
            "handlers": ["access"],
            "propagate": False
        }
    }
}