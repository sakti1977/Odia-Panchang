#!/usr/bin/env python3
"""
Test script to verify Twitter/X API credentials are working.
This will attempt to authenticate and retrieve your account info.

Usage:
    python test_twitter_credentials.py

Required environment variables:
    TWITTER_API_KEY
    TWITTER_API_SECRET
    TWITTER_ACCESS_TOKEN
    TWITTER_ACCESS_SECRET
"""

import os
import sys

def test_credentials():
    """Test Twitter API credentials by authenticating and getting user info."""

    # Check if all credentials are set
    required_keys = [
        "TWITTER_API_KEY",
        "TWITTER_API_SECRET",
        "TWITTER_ACCESS_TOKEN",
        "TWITTER_ACCESS_SECRET"
    ]

    missing = [k for k in required_keys if not os.getenv(k)]
    if missing:
        print("❌ Missing credentials:")
        for key in missing:
            print(f"   - {key}")
        print("\nSet these environment variables and try again.")
        return False

    print("✅ All 4 Twitter credentials found in environment")

    # Try importing tweepy
    try:
        import tweepy
        print(f"✅ Tweepy library installed (v{tweepy.__version__})")
    except ImportError:
        print("❌ Tweepy not installed. Run: pip install tweepy")
        return False

    # Create client
    try:
        client = tweepy.Client(
            consumer_key=os.getenv("TWITTER_API_KEY"),
            consumer_secret=os.getenv("TWITTER_API_SECRET"),
            access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
            access_token_secret=os.getenv("TWITTER_ACCESS_SECRET"),
        )
        print("✅ Tweepy client created successfully")
    except Exception as e:
        print(f"❌ Failed to create client: {e}")
        return False

    # Test authentication by getting user info
    try:
        me = client.get_me()
        if me and me.data:
            print(f"✅ Authentication successful!")
            print(f"   Account: @{me.data.username}")
            print(f"   Name: {me.data.name}")
            print(f"   ID: {me.data.id}")
        else:
            print("⚠️  Authentication returned no data")
            return False
    except tweepy.errors.Forbidden as e:
        print(f"❌ Authentication failed with Forbidden error")
        print(f"   Error: {e}")
        print("\n   This usually means:")
        print("   1. Your API access level is 'Free' (cannot post tweets)")
        print("   2. You need 'Basic' ($100/mo) or 'Elevated' (free but approved) access")
        print("   3. Check your access at: https://developer.twitter.com/en/portal/dashboard")
        return False
    except Exception as e:
        print(f"❌ Authentication test failed: {type(e).__name__}: {e}")
        return False

    print("\n🎉 SUCCESS! Your Twitter credentials are valid and working.")
    print("   You can now post tweets from this application.")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("Twitter/X API Credentials Test")
    print("=" * 60)
    print()

    success = test_credentials()

    print()
    print("=" * 60)

    sys.exit(0 if success else 1)
