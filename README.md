# TradingView Chart Capture API

Professional chart capture service for TradingView with advanced session management.

## Features
- Automated chart capture
- Session-based authentication  
- RESTful API
- Docker deployment ready
- Koyeb cloud deployment

## Deployment
Deploy directly to Koyeb using the included Dockerfile and koyeb.toml configuration.

## API Endpoints
- POST /api/login - Authentication
- POST /api/capture - Chart capture
- GET /api/session-status - Session validation
- GET /api/health - Health check