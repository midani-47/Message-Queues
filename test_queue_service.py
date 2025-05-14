#!/usr/bin/env python3
"""
Test script for the Message Queue Service

This script demonstrates how to interact with the queue service API
by performing a series of operations including:
- Authentication
- Creating a queue
- Pushing messages
- Pulling messages
- Getting queue information
"""

import requests
import json
import time
from typing import Dict, Any, Optional

# Service URL
BASE_URL = "http://localhost:7500"

# Test users
ADMIN_USER = {"username": "admin", "password": "admin_password"}
AGENT_USER = {"username": "agent", "password": "agent_password"}
USER_USER = {"username": "user", "password": "user_password"}


def get_token(username: str, password: str) -> str:
    """Get an authentication token from the service"""
    response = requests.post(
        f"{BASE_URL}/token",
        params={"username": username, "password": password}
    )
    
    if response.status_code != 200:
        print(f"Error getting token: {response.text}")
        exit(1)
    
    token_data = response.json()
    return token_data["access_token"]


def make_request(
    method: str,
    endpoint: str,
    token: Optional[str] = None,
    json_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Make a request to the service with proper authentication"""
    url = f"{BASE_URL}/{endpoint}"
    headers = {}
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    if method == "GET":
        response = requests.get(url, headers=headers)
    elif method == "POST":
        response = requests.post(url, headers=headers, json=json_data)
    elif method == "DELETE":
        response = requests.delete(url, headers=headers)
    else:
        raise ValueError(f"Unsupported method: {method}")
    
    print(f"{method} {endpoint} -> {response.status_code}")
    
    if response.status_code == 204:  # No content
        return {}
    
    try:
        return response.json()
    except:
        print(f"Response is not JSON: {response.text}")
        return {"detail": response.text}


def test_queue_service():
    """Run a complete test of the queue service"""
    print("\n=== Testing Queue Service ===\n")
    
    # Get tokens for different users
    print("Authenticating users...")
    admin_token = get_token(ADMIN_USER["username"], ADMIN_USER["password"])
    agent_token = get_token(AGENT_USER["username"], AGENT_USER["password"])
    user_token = get_token(USER_USER["username"], USER_USER["password"])
    print("Authentication successful\n")
    
    # List queues (should be empty initially)
    print("Listing queues...")
    queues = make_request("GET", "queues", admin_token)
    print(f"Initial queues: {json.dumps(queues, indent=2)}\n")
    
    # Create a test queue
    print("Creating test queue...")
    queue_data = {
        "name": "test_queue",
        "config": {
            "max_messages": 100,
            "persist_interval_seconds": 10
        }
    }
    create_result = make_request("POST", "queues", admin_token, queue_data)
    print(f"Create result: {json.dumps(create_result, indent=2)}\n")
    
    # Push some test messages
    print("Pushing test messages...")
    for i in range(3):
        message = {
            "customer": f"customer_{i}",
            "vendor_id": f"vendor_{i}",
            "amount": 100.0 + i * 10,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
        }
        
        push_result = make_request(
            "POST",
            f"queues/test_queue/push",
            admin_token,
            message
        )
        print(f"Push result {i}: {json.dumps(push_result, indent=2)}")
    print()
    
    # Get queue info
    print("Getting queue info...")
    queue_info = make_request("GET", "queues/test_queue", user_token)
    print(f"Queue info: {json.dumps(queue_info, indent=2)}\n")
    
    # Pull messages from the queue
    print("Pulling messages...")
    for i in range(3):
        pull_result = make_request("GET", f"queues/test_queue/pull", agent_token)
        print(f"Pull result {i}: {json.dumps(pull_result, indent=2)}")
    print()
    
    # Try to pull from empty queue (should fail gracefully)
    print("Pulling from empty queue...")
    empty_pull = make_request("GET", f"queues/test_queue/pull", agent_token)
    print(f"Empty pull result: {json.dumps(empty_pull, indent=2)}\n")
    
    # Delete the test queue
    print("Deleting test queue...")
    delete_result = make_request("DELETE", f"queues/test_queue", admin_token)
    print(f"Delete result: {json.dumps(delete_result, indent=2)}\n")
    
    # Verify queue is deleted
    print("Verifying queue deletion...")
    final_queues = make_request("GET", "queues", admin_token)
    print(f"Final queues: {json.dumps(final_queues, indent=2)}\n")
    
    print("=== Test Complete ===")


if __name__ == "__main__":
    test_queue_service()
