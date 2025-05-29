import config
import requests
import platform
import logging
from urllib3 import encode_multipart_formdata
import database


def login():
    """Check existing session validity"""
    print('Getting sessionid from database')
    sessionid = database.get_session()

    if sessionid:
        headers = {'cookie': 'sessionid=' + sessionid}
        test = requests.request("GET", config.urls["tvcoins"], headers=headers)
        print(f"Session test status: {test.status_code}")
        
        if test.status_code == 200:
            print("Existing session is valid")
            return
    
    raise Exception("No valid session found. Please login first using the API endpoints.")


def login_with_credentials(username, password):
    """Login to TradingView with username and password"""
    if not username or not password:
        raise Exception("Username and password are required")
    
    payload = {
        'username': username,
        'password': password,
        'remember': 'on'
    }
    
    try:
        body, contentType = encode_multipart_formdata(payload)
        userAgent = 'TWAPI/3.0 (' + platform.system() + '; ' + platform.version() + '; ' + platform.release() + ')'
        print(f"User Agent: {userAgent}")
        
        login_headers = {
            'origin': 'https://www.tradingview.com',
            'User-Agent': userAgent,
            'Content-Type': contentType,
            'referer': 'https://www.tradingview.com'
        }
        
        login_response = requests.post(config.urls["signin"],
                                     data=body,
                                     headers=login_headers)
        
        print(f"Login response status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            cookies = login_response.cookies.get_dict()
            if 'sessionid' in cookies:
                sessionid = cookies["sessionid"]
                # Store all cookies instead of just sessionid
                database.store_cookies(cookies)
                print("Login successful, all cookies stored")
                return sessionid
            else:
                raise Exception("No sessionid in login response cookies")
        else:
            raise Exception(f"Login failed with status code: {login_response.status_code}")
            
    except Exception as e:
        logging.error(f"Login error: {e}")
        raise Exception(f"Failed to login with username/password: {e}")


def store_session_directly(sessionid):
    """Store a session ID directly"""
    if not sessionid:
        raise Exception("Session ID is required")
    
    # Validate the session ID first
    if not check_session_valid(sessionid):
        raise Exception("Invalid session ID provided")
    
    database.store_session(sessionid)
    print("Session ID stored successfully")
    return sessionid


def check_session_valid(sessionid):
    """Check if a session ID is valid"""
    if not sessionid:
        return False
        
    headers = {'cookie': 'sessionid=' + sessionid}
    try:
        test = requests.request("GET", config.urls["tvcoins"], headers=headers, timeout=10)
        return test.status_code == 200
    except Exception as e:
        logging.error(f"Session validation error: {e}")
        return False


def get_user_info(sessionid):
    """Get user information using session ID"""
    if not sessionid:
        return None
        
    headers = {'cookie': 'sessionid=' + sessionid}
    try:
        response = requests.request("GET", config.urls["tvcoins"], headers=headers, timeout=10)
        if response.status_code == 200:
            # Parse user info from response if needed
            return {"status": "authenticated", "session_valid": True}
        return None
    except Exception as e:
        logging.error(f"Get user info error: {e}")
        return None
