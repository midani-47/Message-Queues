# Message Queue Service for HPC Tasks

A high-performance message queue service for computational-intensive tasks, designed as part of a distributed system architecture.
We have a well-structured FastAPI application with:
- Docker support with volume persistence
- A modern lifespan context manager for startup/shutdown
- Proper CORS middleware
- Request/response logging middleware
- Role-based authentication
- Queue management and message operations endpoints
- A web UI


## Overview

This message queue service provides a reliable way to handle requests for computation-intensive tasks. It receives requests containing transactions and allows calculation workers to pull requests as soon as they are ready for processing.

The service implements:
- Queue management (create, list, delete)
- Message operations (push, pull)
- Persistent storage for queues
- Role-based access control
- Comprehensive logging

## Features

- **Queue Management**: Create, list, and delete queues with appropriate access controls
- **Message Operations**: Push messages to queues and pull messages from queues
- **Persistence**: Queues are automatically persisted to disk and can be restored on service restart
- **Configurable**: Persistence intervals and other settings can be configured via config.json
- **Fixed Queue Size**: Each queue has a maximum of 5 messages as specified in the config.json file. This limit cannot be modified through the UI and must be changed directly in the config file if needed
- **Role-Based Access Control**: Different access levels for administrators, agents, and regular users
- **Logging**: Comprehensive logging of all operations, requests, and responses
- **Error Handling**: Graceful handling of common error conditions (queue full, empty, etc.)
- **Docker Support**: Easy deployment using Docker and Docker Compose

## System Requirements

- Python 3.8 or higher
- Docker and Docker Compose (for containerized deployment)
- FastAPI and dependencies listed in requirements.txt

## Logging

The service logs all operations to `queue_service.log` in the root directory. The log format is structured JSON with the following information:

- For message operations (push/pull):
  ```json
  {
    "timestamp": "ISO-8601 timestamp",
    "queue": "queue_name",
    "action": "push or pull",
    "message_id": "unique message ID",
    "message_type": "transaction or prediction",
    "content": "message content"
  }
  ```

- For HTTP requests/responses:
  ```json
  {
    "timestamp": "ISO-8601 timestamp",
    "level": "INFO/WARNING/ERROR",
    "message": "Request/Response description",
    "module": "module name",
    "function": "function name",
    "line": "line number",
    "source": "request source",
    "destination": "request destination",
    "headers": "HTTP headers",
    "metadata": "additional metadata",
    "body": "request/response body"
  }
  ```

## Project Structure

```
/queue_service
├── app/                      # Application code
│   ├── __init__.py
│   ├── auth.py              # Authentication and authorization
│   ├── config.py            # Configuration handling
│   ├── logger.py            # Logging setup and utilities
│   ├── main.py              # FastAPI application and endpoints
│   ├── models.py            # Pydantic models
│   ├── queue_manager.py     # Queue management logic
│   └── templates/           # HTML templates
│       └── index.html       # Web UI
├── config.json              # Configuration file
├── Dockerfile               # Docker configuration
├── queue_service.log        # Log file
└── requirements.txt         # Python dependencies
```

## Quick Setup

### Using Docker Compose (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd assignment3

# Start the service using Docker Compose
docker-compose up -d

# To check logs
docker-compose logs -f
```

```bash
# If you encounter strange cache issues (e.g., stale builds), try:
docker-compose down
docker-compose build --no-cache
docker-compose up
# Then open http://localhost:7500 in your browser to access the web UI.
````

### Manual Setup

```bash
# Clone the repository
git clone <repository-url>
cd assignment3

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r queue_service/requirements.txt


```

## Testing the Service

### Using the Web UI

The easiest way to test the service is through the web UI, which is available at http://localhost:7500 after starting the service.

1. **Authentication**:
   - Log in with one of the following credentials:
     - Admin: username `admin`, password `admin_password`
     - Agent: username `agent`, password `agent_password`
     - User: username `user`, password `user_password`

2. **Creating Queues** (Admin only):
   - Enter a queue name
   - Select queue type (Transaction or Prediction)
   - Click "Create Queue"

3. **Pushing Messages** (Admin and Agent):
   - Select a queue from the dropdown
   - Select message type (must match the queue type)
   - Enter message content in JSON format (examples are provided)
   - Click "Push Message"

4. **Pulling Messages** (Admin and Agent):
   - Select a queue from the dropdown
   - Click "Pull Message"


### Important Notes

- Queue names must be alphanumeric
- Each queue has a maximum of 5 messages (configured in config.json)
- Message types must match the queue type (transaction, or prediction)
- Transaction messages require fields: transaction_id, customer_id, amount, vendor_id
- Prediction messages require fields: transaction_id, prediction, confidence
- The message queue service uses a maximum number of messages per queue, which is primarily configured through the global max_messages_per_queue setting in the config.json file (currently set to 5 as per requirements). This setting serves as the default for all queues in the system. The application also supports a more flexible model where individual queues can have their own limits specified during creation, allowing for queue-specific configurations if needed. To test this functionality, simply modify the max_messages_per_queue value in the configuration file before starting the service, or for individual queues, include a custom max_messages value when creating a new queue through the API.

## Service API

The service runs on port 7500 and provides the following endpoints:

### Authentication
- `POST /token`: Get an access token with username and password

### Queue Management
- `GET /queues`: List all queues (all authenticated users)
- `POST /queues`: Create a new queue (admin only)
- `DELETE /queues/{queue_name}`: Delete a queue (admin only)
- `GET /queues/{queue_name}`: Get information about a queue (all authenticated users)

### Message Operations
- `POST /queues/{queue_name}/push`: Push a message to a queue (agents and admins)
- `GET /queues/{queue_name}/pull`: Pull a message from a queue (agents and admins)

## Configuration

The service can be configured through the `config.json` file or environment variables:

```json
{
    "max_messages_per_queue": 1000,
    "persist_interval_seconds": 60,
    "storage_path": "./queue_data",
    "port": 7500,
    "host": "localhost",
    "log_level": "INFO",
    "jwt_secret_key": "your-secret-key-change-in-production",
    "jwt_algorithm": "HS256",
    "jwt_expiration_minutes": 30
}
```

## Test Users

For testing purposes, the service includes three predefined users:
- admin: password `admin_password` (admin role)
- agent: password `agent_password` (agent role)
- user: password `user_password` (user role)

## Project Structure

```
.
├── queue_service/           # Message queue service
│   ├── app/
│   │   ├── __init__.py      # Package initialization
│   │   ├── main.py          # API endpoints and service configuration
│   │   ├── auth.py          # Authentication and authorization
│   │   ├── models.py        # Data models
│   │   ├── queue_manager.py # Queue operations and persistence
│   │   ├── logger.py        # Logging configuration
│   │   └── config.py        # Configuration handling
│   ├── Dockerfile           # Container configuration
│   ├── requirements.txt     # Project dependencies
│   └── config.json          # Default configuration
│
├── docker-compose.yml       # Docker Compose configuration
├── README.md                # This file
└── DOCUMENTATION.md         # Detailed documentation
```

Plrsdr see [DOCUMENTATION.md](DOCUMENTATION.md) for more detailed information about the implementation and usage of this service.

