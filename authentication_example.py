import time
import requests

BASE_URL = "https://dummyjson.com"

# Global token storage
tokens = {
    "access_token": None,
    "refresh_token": None
}

def login():
    """Initial login to retrieve short-lived tokens (1 minute minimum)"""
    print("[*] Performing initial login...")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "username": "emilys",
            "password": "emilyspass",
            "expiresInMins": 1  # 1 minute expiration (DummyJSON's minimum)
        },
        headers={"Content-Type": "application/json"}
    )
    if response.status_code == 200:
        data = response.json()
        tokens["access_token"] = data.get("accessToken")
        tokens["refresh_token"] = data.get("refreshToken")
        print("[+] Login successful!")
        print(f"    Access Token:  {tokens['access_token'][:25]}...")
        print(f"    Refresh Token: {tokens['refresh_token'][:25]}...\n")
    else:
        raise Exception(f"Login failed: {response.text}")

def refresh_tokens():
    """Uses the current refresh token to get a new pair of access + refresh tokens"""
    print("[*] Rotating tokens via /auth/refresh endpoint...")
    response = requests.post(
        f"{BASE_URL}/auth/refresh",
        json={
            "refreshToken": tokens["refresh_token"],
            "expiresInMins": 1
        },
        headers={"Content-Type": "application/json"}
    )
    if response.status_code == 200:
        data = response.json()
        tokens["access_token"] = data.get("accessToken")
        tokens["refresh_token"] = data.get("refreshToken")
        print("[+] Token refresh successful!")
        print(f"    New Access Token:  {tokens['access_token'][:25]}...")
        print(f"    New Refresh Token: {tokens['refresh_token'][:25]}...\n")
    else:
        print(f"[-] Token refresh failed: {response.text}")
        # If the refresh token itself has completely expired, we must re-login
        if response.status_code in [401, 403]:
            print("[!] Refresh token expired. Forcing a fresh login...")
            login()

def make_authenticated_request(url):
    """Wrapper that signs requests and auto-refreshes if the access token expires (401)"""
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    response = requests.get(url, headers=headers)
    
    # Catch access token expiration
    if response.status_code == 401:
        print("[!] Got 401 Unauthorized! Access token has expired.")
        refresh_tokens()  # Renew the access token
        
        # Retry the request with the new access token
        print("[*] Retrying the original request with the new access token...")
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        response = requests.get(url, headers=headers)
        
    return response

# =====================================================================
# EXECUTION FLOW SIMULATION
# =====================================================================

# 1. Start the Session
login()

# 2. Call API immediately (Everything is valid)
print("[*] Making an immediate API call...")
res = make_authenticated_request(f"{BASE_URL}/auth/me")
print(f"    Response Status: {res.status_code} | User: {res.json().get('username')}\n")

# 3. Simulate Refresh Token Expiration (Your 30-sec window constraint)
# We choose to refresh the token manually here to extend the session
print("[*] Waiting 30 seconds to simulate refresh token expiration threshold...")
time.sleep(30)

print("[*] Proactively refreshing the session using the refresh token...")
refresh_tokens()

# 4. Simulate Access Token Expiration (Your 1-min window constraint)
# We wait long enough for the access token issued during step 3 to expire.
print("[*] Waiting 65 seconds to guarantee the access token expires...")
time.sleep(65)

# 5. Call API with Expired Access Token
# The wrapper function will automatically detect the 401, trigger the refresh, and retry.
print("[*] Attempting API call with expired access token...")
res_after_expiry = make_authenticated_request(f"{BASE_URL}/auth/me")
print(f"    Final Response Status: {res_after_expiry.status_code} | Email: {res_after_expiry.json().get('email')}")
print("[+] Process workflow complete.")
