# Message Queue Service for HPC Tasks

A high-performance message queue service for computational-intensive tasks, designed as part of a distributed system architecture.

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
- **Configurable**: Max queue size, persistence intervals, and other settings can be configured
- **Role-Based Access Control**: Different access levels for administrators, agents, and regular users
- **Logging**: Comprehensive logging of all operations, requests, and responses
- **Error Handling**: Graceful handling of common error conditions (queue full, empty, etc.)
- **Docker Support**: Easy deployment using Docker and Docker Compose

## System Requirements

- Python 3.8 or higher
- Docker and Docker Compose (for containerized deployment)
- FastAPI and dependencies listed in requirements.txt

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

# Start the service
cd queue_service
python -m app.main
```

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
    "host": "0.0.0.0",
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

See [DOCUMENTATION.md](DOCUMENTATION.md) for more detailed information about the implementation and usage of this service.

## Common Issues

- If you have permission issues with the queue_data directory, make sure the directory has proper read/write permissions
- If authentication fails, check that you're using the correct credentials and token format
- For any configuration issues, verify your config.json file and environment variables
