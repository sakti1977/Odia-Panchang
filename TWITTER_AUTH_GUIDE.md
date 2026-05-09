# Twitter/X API Authentication Guide

## Problem: 401 Unauthorized Error

If you're seeing a `401 Unauthorized` error when testing Twitter credentials, this guide will help you resolve it.

## Common Causes

The **401 Unauthorized** error typically occurs due to one of these reasons:

1. **Incorrect or mismatched credentials** - The API Key, API Secret, Access Token, or Access Token Secret are incorrect or don't belong to the same Twitter app
2. **Regenerated API keys** - If you regenerated your API keys in the Twitter Developer Portal, you must also regenerate the access tokens
3. **OAuth 1.0a not enabled** - The Twitter app must have OAuth 1.0a authentication enabled
4. **Credentials from different apps** - All 4 credentials must be from the SAME Twitter application

## Solutions

### 1. Verify All Credentials Are From The Same App

Go to the [Twitter Developer Portal](https://developer.twitter.com/en/portal/projects-and-apps):

1. Select your project and app
2. Go to "Keys and tokens"
3. Verify that:
   - API Key and API Secret are visible (or regenerate them)
   - Access Token and Secret are from the same app
   - All credentials are copied correctly to your `.env` file

### 2. Regenerate Access Token and Secret

**IMPORTANT**: If you regenerated your API Key/Secret at any point, you MUST regenerate the Access Token/Secret:

1. Go to your app in the Developer Portal
2. Navigate to "Keys and tokens"
3. Under "Authentication Tokens", click "Regenerate" for Access Token and Secret
4. Copy the new values immediately (they won't be shown again)
5. Update your `.env` file with the new values

### 3. Enable OAuth 1.0a in App Settings

1. Go to your app's Settings in the Developer Portal
2. Scroll to "User authentication settings"
3. Click "Set up" or "Edit" if already configured
4. Ensure OAuth 1.0a is enabled
5. Set permissions to "Read and write" (required for posting tweets)
6. Save changes

### 4. Verify Environment Variables

Make sure your `.env` file has all 4 credentials from the same app:

```bash
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_SECRET=your_access_secret_here
```

### 5. Optional: Add Bearer Token (Recommended)

While not required for posting tweets, adding the Bearer Token can improve authentication reliability:

1. In the Developer Portal, go to "Keys and tokens"
2. Find "Bearer Token" and copy it
3. Add to your `.env`:

```bash
TWITTER_BEARER_TOKEN=your_bearer_token_here
```

The application will automatically use it if available.

## Testing Your Credentials

Run the test script to verify your credentials:

```bash
python test_twitter_credentials.py
```

Expected output if successful:
```
============================================================
Twitter/X API Credentials Test
============================================================

✅ All 4 Twitter credentials found in environment
✅ Tweepy library installed (v4.16.0)
🔑 Using OAuth 1.0a User Context authentication
✅ Tweepy client created successfully
✅ Authentication successful!
   Account: @your_username
   Name: Your Name
   ID: 123456789

🎉 SUCCESS! Your Twitter credentials are valid and working.
   You can now post tweets from this application.

============================================================
```

## API Access Levels

Note that Twitter API has different access levels:

- **Free tier**: Cannot post tweets (read-only)
- **Basic** ($100/month): Can post tweets, limited endpoints
- **Elevated** (Free, requires approval): Can post tweets, more endpoints
- **Enterprise**: Full access

If you see a **403 Forbidden** error instead of 401, it means your access level doesn't support posting tweets.

## Additional Resources

- [Twitter API Documentation](https://developer.twitter.com/en/docs/twitter-api)
- [Tweepy Documentation](https://docs.tweepy.org/)
- [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)

## Still Having Issues?

If you've tried all the above and still see 401 errors:

1. Create a completely new Twitter app in the Developer Portal
2. Generate fresh credentials
3. Update your `.env` file with the new credentials
4. Test again

This often resolves persistent authentication issues.
