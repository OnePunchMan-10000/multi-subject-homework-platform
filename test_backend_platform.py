#!/usr/bin/env python3
"""
Smoke test for Edullm backend API
Tests: register → login → get user info
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "http://127.0.0.1:8000"
TEST_USERNAME = f"testuser_{int(datetime.now().timestamp())}"
TEST_PASSWORD = "testpass123"

def test_health():
    """Test if backend is running"""
    print("1. Testing backend health...")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            print("   ✓ Backend is running")
            return True
        else:
            print(f"   ✗ Backend returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ✗ Backend not reachable: {e}")
        return False

def test_register():
    """Test user registration"""
    print(f"2. Testing registration for user '{TEST_USERNAME}'...")
    try:
        payload = {
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        }
        response = requests.post(
            f"{BACKEND_URL}/auth/register",
            json=payload,
            timeout=5
        )
        
        if response.status_code == 201:
            data = response.json()
            print(f"   ✓ Registration successful: {data}")
            return True
        else:
            print(f"   ✗ Registration failed: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ✗ Registration request failed: {e}")
        return False

def test_login():
    """Test user login and return access token"""
    print(f"3. Testing login for user '{TEST_USERNAME}'...")
    try:
        # Send JSON data to Flask backend
        json_data = {
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        }
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json=json_data,  # json data for Flask
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            access_token = data.get("access_token")
            token_type = data.get("token_type")
            print(f"   ✓ Login successful")
            print(f"   Token type: {token_type}")
            print(f"   Access token (first 20 chars): {access_token[:20]}...")
            return access_token
        else:
            print(f"   ✗ Login failed: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"   ✗ Login request failed: {e}")
        return None

def test_get_me(access_token):
    """Test getting user info with JWT token"""
    print("4. Testing /auth/me endpoint...")
    try:
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        response = requests.get(
            f"{BACKEND_URL}/auth/me",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ User info retrieved: {data}")
            return True
        else:
            print(f"   ✗ Get user info failed: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ✗ Get user info request failed: {e}")
        return False

def main():
    print("=== Edullm Backend Smoke Test ===")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test user: {TEST_USERNAME}")
    print()
    
    # Step 1: Health check
    if not test_health():
        print("\n❌ Backend is not running. Please start it with:")
        print("   python -m uvicorn backend.main:app --reload --port 8000")
        sys.exit(1)
    
    # Step 2: Register
    if not test_register():
        print("\n❌ Registration failed. Check backend logs.")
        sys.exit(1)
    
    # Step 3: Login
    access_token = test_login()
    if not access_token:
        print("\n❌ Login failed. Check backend logs.")
        sys.exit(1)
    
    # Step 4: Get user info
    if not test_get_me(access_token):
        print("\n❌ Get user info failed. Check backend logs.")
        sys.exit(1)
    
    print("\n🎉 All tests passed! Backend is working correctly.")
    print("\nYou can now:")
    print("1. Run your Streamlit app: streamlit run hw01.py")
    print("2. Register/login through the UI")
    print("3. The frontend will communicate with this backend")

if __name__ == "__main__":
    main()
