const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

class TradingViewCapture {
    constructor() {
        this.browser = null;
        this.page = null;
    }

    async setup() {
        console.log('--->Setup Puppeteer start:', new Date().toISOString());
        
        try {
            this.browser = await puppeteer.launch({
                headless: true,
                executablePath: '/nix/store/zi4f80l169xlmivz8vja8wlphq74qqk0-chromium-125.0.6422.141/bin/chromium-browser',
                args: [
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu',
                    '--disable-extensions',
                    '--disable-default-apps',
                    '--window-size=1280,720'
                ]
            });
            
            this.page = await this.browser.newPage();
            await this.page.setViewport({ width: 1280, height: 720 });
            
            // Set user agent
            await this.page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36');
            
            console.log('Puppeteer setup complete');
            
        } catch (error) {
            console.error('Puppeteer setup error:', error);
            throw error;
        }
    }

    async screenshot(symbol, ticker = 'NONE', adjustment = 30, interval = '60', theme = 'dark') {
        console.log('--->Chart Capture:', symbol, ':', new Date().toISOString());
        
        const chartUrl = `https://www.tradingview.com/chart/?interval=${interval}&theme=${theme}&symbol=${symbol}`;
        
        try {
            await this.page.goto(chartUrl, { 
                waitUntil: 'networkidle2', 
                timeout: 30000 
            });
            
            // Wait for chart to load
            console.log('Waiting for chart to load...');
            await this.page.waitForSelector('.chart-container, .tv-chart-container', { timeout: 20000 });
            
            // Additional wait for chart rendering
            await new Promise(resolve => setTimeout(resolve, 5000));
            
            // Apply adjustments if needed
            if (adjustment > 0) {
                console.log(`Adjusting chart position ${adjustment} times...`);
                await this.page.keyboard.press('Escape');
                
                for (let i = 0; i < adjustment; i++) {
                    await this.page.keyboard.press('ArrowRight');
                    await new Promise(resolve => setTimeout(resolve, 10));
                }
                
                await new Promise(resolve => setTimeout(resolve, 500));
            }
            
            // Take screenshot
            const timestamp = Date.now();
            const screenshotPath = `charts/chart_${symbol.replace(':', '_')}_${timestamp}.png`;
            
            // Try to capture chart container first
            try {
                const chartElement = await this.page.$('.chart-container, .tv-chart-container');
                if (chartElement) {
                    await chartElement.screenshot({ path: screenshotPath, type: 'png' });
                } else {
                    await this.page.screenshot({ path: screenshotPath, type: 'png' });
                }
            } catch (e) {
                await this.page.screenshot({ path: screenshotPath, type: 'png' });
            }
            
            console.log('Main capture screenshot:', screenshotPath);
            return screenshotPath;
            
        } catch (error) {
            console.error('Main capture error:', error);
            throw error;
        }
    }

    async screenshotTestChart(chartId, ticker = 'NONE', adjustment = 30, interval = '60', theme = 'dark') {
        console.log('--->Test Chart Capture:', chartId, ':', new Date().toISOString());
        
        const chartUrl = `https://www.tradingview.com/chart/${chartId}/?interval=${interval}&theme=${theme}`;
        
        try {
            await this.page.goto(chartUrl, { 
                waitUntil: 'networkidle2', 
                timeout: 30000 
            });
            
            // Wait for chart to load
            console.log('Waiting for test chart to load...');
            await this.page.waitForSelector('.chart-container, .tv-chart-container', { timeout: 20000 });
            
            // Additional wait for chart rendering
            await new Promise(resolve => setTimeout(resolve, 5000));
            
            // Auto-center chart in viewport
            console.log('Auto-centering chart...');
            await this.page.evaluate(() => {
                const chartContainer = document.querySelector('.chart-container, .tv-chart-container');
                if (chartContainer) {
                    // Center the chart horizontally and vertically
                    const rect = chartContainer.getBoundingClientRect();
                    const centerX = window.innerWidth / 2;
                    const centerY = window.innerHeight / 2;
                    const scrollX = rect.left + (rect.width / 2) - centerX;
                    const scrollY = rect.top + (rect.height / 2) - centerY;
                    
                    window.scrollTo(scrollX, scrollY);
                }
            });
            
            // Wait for scroll to complete
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            // Apply adjustments if needed
            if (adjustment > 0) {
                console.log(`Adjusting test chart position ${adjustment} times...`);
                await this.page.keyboard.press('Escape');
                
                for (let i = 0; i < adjustment; i++) {
                    await this.page.keyboard.press('ArrowRight');
                    await new Promise(resolve => setTimeout(resolve, 10));
                }
                
                await new Promise(resolve => setTimeout(resolve, 500));
            }
            
            // Take screenshot
            const timestamp = Date.now();
            const screenshotPath = `charts/test_chart_${chartId}_${timestamp}.png`;
            
            // Try to capture chart container first
            try {
                const chartElement = await this.page.$('.chart-container, .tv-chart-container');
                if (chartElement) {
                    await chartElement.screenshot({ path: screenshotPath, type: 'png' });
                } else {
                    await this.page.screenshot({ path: screenshotPath, type: 'png' });
                }
            } catch (e) {
                await this.page.screenshot({ path: screenshotPath, type: 'png' });
            }
            
            console.log('Test capture screenshot:', screenshotPath);
            return screenshotPath;
            
        } catch (error) {
            console.error('Test capture error:', error);
            throw error;
        }
    }

    async setSession(sessionId) {
        // Try to load all cookies first, fallback to sessionId only if needed
        try {
            const success = await this.loadAllCookies();
            if (success) {
                console.log('All cookies loaded successfully from tradingview_cookies.json');
                return;
            }
        } catch (error) {
            console.log('Could not load full cookies, using sessionId only:', error.message);
        }
        
        // Fallback to sessionId only (legacy compatibility)
        if (!sessionId) return;
        
        try {
            await this.page.setCookie({
                name: 'sessionid',
                value: sessionId,
                domain: '.tradingview.com',
                path: '/',
                httpOnly: true,
                secure: true
            });
            
            console.log('Session cookie set successfully (sessionId only)');
        } catch (error) {
            console.error('Error setting session:', error);
        }
    }

    async loadAllCookies() {
        try {
            const cookiesData = JSON.parse(fs.readFileSync('/tmp/tradingview_cookies.json', 'utf8'));
            const cookies = cookiesData.cookies;
            
            // Check if cookies are expired
            if (Date.now() / 1000 > cookiesData.expires_at) {
                console.log('Stored cookies have expired');
                return false;
            }
            
            // Convert cookies dict to Puppeteer cookie format and set them
            const puppeteerCookies = Object.entries(cookies).map(([name, value]) => ({
                name: name,
                value: value,
                domain: '.tradingview.com',
                path: '/',
                httpOnly: name === 'sessionid', // Only sessionid should be httpOnly
                secure: true
            }));
            
            await this.page.setCookie(...puppeteerCookies);
            console.log(`Successfully loaded ${puppeteerCookies.length} cookies from storage`);
            return true;
            
        } catch (error) {
            console.error('Error loading cookies:', error);
            return false;
        }
    }

    async saveCookies() {
        try {
            const cookies = await this.page.cookies();
            fs.writeFileSync('cookies.json', JSON.stringify(cookies, null, 2));
            console.log('Cookies saved successfully');
        } catch (error) {
            console.error('Error saving cookies:', error);
        }
    }

    async quit() {
        try {
            if (this.page) {
                await this.page.close();
                this.page = null;
            }
            
            if (this.browser) {
                await this.browser.close();
                this.browser = null;
            }
            
            console.log('Browser closed successfully');
        } catch (error) {
            console.error('Error closing browser:', error);
        }
    }
}

// Main capture function 
async function captureChart(symbol, ticker = 'NONE', adjustment = 30, sessionId = null, interval = '60', theme = 'dark') {
    const capture = new TradingViewCapture();
    
    try {
        await capture.setup();
        
        if (sessionId) {
            await capture.setSession(sessionId);
        }
        
        const screenshotPath = await capture.screenshot(symbol, ticker, adjustment, interval, theme);
        return screenshotPath;
        
    } finally {
        await capture.quit();
    }
}

// Test capture function
async function captureTestChart(chartId, ticker = 'NONE', adjustment = 30, sessionId = null, interval = '60', theme = 'dark') {
    const capture = new TradingViewCapture();
    
    try {
        await capture.setup();
        
        if (sessionId) {
            await capture.setSession(sessionId);
        }
        
        const screenshotPath = await capture.screenshotTestChart(chartId, ticker, adjustment, interval, theme);
        return screenshotPath;
        
    } finally {
        await capture.quit();
    }
}

// Export for use from Python
if (require.main === module) {
    // Command line usage
    const args = process.argv.slice(2);
    
    // Check if --test flag is provided for test capture mode
    if (args[0] === '--test') {
        // Test capture mode with chart ID
        const chartId = args[1];
        const ticker = args[2] || 'NONE';
        const adjustment = parseInt(args[3]) || 30;
        const sessionId = args[4] || null;
        const interval = args[5] || '60';
        const theme = args[6] || 'dark';
        
        if (!chartId) {
            console.error('Usage: node captureutil_puppeteer.js --test <chartId> [ticker] [adjustment] [sessionId] [interval] [theme]');
            process.exit(1);
        }
        
        console.log('Using test capture mode...');
        captureTestChart(chartId, ticker, adjustment, sessionId, interval, theme)
            .then(result => {
                console.log('SUCCESS:', result);
                process.exit(0);
            })
            .catch(error => {
                console.error('ERROR:', error.message);
                process.exit(1);
            });
    } else {
        // Main capture mode with symbol
        const symbol = args[0];
        const ticker = args[1] || 'NONE';
        const adjustment = parseInt(args[2]) || 30;
        const sessionId = args[3] || null;
        const interval = args[4] || '60';
        const theme = args[5] || 'dark';
        
        if (!symbol) {
            console.error('Usage: node captureutil_puppeteer.js <symbol> [ticker] [adjustment] [sessionId] [interval] [theme]');
            console.error('       node captureutil_puppeteer.js --test <chartId> [ticker] [adjustment] [sessionId] [interval] [theme]');
            process.exit(1);
        }
        
        console.log('Using main capture mode...');
        captureChart(symbol, ticker, adjustment, sessionId, interval, theme)
            .then(result => {
                console.log('SUCCESS:', result);
                process.exit(0);
            })
            .catch(error => {
                console.error('ERROR:', error.message);
                process.exit(1);
            });
    }
}

module.exports = {
    TradingViewCapture,
    captureChart,
    captureTestChart
};