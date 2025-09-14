# Vercel Deployment Guide

## Fixed Issues ✅

1. **ImportError: cannot import name 'url_quote'** - Fixed with compatible Flask 3.0.3 + Werkzeug 3.0.3
2. **Template not found errors** - Fixed with `template_folder='../templates'` for Vercel serverless environment
3. **Malformed ABI string** - Replaced with proper JSON loading from `CONTRACT_ABI_JSON` environment variable
4. **Request parsing errors** - Fixed form data parsing and validation
5. **Serverless timeout issues** - Removed transaction receipt waiting

## Environment Variables Required

Set these in Vercel Project Settings → Environment Variables:

```bash
INFURA_URL=https://sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID
WALLET_PRIVATE_KEY=your_private_key_here
CONTRACT_ADDRESS=0xe183333fC6332faa9C32F502542d5554Bcb2192E
CONTRACT_ABI_JSON=[{"inputs":[], ...full ABI array here...}]
```

Use the complete ABI from `.env.example` for `CONTRACT_ABI_JSON`.

## Testing Endpoints

After deployment:

1. **Health Check**: `https://your-app.vercel.app/api/health` → Should return `{"status":"ok"}`
2. **Home Page**: `https://your-app.vercel.app/` → Should render mobile form
3. **Dashboard**: `https://your-app.vercel.app/dashboard` → Should render dashboard
4. **Submit Project**: POST to `/api/submit_project` with form data → Should return transaction hash

## Local Development

```bash
pip install -r requirements.txt
python app.py
```

Access at http://localhost:5000