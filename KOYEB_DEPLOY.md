# Deploy TradingView Chart Capture lên Koyeb

## Bước 1: Chuẩn bị
1. Tạo tài khoản miễn phí tại [koyeb.com](https://www.koyeb.com)
2. Push code này lên GitHub repository

## Bước 2: Deploy trên Koyeb
1. **Connect GitHub**: Trong Koyeb dashboard, connect với GitHub repo
2. **App Settings**:
   - **Name**: `tradingview-capture`
   - **Builder**: Docker
   - **Port**: 5000
   - **Instance**: nano (free tier)

## Bước 3: Environment Variables
Thêm các biến môi trường:
```
SESSION_SECRET=your-secret-key-here
NODE_ENV=production
```

## Bước 4: Deploy
- Click "Deploy" 
- Đợi 5-10 phút build container
- Service sẽ có URL: `https://tradingview-capture-yourname.koyeb.app`

## Tính năng sau khi deploy:
✅ TradingView chart capture API
✅ Web dashboard
✅ Auto-login session management  
✅ SSL certificate tự động
✅ Global CDN

## Free Tier Limits:
- 2 nano services
- 512MB RAM
- 0.1 vCPU
- Đủ cho traffic cá nhân

Service sẽ chạy 24/7 miễn phí!