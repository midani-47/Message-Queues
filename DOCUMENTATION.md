# Technical Documentation: Message Queue Service for Distributed Systems

## Authors
- Nevin Joseph
- Abed Midani

## Table of Contents
1. [Introduction](#introduction)
2. [System Architecture](#system-architecture)
3. [Queue Service Design](#queue-service-design)
4. [Message Types and Processing](#message-types-and-processing)
5. [Authentication and Authorization](#authentication-and-authorization)
6. [Persistence Mechanism](#persistence-mechanism)
7. [Logging System](#logging-system)
8. [API Endpoints](#api-endpoints)
9. [Web UI Implementation](#web-ui-implementation)
10. [Deployment and Configuration](#deployment-and-configuration)
11. [Limitations and Future Improvements](#limitations-and-future-improvements)

## Introduction

This document provides technical details about a message queue service designed to facilitate communication between distributed system components. The service is built to handle both transaction data and prediction results, providing a reliable way to decouple components in a distributed architecture.

The message queue service was developed as part of Assignment_3, based on the transaction and authentication services from Assignment_2. It serves as a middleware component that enables asynchronous communication between services.

## System Architecture

The message queue service follows a microservices architecture pattern, designed to operate as a service that can be integrated with other components of a distributed system. 

### Technology Stack

The system is built using the following technologies:

- **Docker**: Inspired by the lectures, and even before you mentioned the bonus in the following assingment, we chose this for the experience. The application is containerized using Docker, making it interesting to deploy. Docker Compose is used to utilize the service deployment.

- **FastAPI**: We ended up choosing this one for its high performance, automatic API documentation, and built-in validation. FastAPI's asynchronous capabilities seem to make it compatible with a message queue service.

- **Pydantic**: We chose this one for data validation, serialization, and documentation. Pydantic models ensure that all messages conform to the expected structure, and reduce errors.

- **JWT Authentication**: Implemented for secure access control, allowing different roles (admin, agent, user) to have appropriate permissions when interacting with the queue service.

- **File-based Persistence**: Queue data is persisted to disk using a simple file-based storage mechanism, ensuring that messages are not lost in case of service restarts.

### Architecture Decisions

Several key architectural decisions we made during the development of this application:

1. **Web UI**: A browser-based UI is provided for easy management and monitoring of queues, making the service accessible to both technical and non-technical users.

2. **Separate Queue Types**: The service supports two distinct queue types - transaction queues and prediction queues. This separation ensures that messages are properly routed and processed according to their type. Note, they are separate.

3. **Role-Based Access Control**: Different user roles (admin, agent, user) have different permissions, so that only authorized users can perform certain tasks like creating queues, deleting queues, pushing messages, or pulling messages. Admin does it all, whereas agent can push and pull but not delete. Users do not have such permissions.

4. **In-Memory Processing with Persistence**: Queues are maintained in memory with periodic persistence (in queue_data directory). 



## Queue Service Design

The Queue Service is designed as a specialized middleware component that implements asynchronous communication between distributed system components.

### Core Components

The application is structured around several key components, each with specific responsibilities:

#### Queue Manager

The Queue Manager (`queue_manager.py`) is the central component responsible for all queue operations. It implements:

- **Queue Creation and Deletion**: Creating and removing queues with appropriate type designation (transaction or prediction)
- **Message Operations**: Pushing messages to and pulling messages from queues
- **Concurrency Control**: Using asyncio locks to ensure thread-safe operations
- **Persistence**: Periodically saving queue state to disk and restoring on startup
- **Queue Type Enforcement**: Ensuring messages match the queue type they're being pushed to

The Queue Manager maintains queues as in-memory data structures (Python's `deque`) for high performance, while also providing durability through periodic persistence.

#### API Layer

The API layer (`main.py`) exposes the Queue Manager's functionality through a RESTful HTTP interface. It handles:

- **Request Routing**: Directing requests to appropriate handlers
- **Authentication**: Verifying user identity and permissions
- **Input Validation**: Ensuring requests contain valid data
- **Response Formatting**: Providing consistent JSON responses
- **Error Handling**: Returning appropriate HTTP status codes and error messages

The API is built using FastAPI, which provides automatic validation, documentation, and efficient request handling.

#### Authentication System

The authentication system (`auth.py`) provides secure access control through:

- **JWT Tokens**: Generating and validating JSON Web Tokens
- **Role-Based Access**: Enforcing different permissions for admin, agent, and user roles
- **Token Expiration**: Ensuring security through limited token lifetimes

#### Data Models

The data models (`models.py`) define the structure of:

- **Messages**: Including both transaction and prediction types
- **Queues**: With configuration options like maximum size and type
- **Authentication**: User tokens and roles

These models use Pydantic for validation and serialization, ensuring data integrity throughout the system.

#### Web UI

The web UI (`templates/index.html`) provides a user-friendly interface for:

- **Authentication**: Logging in with different roles
- **Queue Management**: Creating, viewing, and deleting queues
- **Message Operations**: Pushing and pulling messages with appropriate type validation

The UI adapts based on the user's role, showing only the operations they're authorized to perform.

## Message Types and Processing

A key feature of the queue service is its support for different message types, specifically designed to handle both transaction data and prediction results from Assignment 2. This design allows for specialized processing and validation based on message content.

### Message Type Definitions

The service supports two distinct message types:

#### 1. Transaction Messages

Transaction messages contain financial transaction data with the following structure:

```json
{
  "transaction_id": "unique identifier for the transaction",
  "customer_id": "identifier for the customer",
  "customer_name": "name of the customer",
  "amount": "transaction amount as a float",
  "vendor_id": "identifier for the vendor",
  "date": "transaction date",
  "additional_fields": "any other transaction-specific data"
}
```

These messages are typically pushed to transaction queues by systems that capture or generate transaction data.

#### 2. Prediction Messages

Prediction messages contain fraud detection results with the following structure:

```json
{
  "transaction_id": "reference to the original transaction",
  "prediction": "boolean indicating fraud detection result",
  "confidence": "confidence score as a float between 0 and 1",
  "model_version": "version of the prediction model used",
  "timestamp": "when the prediction was made",
  "additional_fields": "any other prediction-specific data"
}
```

These messages are typically pushed to prediction queues by fraud detection systems after analyzing transactions.

### Queue Types and Message Routing

To ensure proper message handling, the service implements queue typing:

- **Transaction Queues**: Accept only transaction messages
- **Prediction Queues**: Accept only prediction messages


When creating a queue, administrators must specify the queue type. The system then enforces this type restriction when messages are pushed to the queue.


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

The queue service implements a robust security model to ensure that only authorized users can access specific functionalities. This model is built around JWT-based authentication and role-based access control.

### Authentication Implementation

The authentication system is implemented in `auth.py` and uses JWT to securely identify users. The implementation includes the `/token` endpoint accepts username and password credentials and returns a JWT token if authentication succeeds. This token contains the user's identity and role, signed with a secret key to prevent tampering. All protected endpoints use the `get_current_user` dependency to validate tokens and extract user information. This function verifies the token signature, checks expiration, and extracts the user's role. The system extracts the user's role from the token and uses it to enforce access control rules.

### Role-Based Access Control

The service defines three distinct roles, each with specific permissions:

1. **Admin Role**:
   - Can create and delete queues, can push messages to any queue, can pull messages from any queue, and has full access to all system functionality

2. **Agent Role**:
   - Cannot create or delete queues, can push messages to any queue (both transaction and prediction types), and can pull messages from any queue. Designed for services that need to interact with queues but shouldn't manage them

3. **User Role**:
   - Can view queue information, cannot push or pull messages, cannot create or delete queues, and is designed for monitoring and read-only access.

### Security Considerations

The authentication system includes several security features:

- **Token Expiration**: Tokens have a configurable expiration time (default: 30 minutes)
- **Secure Password Handling**: For demo purposes, passwords are hardcoded, but in a production environment, they would be securely hashed and stored
- **HTTPS Support**: The service can be configured to use HTTPS for secure communication

These measures help protect the system from common security threats while maintaining usability.

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


## Error Handling

The queue service implements a comprehensive error handling system to ensure that errors are properly caught, reported, and responded to.
The error handling system is designed with several principles in mind:
Error responses follow a consistent format, making them easy to handle on the client side. Error messages are specific and descriptive, helping clients understand what went wrong and how to fix it. HTTP status codes are used correctly to indicate the nature of the error. When errors occur, the service attempts to continue operating as much as possible.

### Common Error Conditions

The service handles several common error conditions:

#### Queue Management Errors
When trying to access a non-existent queue (404 Not Found), when trying to create a queue with a name that already exists (409 Conflict). When trying to create a queue with an invalid name (400 Bad Request), when trying to push a message type that doesn't match the queue type (400 Bad Request)

#### Message Operation Errors
When trying to push to a queue that has reached its maximum capacity (409 Conflict), and when trying to pull from an empty queue (404 Not Found). When trying to push a message with invalid or missing fields (400 Bad Request)

#### Authentication Errors
When trying to authenticate with incorrect username or password (401 Unauthorized), when using an invalid or malformed JWT token (401 Unauthorized), when using an expired JWT token (401 Unauthorized), when trying to perform an action without the required role (403 Forbidden)



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
  -d '{"name": "testQueue", "config": {"max_messages": 100, "persist_interval_seconds": 30, "queue_type": "transaction"}}'
```

#### Push a message
```bash
curl -X POST "http://localhost:7500/queues/testQueue/push" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"customer": "testCustomer", "vendor_id": "vendor123", "amount": 100.50, "transaction_id": "123456", "date": "2025-05-19", "customer_id": "123456"}'
```

#### Pull a message
```bash
curl -X GET "http://localhost:7500/queues/testQueue/pull" \
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

