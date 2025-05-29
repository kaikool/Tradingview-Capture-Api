class APITester {
    constructor() {
        this.baseUrl = '/api';
    }

    init() {
        console.log('API Tester initialized');
        this.checkSessionStatus();
        setInterval(() => this.checkSessionStatus(), 15000);
    }

    async makeRequest(endpoint, options = {}) {
        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            ...options
        };

        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`, defaultOptions);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || `HTTP ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error(`Request failed: ${error.message}`);
            throw error;
        }
    }

    showResult(data, isError = false) {
        const resultDiv = document.getElementById('result');
        if (!resultDiv) return;

        const alertClass = isError ? 'alert-danger' : 'alert-success';
        const icon = isError ? 'fa-exclamation-triangle' : 'fa-check';
        
        resultDiv.innerHTML = `
            <div class="alert ${alertClass}" role="alert">
                <i class="fas ${icon} me-2"></i>
                <strong>${isError ? 'Error' : 'Success'}</strong>
            </div>
            <pre class="bg-dark text-light p-3 rounded">${JSON.stringify(data, null, 2)}</pre>
        `;
    }

    showAlert(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.container');
        container.insertBefore(alertDiv, container.firstChild);
        
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }

    setButtonLoading(button, loading = true) {
        if (!button) return;
        
        if (loading) {
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Loading...';
        } else {
            button.disabled = false;
            button.innerHTML = button.getAttribute('data-original-text') || 'Submit';
        }
    }

    async handleLogin() {
        const button = document.getElementById('loginBtn');
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        if (!username || !password) {
            this.showAlert('Please enter both username and password', 'warning');
            return;
        }

        this.setButtonLoading(button, true);

        try {
            const result = await this.makeRequest('/login', {
                method: 'POST',
                body: JSON.stringify({ username, password })
            });

            this.showAlert('Login successful!', 'success');
            this.showResult(result);
            setTimeout(() => location.reload(), 1500);

        } catch (error) {
            this.showAlert(`Login failed: ${error.message}`, 'danger');
            this.showResult({ error: error.message }, true);
        } finally {
            this.setButtonLoading(button, false);
        }
    }



    async handleCapture() {
        const button = document.querySelector('#captureForm button[type="submit"]');
        const chart_id = document.getElementById('chart').value;
        const adjustment = parseInt(document.getElementById('adjustment').value) || 30;
        const interval = document.getElementById('interval').value;
        const theme = document.getElementById('theme').value;

        if (!chart_id) {
            this.showAlert('Please enter a chart ID', 'warning');
            return;
        }

        this.setButtonLoading(button, true);

        const requestData = {
            chart_id: chart_id,
            adjustment,
            interval,
            theme
        };

        try {
            const result = await this.makeRequest('/capture', {
                method: 'POST',
                body: JSON.stringify(requestData)
            });

            this.showAlert('Chart captured successfully!', 'success');
            this.showResult(result);

        } catch (error) {
            this.showAlert(`Capture failed: ${error.message}`, 'danger');
            this.showResult({ error: error.message }, true);
        } finally {
            this.setButtonLoading(button, false);
        }
    }



    async checkSessionStatus() {
        try {
            const result = await this.makeRequest('/session-status');
            console.log('Session status:', result);
        } catch (error) {
            console.error('Failed to check session status:', error);
        }
    }



    async handleRefreshSession() {
        const button = document.getElementById('refreshSessionBtn');
        this.setButtonLoading(button, true);

        try {
            const result = await this.makeRequest('/refresh-session', {
                method: 'POST',
                body: JSON.stringify({})
            });
            
            this.showAlert('Session đã được làm mới! Vui lòng đăng nhập lại.', 'success');
            this.showResult(result);
            
            setTimeout(() => location.reload(), 1500);

        } catch (error) {
            this.showAlert(`Không thể làm mới session: ${error.message}`, 'danger');
            this.showResult({ error: error.message }, true);
        } finally {
            this.setButtonLoading(button, false);
        }
    }



    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            this.showAlert('Copied to clipboard!', 'success');
        } catch (err) {
            console.error('Failed to copy: ', err);
            this.showAlert('Failed to copy to clipboard', 'danger');
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {
    window.apiTester = new APITester();
    window.apiTester.init();
});