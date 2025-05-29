import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
import time
import traceback

# Import our modules
import captureutil
import tradingview
import database

api_bp = Blueprint('api', __name__)

# Rate limiting storage (simple in-memory for demo)
request_counts = {}
RATE_LIMIT = 10  # requests per minute

def check_rate_limit(client_ip):
    """Simple rate limiting check"""
    current_time = time.time()
    minute_ago = current_time - 60
    
    # Clean old entries
    for ip in list(request_counts.keys()):
        request_counts[ip] = [req_time for req_time in request_counts[ip] if req_time > minute_ago]
        if not request_counts[ip]:
            del request_counts[ip]
    
    # Check current IP
    if client_ip not in request_counts:
        request_counts[client_ip] = []
    
    if len(request_counts[client_ip]) >= RATE_LIMIT:
        return False
    
    request_counts[client_ip].append(current_time)
    return True

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'TradingView Chart Capture API'
    })

@api_bp.route('/login', methods=['POST'])
def login():
    """Login to TradingView and store session"""
    try:
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        if not check_rate_limit(client_ip):
            return jsonify({'error': 'Rate limit exceeded. Try again later.'}), 429

        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON payload required'}), 400

        # Check if sessionid is provided directly
        if 'sessionid' in data:
            sessionid = data['sessionid']
            tradingview.store_session_directly(sessionid)
            return jsonify({
                'status': 'success',
                'message': 'Session ID validated and stored successfully',
                'session_id': sessionid[:8] + '...'  # Show partial for confirmation
            })

        # Check if username/password provided
        if 'username' in data and 'password' in data:
            username = data['username']
            password = data['password']
            
            # Attempt login with credentials
            sessionid = tradingview.login_with_credentials(username, password)
            
            return jsonify({
                'status': 'success',
                'message': 'Login successful, session stored',
                'session_id': sessionid[:8] + '...'  # Show partial for confirmation
            })

        return jsonify({'error': 'Either sessionid or username/password required'}), 400

    except Exception as e:
        logging.error(f"Login error: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': f'Login failed: {str(e)}'}), 500


@api_bp.route('/capture', methods=['POST'])
def capture_chart():
    """Capture a TradingView chart using chart ID"""
    try:
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        if not check_rate_limit(client_ip):
            return jsonify({'error': 'Rate limit exceeded. Try again later.'}), 429

        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON payload required'}), 400

        # Required parameters
        chart_id = data.get('chart_id')
        if not chart_id:
            return jsonify({'error': 'chart_id parameter is required (e.g., SPczhWCm)'}), 400

        # Optional parameters
        adjustment = data.get('adjustment', 30)
        ticker = data.get('ticker', 'NONE')
        interval = data.get('interval', '60')  # Default 1 hour
        theme = data.get('theme', 'dark')  # Default dark theme

        # Validate parameters
        if not isinstance(adjustment, int) or adjustment < 0:
            return jsonify({'error': 'adjustment must be a positive integer'}), 400

        if theme not in ['dark', 'light']:
            return jsonify({'error': 'theme must be either "dark" or "light"'}), 400

        # Check if we have a valid session
        if not database.has_valid_session():
            return jsonify({'error': 'No valid session found. Please login first.'}), 401

        logging.info(f"Capturing chart ID: {chart_id}, ticker: {ticker}, adjustment: {adjustment}, interval: {interval}, theme: {theme}")

        # Use chart ID capture method
        screenshot_path = captureutil.screenshot_test_chart(chart_id, ticker, adjustment, interval, theme)
        
        result = {
            'status': 'success',
            'chart_id': chart_id,
            'ticker': ticker,
            'adjustment': adjustment,
            'interval': interval,
            'theme': theme,
            'screenshot_path': screenshot_path,
            'timestamp': datetime.now().isoformat()
        }

        return jsonify(result)

    except Exception as e:
        logging.error(f"Chart capture error: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': f'Capture failed: {str(e)}'}), 500



@api_bp.route('/session-status', methods=['GET'])
def session_status():
    """Check current session status"""
    try:
        has_session = database.has_valid_session()
        session_id = database.get_session() if has_session else None
        
        return jsonify({
            'has_valid_session': has_session,
            'session_id': session_id[:8] + '...' if session_id else None,  # Partial for security
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logging.error(f"Session status error: {str(e)}")
        return jsonify({'error': f'Failed to check session status: {str(e)}'}), 500

@api_bp.route('/refresh-session', methods=['POST'])
def refresh_session():
    """Clear current session and perform fresh login with full cookie capture"""
    try:
        # Clear existing session first
        database.clear_session()
        logging.info("Previous session cleared")
        
        # Perform fresh login just like autologin
        try:
            username = "taotaufx"
            password = "jigno9-hurfyx-xibmYb"
            
            sessionid = tradingview.login_with_credentials(username, password)
            logging.info(f"Refresh login successful, new session: {sessionid[:8]}...")
            
            # Get cookie count for display
            cookies = database.get_cookies()
            cookie_count = len(cookies) if cookies else 0
            
            return jsonify({
                'status': 'success',
                'message': f'Session refreshed successfully with fresh cookies ({cookie_count} cookies)',
                'session_id': sessionid[:8] + '...',
                'cookie_count': cookie_count,
                'refreshed': True
            })
            
        except Exception as login_error:
            logging.error(f"Refresh login failed: {login_error}")
            return jsonify({
                'status': 'error',
                'message': f'Failed to refresh session: {str(login_error)}',
                'requires_manual_login': True
            }), 500
            
    except Exception as e:
        logging.error(f"Failed to refresh session: {str(e)}")
        return jsonify({'error': f'Failed to refresh session: {str(e)}'}), 500






