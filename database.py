import os
import time
import json
import logging
from datetime import datetime, timedelta

COOKIES_FILE = '/tmp/tradingview_cookies.json'
SESSION_TIMEOUT = 24 * 60 * 60  # 24 hours

def store_cookies(cookies_dict):
    """Store all cookies to JSON file"""
    try:
        current_time = time.time()
        
        cookies_data = {
            'cookies': cookies_dict,
            'timestamp': current_time,
            'expires_at': current_time + SESSION_TIMEOUT
        }
        
        with open(COOKIES_FILE, 'w') as f:
            json.dump(cookies_data, f, indent=2)
            
        logging.info("Cookies stored successfully")
        sessionid = cookies_dict.get('sessionid', 'unknown')
        cookie_count = len(cookies_dict)
        print(f"Cookies stored with session: {sessionid[:8]}... ({cookie_count} cookies)")
        
    except Exception as e:
        logging.error(f"Failed to store cookies: {e}")
        raise

def store_session(sessionid):
    """Store session ID to file (legacy compatibility)"""
    # For backwards compatibility, create a minimal cookies dict
    cookies_dict = {'sessionid': sessionid}
    store_cookies(cookies_dict)

def get_cookies():
    """Get all cookies from JSON file"""
    try:
        if not os.path.exists(COOKIES_FILE):
            return None
            
        with open(COOKIES_FILE, 'r') as f:
            cookies_data = json.load(f)
            
        # Check if cookies are expired
        if time.time() > cookies_data.get('expires_at', 0):
            print("Cookies have expired")
            clear_session()
            return None
            
        return cookies_data.get('cookies', {})
        
    except Exception as e:
        logging.error(f"Failed to get cookies: {e}")
        return None

def get_session():
    """Get session ID from cookies (legacy compatibility)"""
    cookies = get_cookies()
    if cookies:
        return cookies.get('sessionid')
    return None

def has_valid_session():
    """Check if we have a valid session"""
    sessionid = get_session()
    return sessionid is not None and len(sessionid) > 0

def refresh_session():
    """Clear expired session and require re-login"""
    try:
        cookies = get_cookies()
        if cookies is None:
            logging.info("No session to refresh - requires new login")
            return False
            
        clear_session()
        logging.info("Session cleared - please login again")
        return True
        
    except Exception as e:
        logging.error(f"Failed to refresh session: {e}")
        return False

def clear_session():
    """Clear stored cookies"""
    try:
        if os.path.exists(COOKIES_FILE):
            os.remove(COOKIES_FILE)
        logging.info("Cookies cleared")
        print("Cookies cleared")
    except Exception as e:
        logging.error(f"Failed to clear cookies: {e}")

def get_session_info():
    """Get session information"""
    try:
        if not has_valid_session():
            return {
                'has_session': False,
                'created_at': None,
                'expires_at': None,
                'session_id': None
            }
            
        with open(COOKIES_FILE, 'r') as f:
            cookies_data = json.load(f)
            
        timestamp = cookies_data.get('timestamp', time.time())
        created_at = datetime.fromtimestamp(timestamp)
        expires_at = datetime.fromtimestamp(cookies_data.get('expires_at', timestamp + SESSION_TIMEOUT))
        
        sessionid = get_session()
        
        return {
            'has_session': True,
            'created_at': created_at.isoformat(),
            'expires_at': expires_at.isoformat(),
            'session_id': sessionid[:8] + '...' if sessionid else None,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Failed to get session info: {e}")
        return {
            'has_session': False,
            'created_at': None,
            'expires_at': None,
            'session_id': None,
            'error': str(e)
        }

# Database compatibility layer removed - using direct functions instead