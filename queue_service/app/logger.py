import logging
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional, Union

from .config import config


class CustomFormatter(logging.Formatter):
    """
    Custom log formatter that outputs logs in a structured JSON format
    
    Includes metadata about request/response when available
    """
    
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add extra fields if available
        if hasattr(record, "source"):
            log_data["source"] = record.source
        if hasattr(record, "destination"):
            log_data["destination"] = record.destination
        if hasattr(record, "headers"):
            log_data["headers"] = record.headers
        if hasattr(record, "metadata"):
            log_data["metadata"] = record.metadata
        if hasattr(record, "body"):
            # Handle the case where body might be an object that needs serialization
            try:
                if isinstance(record.body, (dict, list)):
                    log_data["body"] = record.body
                else:
                    log_data["body"] = str(record.body)
            except:
                log_data["body"] = str(record.body)
        
        # Add exception info if available
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


def setup_logger():
    """Set up and configure the logger"""
    logger = logging.getLogger("queue_service")
    
    # Set log level from config
    log_level = config.get("log_level", "INFO")
    level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(level)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(CustomFormatter())
    logger.addHandler(console_handler)
    
    # Create file handler
    try:
        file_handler = logging.FileHandler("queue_service.log")
        file_handler.setFormatter(CustomFormatter())
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not create log file: {str(e)}")
    
    return logger


# Create logger instance
logger = setup_logger()

def log_message(queue_name: str, message: Dict, action: str):
    """Log message operations to queue_service.log"""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "queue": queue_name,
        "action": action,  # "push" or "pull"
        "message_id": message.get("id"),
        "message_type": message.get("message_type"),
        "content": message.get("content")
    }
    logger.info(json.dumps(log_entry))

def log_request_response(
    source: str,
    destination: str,
    headers: Optional[Dict[str, str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    body: Optional[Union[Dict[str, Any], str]] = None,
    level: str = "INFO"
):
    """
    Log a request or response with the required fields
    
    Args:
        source: Source of the request/response
        destination: Destination of the request/response
        headers: HTTP headers if applicable
        metadata: Additional metadata
        body: Request/response body
        level: Log level (INFO, WARNING, ERROR, etc.)
    """
    logger_method = getattr(logger, level.lower(), logger.info)
    
    extra = {
        "source": source,
        "destination": destination,
        "headers": headers or {},
        "metadata": metadata or {},
        "body": body or {}
    }
    
    logger_method("Request/Response", extra=extra)
