import subprocess
import os
import database
from datetime import datetime
from threading import Thread
import logging


def screenshot(driver, symbol, ticker='NONE', adjustment=30, interval='60', theme='dark'):
    """Capture screenshot of TradingView chart with session (main capture)"""
    start_time = datetime.now()
    print(f'--->START Main Capture: {symbol} at {start_time}')
    
    try:
        # Debug: Get session ID timing
        session_start = datetime.now()
        sessionId = database.get_session()
        session_time = (datetime.now() - session_start).total_seconds()
        print(f"DEBUG: Session retrieval took {session_time:.2f}s")
        
        # Call Node.js Puppeteer script for main capture
        cmd = [
            'node', 
            'captureutil_puppeteer.js', 
            symbol, 
            ticker if ticker != 'NONE' else 'NONE',
            str(adjustment),
            sessionId if sessionId else '',
            interval,
            theme
        ]
        
        puppeteer_start = datetime.now()
        print(f"DEBUG: Starting Puppeteer at {puppeteer_start}")
        print(f"Running main capture command: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=os.getcwd()
        )
        
        puppeteer_time = (datetime.now() - puppeteer_start).total_seconds()
        print(f"DEBUG: Puppeteer execution took {puppeteer_time:.2f}s")
        
        if result.returncode == 0:
            # Parse output to get screenshot path
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if line.startswith('SUCCESS:'):
                    screenshot_path = line.replace('SUCCESS:', '').strip()
                    total_time = (datetime.now() - start_time).total_seconds()
                    print(f"DEBUG: TOTAL CAPTURE TIME: {total_time:.2f}s")
                    print(f"Main capture screenshot: {screenshot_path}")
                    return screenshot_path
            
            # Fallback - return last line
            screenshot_path = lines[-1].strip()
            total_time = (datetime.now() - start_time).total_seconds()
            print(f"DEBUG: TOTAL CAPTURE TIME (fallback): {total_time:.2f}s")
            return screenshot_path
        else:
            error_msg = result.stderr.strip() or result.stdout.strip()
            print(f"DEBUG: Puppeteer failed after {(datetime.now() - start_time).total_seconds():.2f}s")
            print(f"Puppeteer main capture error: {error_msg}")
            raise Exception(f"Puppeteer main capture failed: {error_msg}")
            
    except subprocess.TimeoutExpired:
        print(f"DEBUG: TIMEOUT after {(datetime.now() - start_time).total_seconds():.2f}s")
        raise Exception("Main capture timeout - chart took too long to load")
    except Exception as e:
        print(f"DEBUG: ERROR after {(datetime.now() - start_time).total_seconds():.2f}s")
        logging.error(f"Main capture error: {e}")
        raise


def screenshot_test_chart(chart_id, ticker='NONE', adjustment=30, interval='60', theme='dark'):
    """Capture screenshot of public TradingView chart using chart ID (test capture)"""
    start_time = datetime.now()
    print(f'--->START Test Capture: {chart_id} at {start_time}')
    
    try:
        # Debug: Get session ID timing
        session_start = datetime.now()
        sessionId = database.get_session()
        session_time = (datetime.now() - session_start).total_seconds()
        print(f"DEBUG: Test session retrieval took {session_time:.2f}s")
        
        # Call Node.js Puppeteer script for test capture
        cmd = [
            'node', 
            'captureutil_puppeteer.js', 
            '--test',
            chart_id,
            ticker if ticker != 'NONE' else 'NONE',
            str(adjustment),
            sessionId if sessionId else '',
            interval,
            theme
        ]
        
        puppeteer_start = datetime.now()
        print(f"DEBUG: Starting Test Puppeteer at {puppeteer_start}")
        print(f"Running test capture command: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=os.getcwd()
        )
        
        puppeteer_time = (datetime.now() - puppeteer_start).total_seconds()
        print(f"DEBUG: Test Puppeteer execution took {puppeteer_time:.2f}s")
        
        if result.returncode == 0:
            # Parse output to get screenshot path
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if line.startswith('SUCCESS:'):
                    screenshot_path = line.replace('SUCCESS:', '').strip()
                    total_time = (datetime.now() - start_time).total_seconds()
                    print(f"DEBUG: TOTAL TEST CAPTURE TIME: {total_time:.2f}s")
                    print(f"Test capture screenshot: {screenshot_path}")
                    return screenshot_path
            
            # Fallback - return last line
            screenshot_path = lines[-1].strip()
            total_time = (datetime.now() - start_time).total_seconds()
            print(f"DEBUG: TOTAL TEST CAPTURE TIME (fallback): {total_time:.2f}s")
            return screenshot_path
        else:
            error_msg = result.stderr.strip() or result.stdout.strip()
            print(f"DEBUG: Test Puppeteer failed after {(datetime.now() - start_time).total_seconds():.2f}s")
            print(f"Puppeteer test capture error: {error_msg}")
            raise Exception(f"Puppeteer test capture failed: {error_msg}")
            
    except subprocess.TimeoutExpired:
        print(f"DEBUG: TEST TIMEOUT after {(datetime.now() - start_time).total_seconds():.2f}s")
        raise Exception("Test capture timeout - chart took too long to load")
    except Exception as e:
        print(f"DEBUG: TEST ERROR after {(datetime.now() - start_time).total_seconds():.2f}s")
        logging.error(f"Test capture error: {e}")
        raise


def quit_browser(driver):
    """Close browser - handled by Puppeteer internally"""
    print('--->Exit browser : ' + str(datetime.now()))
    # Puppeteer handles cleanup automatically
    print('Browser cleanup complete')


def send_chart(symbol, ticker, message, delivery, interval='60', theme='dark', adjustment=30):
    """Send chart capture (updated to use symbol-based capture)"""
    try:
        screenshot_path = screenshot(None, symbol, ticker, adjustment, interval, theme)
        print(f"Chart captured: {screenshot_path}")
        return screenshot_path
        
    except Exception as e:
        print(f"Chart capture error: {e}")
        raise


def send_chart_async(symbol, ticker='NONE', message='', delivery='asap', interval='60', theme='dark', adjustment=30):
    """Send chart capture asynchronously (updated to use symbol)"""
    try:
        capture = Thread(target=send_chart,
                         args=[symbol, ticker, message, delivery, interval, theme, adjustment])
        capture.start()
        return True
    except Exception as e:
        print("[X] Capture error:\n>", e)
        logging.error(f"Async capture error: {e}")
        return False