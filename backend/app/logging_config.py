"""Structured logging configuration."""

import json
import logging
from datetime import datetime
from pythonjsonlogger import jsonlogger


class StructuredFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter for structured logging."""

    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record['timestamp'] = datetime.utcnow().isoformat()
        log_record['level'] = record.levelname
        log_record['logger'] = record.name
        log_record['module'] = record.module


def setup_logging():
    """Configure structured logging."""
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # JSON formatter for structured logs
    json_formatter = StructuredFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s'
    )

    # File handler for JSON logs
    file_handler = logging.FileHandler('app.log')
    file_handler.setFormatter(json_formatter)
    file_handler.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)

    # Console handler with simple format
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)


def get_logger(name):
    """Get logger instance."""
    return logging.getLogger(name)
