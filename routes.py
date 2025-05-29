from flask import render_template, jsonify
from app import app
import database
import tradingview
import logging
from datetime import datetime

@app.route('/')
def index():
    """Main dashboard page"""
    session_info = database.get_session_info()
    
    # Auto-login if no valid session exists
    if not session_info.get('has_session', False):
        try:
            print("No valid session found, attempting auto-login...")
            username = "taotaufx"
            password = "jigno9-hurfyx-xibmYb"
            
            session_id = tradingview.login_with_credentials(username, password)
            print(f"Auto-login successful, session: {session_id[:8]}...")
            # Refresh session info after login
            session_info = database.get_session_info()
            
        except Exception as e:
            print(f"Auto-login failed: {e}")
            logging.error(f"Auto-login error: {e}")
    
    return render_template('index.html', session_info=session_info)

@app.route('/docs')
def api_docs():
    """API documentation page"""
    return render_template('api_docs.html')

@app.route('/status')
def status():
    """Status endpoint for monitoring"""
    session_info = database.get_session_info()
    return jsonify({
        'status': 'online',
        'timestamp': datetime.now().isoformat(),
        'session': session_info,
        'service': 'TradingView Chart Capture API'
    })

@app.errorhandler(404)
def not_found(error):
    session_info = database.get_session_info()
    return render_template('index.html', session_info=session_info, error='Page not found'), 404

@app.errorhandler(500)
def internal_error(error):
    session_info = database.get_session_info()
    return render_template('index.html', session_info=session_info, error='Internal server error'), 500
