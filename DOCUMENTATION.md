# Message Queue Service Documentation

This document provides detailed information about the implementation, architecture, and usage of the Message Queue Service.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Component Descriptions](#component-descriptions)
3. [Data Models](#data-models)
4. [API Endpoints](#api-endpoints)
5. [Authentication and Authorization](#authentication-and-authorization)
6. [Persistence Mechanism](#persistence-mechanism)
7. [Logging System](#logging-system)
8. [Configuration Options](#configuration-options)
9. [Error Handling](#error-handling)
10. [Testing](#testing)

## Architecture Overview

The Message Queue Service is designed as a standalone microservice that provides queue functionality for high-performance computing tasks. It follows RESTful API design principles and uses FastAPI as the web framework.

Key architectural features:
- **Stateful Service**: Maintains queue state in memory with persistence to disk
- **Role-Based Access Control**: Different permission levels for different user roles
- **Thread-Safe Queues**: Locks for thread safety in queue operations
- **Asynchronous API**: FastAPI's async support for handling concurrent requests
- **Configurable**: Configuration via file and environment variables
- **Persistence**: Automatic and configurable persistence to disk

## Component Descriptions

### Main Components

- **FastAPI Application (`main.py`)**: Defines API endpoints and handles requests
- **Queue Manager (`queue_manager.py`)**: Core component that handles queue operations and persistence
- **Authentication (`auth.py`)**: JWT-based authentication and authorization
- **Data Models (`models.py`)**: Pydantic models for data validation
- **Configuration (`config.py`)**: Configuration management
- **Logging (`logger.py`)**: Comprehensive request/response logging

### Queue Manager

The Queue Manager is the core component responsible for:
1. Creating and deleting queues
2. Managing message push and pull operations
3. Periodically persisting queue state to disk
4. Restoring queues from persistent storage on startup
5. Enforcing queue limits and access control

## Data Models

The service uses Pydantic models for data validation and serialization. Key models include:

### Message Types

The service supports two types of messages as required by the assignment:

1. **Transaction Messages**: Contains transaction data with fields from Assignment 2:
   ```json
   {
     "transaction_id": "string",
     "customer_id": "string",
     "customer_name": "string",
     "amount": "float",
     "vendor_id": "string",
     "date": "string",
     ... other transaction fields
   }
   ```

2. **Prediction Result Messages**: Contains prediction results with fields from Assignment 2:
   ```json
   {
     "transaction_id": "string",
     "prediction": "boolean",  // True for approved, False for rejected
     "confidence": "float",   // Confidence score of the prediction
     "model_version": "string",
     "timestamp": "string",
     ... other prediction fields
   }
   ```

The `MessageBase` model includes a `message_type` field that identifies whether a message contains transaction data or prediction results.

### Key Models

- **Message**: Represents a message in a queue with content and metadata
  ```python
  class Message(MessageBase):
      id: str  # Unique message ID
      content: Dict[str, Any]  # Message content
      timestamp: datetime
  ```

- **QueueInfo**: Information about a queue
  ```python
  class QueueInfo:
      name: str
      message_count: int
      created_at: datetime
      last_modified: datetime
  ```

- **QueueConfig**: Configuration for a queue
  ```python
  class QueueConfig:
      max_messages: int = 1000
      persist_interval_seconds: int = 60
  ```

- **TokenData**: Authentication token data
  ```python
  class TokenData:
      username: str
      role: QueueRole
  ```

## API Endpoints

### Authentication
- `POST /token`: Get an access token
  - Parameters: `username` (string), `password` (string)
  - Returns: `{"access_token": "token", "token_type": "bearer"}`

### Queue Management
- `GET /queues`: List all queues
  - Authentication: Any authenticated user
  - Returns: `{"queues": [QueueInfo]}`

- `POST /queues`: Create a new queue
  - Authentication: Admin only
  - Request Body: `{"name": "queue_name", "config": {"max_messages": 1000, "persist_interval_seconds": 60}}`
  - Returns: `QueueInfo`

- `DELETE /queues/{queue_name}`: Delete a queue
  - Authentication: Admin only
  - Returns: `{"message": "Queue 'queue_name' deleted successfully"}`

- `GET /queues/{queue_name}`: Get information about a queue
  - Authentication: Any authenticated user
  - Returns: `QueueInfo`

### Message Operations
- `POST /queues/{queue_name}/push`: Push a message to a queue
  - Authentication: Agent or Admin
  - Request Body: Any JSON object (will be stored as message content)
  - Returns: `{"message": "Message pushed to queue 'queue_name'", "message_id": "uuid"}`

- `GET /queues/{queue_name}/pull`: Pull a message from a queue
  - Authentication: Agent or Admin
  - Returns: `{"message_id": "uuid", "content": {...}, "timestamp": "iso-datetime"}`

## Authentication and Authorization

The service uses JWT (JSON Web Tokens) for authentication and role-based authorization.

### Roles

- **Admin**: Can create and delete queues, push and pull messages
- **Agent**: Can push and pull messages
- **User**: Can view queue information only

### Token Generation

Tokens are generated with the `/token` endpoint using a username and password. In the current implementation, there are three predefined users:

- admin: password `admin_password` (admin role)
- agent: password `agent_password` (agent role)
- user: password `user_password` (user role)

In a production environment, these credentials should be stored securely in a database.

## Persistence Mechanism

The service persists queue state to disk to ensure data is not lost when the service restarts.

### Persistence Implementation

1. **Queue Data Storage**: Each queue is stored as a separate JSON file in the storage directory
2. **Metadata Storage**: Queue metadata is stored in a separate `metadata.json` file
3. **Automatic Persistence**: Queues are automatically persisted at configurable intervals
4. **Persistence on Shutdown**: Queues are persisted when the service shuts down gracefully
5. **Restoration on Startup**: Queues are restored from persistent storage when the service starts

### Persistence Configuration

The persistence behavior can be configured with:
- `persist_interval_seconds`: How often to persist queues (default: 60 seconds)
- `storage_path`: Where to store the queue data (default: "./queue_data")

## Logging System

The service implements a comprehensive logging system that records all operations to `queue_service.log` in the root directory. The logging system is designed to match the requirements from Assignment 2.

### Log Format

Logs are stored in structured JSON format for easy parsing and analysis. There are two main types of log entries:

#### 1. Message Operation Logs

When messages are pushed to or pulled from queues, the following information is logged:

```json
{
  "timestamp": "ISO-8601 timestamp",
  "queue": "name of the queue",
  "action": "push or pull",
  "message_id": "unique message ID",
  "message_type": "transaction or prediction",
  "content": "full message content"
}
```

This format ensures that all message operations are traceable and can be audited if needed.

#### 2. HTTP Request/Response Logs

For HTTP requests and responses, the following information is logged:

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
### Log Implementation

The logging system is implemented in `logger.py` with the following components:

1. **CustomFormatter**: A custom log formatter that outputs logs in structured JSON format
2. **setup_logger**: Function to configure the logger with console and file handlers
3. **log_request_response**: Function to log HTTP requests and responses
4. **log_message**: Function to log message operations (push/pull)

The log level can be configured in `config.json` and defaults to INFO.

The service uses a comprehensive logging system that logs all requests and responses.

### Log Format

Logs are output in a structured JSON format with the following information:
- **Timestamp**: When the log was created
- **Level**: Log level (INFO, WARNING, ERROR, etc.)
- **Message**: Log message
- **Source**: Where the request came from
- **Destination**: Where the request is going to
- **Headers**: HTTP headers (if applicable)
- **Metadata**: Additional metadata
- **Body**: Request or response body

### Request/Response Logging

Every request and response is logged with:
- Source and destination
- Headers
- Request/response body
- Processing time
- Status code

## Configuration Options

The service can be configured through a JSON configuration file or environment variables.

### Configuration Options

- `max_messages_per_queue`: Maximum number of messages per queue (fixed at 5 as per assignment requirements). This value can only be changed in the config file and cannot be modified through the UI
- `persist_interval_seconds`: How often to persist queues (default: 60 seconds)
- `storage_path`: Where to store the queue data (default: "./queue_data")
- `port`: Port to run the service on (default: 7500)
- `host`: Host to bind to (default: "0.0.0.0")
- `log_level`: Logging level (default: "INFO")
- `jwt_secret_key`: Secret key for JWT token generation
- `jwt_algorithm`: Algorithm for JWT token generation (default: "HS256")
- `jwt_expiration_minutes`: Token expiration time in minutes (default: 30)

## Error Handling

The service includes comprehensive error handling for various conditions.

### Common Error Conditions

- **Queue Not Found**: When trying to access a non-existent queue
- **Queue Full**: When trying to push to a queue that has reached its maximum capacity
- **Queue Empty**: When trying to pull from an empty queue
- **Insufficient Privileges**: When a user tries to perform an action they don't have permission for
- **Invalid Token**: When authentication fails
- **Token Expired**: When a token has expired

### Error Responses

Error responses are standardized as:
```json
{
    "detail": "Error message"
}
```

## Testing

To test the service functionality, you can use the included test script or manual HTTP requests.

### Using curl for Testing

Here are some example curl commands to test the service:

#### Get a token
```bash
curl -X POST "http://localhost:7500/token?username=admin&password=admin_password"
```

#### Create a queue
```bash
curl -X POST "http://localhost:7500/queues" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "test_queue", "config": {"max_messages": 100, "persist_interval_seconds": 30}}'
```

#### Push a message
```bash
curl -X POST "http://localhost:7500/queues/test_queue/push" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"customer": "test_customer", "vendor_id": "vendor123", "amount": 100.50}'
```

#### Pull a message
```bash
curl -X GET "http://localhost:7500/queues/test_queue/pull" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Docker Deployment

The service can be easily deployed using Docker and Docker Compose.

### Build and Run with Docker Compose
```bash
docker-compose up -d
```

### Build and Run Manually with Docker
```bash
cd queue_service
docker build -t queue-service .
docker run -p 7500:7500 -v ./queue_data:/app/queue_data queue-service
```

### Build and Run Manually
```bash
cd queue_service
python -m app.main
```
