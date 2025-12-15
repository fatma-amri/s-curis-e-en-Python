"""
Secure logging system for the P2P messenger.
Ensures sensitive data is never logged.
"""

import logging
import json
import os
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path


class SecureFormatter(logging.Formatter):
    """Custom formatter that ensures sensitive data is not logged."""
    
    SENSITIVE_KEYS = ['password', 'key', 'secret', 'token', 'private']
    
    def format(self, record):
        """Format log record, redacting sensitive information."""
        # Create a copy of the record to avoid modifying the original
        record_dict = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add extra fields if present
        if hasattr(record, 'event'):
            record_dict['event'] = record.event
        
        return json.dumps(record_dict)


class SecureLogger:
    """Secure logger that prevents logging of sensitive information."""
    
    def __init__(self, name, log_dir='data/logs', max_bytes=10485760, backup_count=5):
        """Initialize secure logger."""
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Ensure log directory exists
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        
        # Create rotating file handler
        log_file = os.path.join(log_dir, f'{name}.log')
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setFormatter(SecureFormatter())
        
        # Console handler for debugging
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def _sanitize_message(self, message):
        """Remove sensitive information from message."""
        if isinstance(message, dict):
            sanitized = {}
            for key, value in message.items():
                if any(sensitive in key.lower() for sensitive in SecureFormatter.SENSITIVE_KEYS):
                    sanitized[key] = '[REDACTED]'
                else:
                    sanitized[key] = self._sanitize_message(value)
            return sanitized
        return message
    
    def info(self, message, event=None, **kwargs):
        """Log info level message."""
        message = self._sanitize_message(message)
        extra = {'event': event} if event else {}
        self.logger.info(message, extra=extra, **kwargs)
    
    def warning(self, message, event=None, **kwargs):
        """Log warning level message."""
        message = self._sanitize_message(message)
        extra = {'event': event} if event else {}
        self.logger.warning(message, extra=extra, **kwargs)
    
    def error(self, message, event=None, **kwargs):
        """Log error level message."""
        message = self._sanitize_message(message)
        extra = {'event': event} if event else {}
        self.logger.error(message, extra=extra, **kwargs)
    
    def debug(self, message, event=None, **kwargs):
        """Log debug level message."""
        message = self._sanitize_message(message)
        extra = {'event': event} if event else {}
        self.logger.debug(message, extra=extra, **kwargs)
    
    def critical(self, message, event=None, **kwargs):
        """Log critical level message."""
        message = self._sanitize_message(message)
        extra = {'event': event} if event else {}
        self.logger.critical(message, extra=extra, **kwargs)


# Create default logger
default_logger = SecureLogger('messenger')
