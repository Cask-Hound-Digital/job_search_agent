"""
One-time Gmail OAuth2 Authentication Flow.
Exchanges Google Cloud client secrets (credentials.json) for a local token.json.
"""

import os
import sys
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(BASE_DIR, "credentials.json")
TOKEN_FILE = os.path.join(BASE_DIR, "token.json")
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def authenticate_gmail(credentials_path: str = CREDENTIALS_FILE, token_path: str = TOKEN_FILE, port: int = 0):
    creds = None
    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        except Exception as e:
            print(f"Error loading existing token: {e}")

    if creds and creds.valid:
        print(f"Valid OAuth token already exists at: {token_path}")
        return creds

    if creds and creds.expired and creds.refresh_token:
        try:
            print("Refreshing expired token...")
            creds.refresh(Request())
            with open(token_path, "w", encoding="utf-8") as token_file:
                token_file.write(creds.to_json())
            print(f"Token successfully refreshed and saved to: {token_path}")
            return creds
        except Exception as e:
            print(f"Token refresh failed: {e}. Starting full auth flow...")

    if not os.path.exists(credentials_path):
        print(f"ERROR: Client credentials file not found at: {credentials_path}")
        print("Please download credentials.json (OAuth 2.0 Client ID for Desktop) from Google Cloud Console.")
        return None

    print("Initiating local OAuth2 web flow...")
    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
    creds = flow.run_local_server(port=port)

    with open(token_path, "w", encoding="utf-8") as token_file:
        token_file.write(creds.to_json())

    print(f"Authentication successful! Token saved to: {token_path}")
    return creds

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Authenticate with Gmail API via OAuth2")
    parser.add_argument("--credentials", default=CREDENTIALS_FILE, help="Path to credentials.json")
    parser.add_argument("--token", default=TOKEN_FILE, help="Path to output token.json")
    parser.add_argument("--port", type=int, default=0, help="Local server port (default 0: random)")
    args = parser.parse_args()

    authenticate_gmail(credentials_path=args.credentials, token_path=args.token, port=args.port)
