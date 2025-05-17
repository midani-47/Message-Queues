import logging
import sys
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, Union

from .config import config


class CustomFormatter(logging.Formatter):
    """
    Custom log formatter that outputs logs in a structured format
    Includes metadata about request/response when available
    """
    
    def format(self, record):
        # Base format similar to previous assignment
        if hasattr(record, 'source') and hasattr(record, 'destination'):
            # This is a request/response log
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "source": record.source,
                "destination": record.destination
            }
            
            # Add headers if available
            if hasattr(record, "headers"):
                log_entry["headers"] = record.headers
                
            # Add metadata if available
            if hasattr(record, "metadata"):
                for key, value in record.metadata.items():
                    log_entry[key] = value
                    
            # Add body if available
            if hasattr(record, "body"):
                log_entry["body"] = record.body
                
            return json.dumps(log_entry)
        else:
            # Regular log
            return f"{datetime.utcnow().isoformat()} - {record.levelname} - {record.getMessage()}"


def setup_logger():
    """Set up and configure the logger"""
    logger = logging.getLogger("queue_service")
    
    # Clear any existing handlers to avoid duplicates
    if logger.handlers:
        logger.handlers = []
    
    # Set log level from config
    log_level = config.get("log_level", "INFO")
    level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(level)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(CustomFormatter())
    logger.addHandler(console_handler)
    
    # Create file handler - making sure the path is correct
    # Use the project root directory (not inside app directory)
    log_file_path = "queue_service.log"
    
    try:
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(CustomFormatter())
        logger.addHandler(file_handler)
        logger.info(f"Logging to file: {os.path.abspath(log_file_path)}")
    except Exception as e:
        logger.warning(f"Could not create log file: {str(e)}")
    
    return logger


# Create logger instance
logger = setup_logger()


def log_message(queue_name: str, message: Dict, action: str):
    """Log message operations to queue_service.log"""
    # Format timestamp as used in Assignment 2
    timestamp = datetime.utcnow().isoformat()
    
    # Get message content and type
    message_id = message.get("id", "unknown")
    message_type = message.get("message_type", "unknown")
    content = message.get("content", {})
    
    # Create log entry based on message type and action
    if message_type == "transaction":
        log_entry = {
            "timestamp": timestamp,
            "service": "queue_service",
            "action": action,
            "queue": queue_name,
            "message_id": message_id,
            "transaction_id": content.get("transaction_id", "unknown"),
            "customer_id": content.get("customer_id", "unknown"),
            "amount": content.get("amount", 0),
            "vendor_id": content.get("vendor_id", "unknown")
        }
    else:  # prediction
        log_entry = {
            "timestamp": timestamp,
            "service": "queue_service",
            "action": action,
            "queue": queue_name,
            "message_id": message_id,
            "transaction_id": content.get("transaction_id", "unknown"),
            "prediction": content.get("prediction", False),
            "confidence": content.get("confidence", 0.0),
            "model_version": content.get("model_version", "unknown")
        }
    
    # Log the entry
    logger.info(f"{action.capitalize()} message {message_id} in queue {queue_name}: {json.dumps(log_entry)}")


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
    
    # Create a record with the required fields
    extra = {
        "source": source,
        "destination": destination,
        "headers": headers or {},
        "metadata": metadata or {},
        "body": body or {}
    }
    
    # Log with extra parameters
    logger_method("Request/Response", extra=extra)