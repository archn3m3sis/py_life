#!/usr/bin/env python3
"""
Test script for auth_utils.py

This script demonstrates the usage of the authentication utilities.
Run this script to test the magic link functionality.
"""

import sys
import os

# Add the current directory to the path so we can import auth_utils
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from auth_utils import (
    generate_token,
    create_magic_link,
    send_magic_link,
    create_and_send_magic_link,
    validate_token,
    consume_token
)

def test_generate_token():
    """Test token generation."""
    print("Testing token generation...")
    token = generate_token()
    print(f"Generated token: {token}")
    assert len(token) > 0
    assert isinstance(token, str)
    print("✓ Token generation test passed\n")

def test_create_magic_link():
    """Test magic link creation."""
    print("Testing magic link creation...")
    email = "test@example.com"
    url = create_magic_link(email)
    print(f"Created magic link for {email}: {url}")
    assert url is not None
    assert "verify?token=" in url
    print("✓ Magic link creation test passed\n")
    return url

def test_send_magic_link():
    """Test sending magic link."""
    print("Testing magic link sending...")
    email = "test@example.com"
    url = "http://localhost:3000/verify?token=test-token"
    success = send_magic_link(email, url)
    print(f"Send result: {success}")
    assert success is True  # Should succeed with console fallback
    print("✓ Magic link sending test passed\n")

def test_create_and_send():
    """Test creating and sending magic link in one step."""
    print("Testing create and send magic link...")
    email = "test2@example.com"
    success = create_and_send_magic_link(email)
    print(f"Create and send result: {success}")
    assert success is True
    print("✓ Create and send test passed\n")

def test_validate_token():
    """Test token validation."""
    print("Testing token validation...")
    
    # Create a magic link first
    email = "test3@example.com"
    url = create_magic_link(email)
    
    # Extract token from URL
    token = url.split("token=")[1]
    
    # Validate the token
    is_valid, user, magic_link = validate_token(token)
    print(f"Token validation result: {is_valid}")
    if is_valid:
        print(f"User: {user.email}")
        print(f"Magic link expires at: {magic_link.expires_at}")
    
    assert is_valid is True
    assert user is not None
    assert user.email == email
    print("✓ Token validation test passed\n")
    
    return token

def test_consume_token():
    """Test token consumption."""
    print("Testing token consumption...")
    
    # Create a magic link first
    email = "test4@example.com"
    url = create_magic_link(email)
    
    # Extract token from URL
    token = url.split("token=")[1]
    
    # Consume the token
    success, user = consume_token(token)
    print(f"Token consumption result: {success}")
    if success:
        print(f"User: {user.email}")
    
    assert success is True
    assert user is not None
    assert user.email == email
    
    # Try to consume again (should fail)
    success2, user2 = consume_token(token)
    print(f"Second consumption result: {success2}")
    assert success2 is False
    assert user2 is None
    
    print("✓ Token consumption test passed\n")

if __name__ == "__main__":
    print("Running auth_utils tests...\n")
    
    try:
        test_generate_token()
        test_create_magic_link()
        test_send_magic_link()
        test_create_and_send()
        test_validate_token()
        test_consume_token()
        
        print("🎉 All tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
