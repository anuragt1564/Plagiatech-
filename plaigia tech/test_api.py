#!/usr/bin/env python3
"""
Test script for PlagiaTech API endpoints.
This script tests the main functionality of the API without requiring a browser.
"""

import requests
import json
import time
import argparse
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Default API URL
DEFAULT_API_URL = "http://localhost:8000/api"

def test_plagiarism_check(api_url, text, token=None):
    """Test the plagiarism check endpoint."""
    print("\n=== Testing Plagiarism Check ===")
    
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    data = {"text": text}
    
    print(f"Sending request to {api_url}/check-plagiarism")
    start_time = time.time()
    response = requests.post(f"{api_url}/check-plagiarism", headers=headers, json=data)
    elapsed = time.time() - start_time
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Time: {elapsed:.2f} seconds")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Plagiarism Percentage: {result.get('percentage')}%")
        print(f"Sources: {', '.join(result.get('sources', []))}")
        return True
    else:
        print(f"Error: {response.text}")
        return False

def test_text_rephrasing(api_url, text, token=None):
    """Test the text rephrasing endpoint."""
    print("\n=== Testing Text Rephrasing ===")
    
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    data = {"text": text}
    
    print(f"Sending request to {api_url}/rephrase")
    start_time = time.time()
    response = requests.post(f"{api_url}/rephrase", headers=headers, json=data)
    elapsed = time.time() - start_time
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Time: {elapsed:.2f} seconds")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Original: {result.get('original')}")
        print(f"Rephrased: {result.get('rephrased')}")
        return True
    else:
        print(f"Error: {response.text}")
        return False

def test_user_registration(api_url, username, email, password):
    """Test user registration."""
    print("\n=== Testing User Registration ===")
    
    data = {
        "username": username,
        "email": email,
        "password": password
    }
    
    print(f"Sending request to {api_url}/register")
    response = requests.post(f"{api_url}/register", json=data)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 201:
        result = response.json()
        print(f"User registered: {result.get('username')}")
        return True
    else:
        print(f"Error: {response.text}")
        return False

def test_user_login(api_url, username, password):
    """Test user login and token retrieval."""
    print("\n=== Testing User Login ===")
    
    data = {
        "username": username,
        "password": password
    }
    
    print(f"Sending request to {api_url}/token")
    response = requests.post(
        f"{api_url}/token",
        data={"username": username, "password": password}
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        token = result.get("access_token")
        print(f"Token received: {token[:10]}...")
        return token
    else:
        print(f"Error: {response.text}")
        return None

def test_user_info(api_url, token):
    """Test retrieving user information."""
    print("\n=== Testing User Info ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"Sending request to {api_url}/me")
    response = requests.get(f"{api_url}/me", headers=headers)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Username: {result.get('username')}")
        print(f"Email: {result.get('email')}")
        print(f"Premium: {result.get('is_premium')}")
        return True
    else:
        print(f"Error: {response.text}")
        return False

def main():
    """Run the API tests."""
    parser = argparse.ArgumentParser(description="Test PlagiaTech API endpoints")
    parser.add_argument("--url", default=DEFAULT_API_URL, help="API base URL")
    parser.add_argument("--text", default="The quick brown fox jumps over the lazy dog.", 
                        help="Text to use for testing")
    parser.add_argument("--register", action="store_true", help="Test user registration")
    parser.add_argument("--username", default="testuser", help="Username for testing")
    parser.add_argument("--email", default="test@example.com", help="Email for testing")
    parser.add_argument("--password", default="TestPassword1", help="Password for testing")
    
    args = parser.parse_args()
    
    # Test health endpoint
    print("\n=== Testing API Health ===")
    try:
        response = requests.get(f"{args.url.replace('/api', '')}/health")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("API is healthy!")
        else:
            print(f"API health check failed: {response.text}")
            return
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to API: {e}")
        print("Make sure the API server is running.")
        return
    
    token = None
    
    # Test user registration if requested
    if args.register:
        test_user_registration(args.url, args.username, args.email, args.password)
    
    # Test user login
    token = test_user_login(args.url, args.username, args.password)
    
    # Test user info if login successful
    if token:
        test_user_info(args.url, token)
    
    # Test plagiarism check
    test_plagiarism_check(args.url, args.text, token)
    
    # Test text rephrasing
    test_text_rephrasing(args.url, args.text, token)
    
    print("\n=== All Tests Completed ===")

if __name__ == "__main__":
    main()
