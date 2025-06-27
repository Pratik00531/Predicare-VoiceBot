# 🚀 Deployment Guide for Predicare VoiceBot

This guide shows you how to deploy your AI Doctor API to various cloud platforms.

## 🌐 Deployment Options

### 1. 🚂 Railway (Recommended - Easiest)

**Why Railway?**
- Free tier available
- Automatic HTTPS
- Easy environment variables
- GitHub integration

**Steps:**
1. Go to [Railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your `Predicare-VoiceBot` repository
5. Add environment variables:
   - `GROQ_API_KEY=your_groq_key`
   - `ELEVENLABS_API_KEY=your_elevenlabs_key`
6. Deploy! 🎉

**Your API will be live at:** `https://your-app.railway.app`

### 2. 🎨 Render (Great for Production)

**Why Render?**
- Free tier with good performance
- Automatic deployments
- Built-in monitoring

**Steps:**
1. Go to [Render.com](https://render.com)
2. Connect your GitHub account
3. Click "New" → "Web Service"
4. Select your repository
5. Use these settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn api_backend:app --host 0.0.0.0 --port $PORT`
6. Add environment variables in the dashboard
7. Deploy!

**Your API will be live at:** `https://your-app.onrender.com`

### 3. ▲ Vercel (Serverless)

**Why Vercel?**
- Instant deployments
- Global CDN
- Perfect for frontend integration

**Steps:**
1. Install Vercel CLI: `npm i -g vercel`
2. Run `vercel` in your project directory
3. Follow the prompts
4. Add environment variables: `vercel env add`

### 4. 🐳 Docker (Any Platform)

**Build and run locally:**
```bash
# Build the Docker image
docker build -t predicare-voicebot .

# Run the container
docker run -p 8000:8000 \
  -e GROQ_API_KEY=your_groq_key \
  -e ELEVENLABS_API_KEY=your_elevenlabs_key \
  predicare-voicebot
```

**Deploy to:**
- Google Cloud Run
- AWS ECS
- Azure Container Instances
- DigitalOcean App Platform

### 5. 🔥 Heroku

**Steps:**
1. Install Heroku CLI
2. Create app: `heroku create your-app-name`
3. Add environment variables:
   ```bash
   heroku config:set GROQ_API_KEY=your_key
   heroku config:set ELEVENLABS_API_KEY=your_key
   ```
4. Deploy: `git push heroku main`

## 🔧 Configuration for Production

### Environment Variables (Required)
```env
GROQ_API_KEY=your_groq_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
```

### Optional Environment Variables
```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=1

# CORS (for production)
CORS_ORIGINS=["https://yourfrontend.com"]

# Logging
LOG_LEVEL=INFO
```

## 🌍 After Deployment

### 1. Test Your Live API
```bash
# Replace with your deployed URL
curl https://your-app.railway.app/health
```

### 2. Update Your TypeScript Client
```typescript
// Update the base URL in your frontend
const api = new PredicareAPI('https://your-app.railway.app');
```

### 3. Test All Endpoints
- `GET /health` - Health check
- `GET /docs` - API documentation
- `POST /analyze` - Medical analysis
- `POST /transcribe` - Speech-to-text
- `POST /synthesize` - Text-to-speech

## 🛡️ Security for Production

### 1. Environment Variables
- Never commit API keys to GitHub
- Use platform-specific secret management
- Rotate keys regularly

### 2. CORS Configuration
```python
# In api_backend.py, update for production:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourfrontend.com"],  # Specific domains only
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### 3. Rate Limiting (Recommended)
```bash
pip install slowapi
```

## 📊 Monitoring & Logs

### Railway
- Built-in metrics dashboard
- Real-time logs
- Automatic restarts

### Render
- Application metrics
- Log streaming
- Health checks

### Custom Monitoring
```python
# Add to api_backend.py
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url} - {response.status_code} - {process_time:.3f}s")
    return response
```

## 🎯 Quick Deploy Commands

### Railway (One-click)
1. Fork the repository
2. Connect to Railway
3. Add environment variables
4. Deploy!

### Render (Git-based)
```bash
# Just push to GitHub, Render auto-deploys
git push origin main
```

### Docker Compose
```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}
      - ELEVENLABS_API_KEY=${ELEVENLABS_API_KEY}
```

## 🔗 Integration with Your TypeScript Frontend

Once deployed, update your frontend:

```typescript
// Production configuration
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://your-app.railway.app'
  : 'http://localhost:8000';

const api = new PredicareAPI(API_BASE_URL);
```

## 🎉 Success Checklist

- [ ] API deployed and accessible
- [ ] Health check returns 200
- [ ] Environment variables configured
- [ ] API documentation accessible at `/docs`
- [ ] CORS configured for your frontend domain
- [ ] TypeScript client updated with production URL
- [ ] All endpoints tested and working

**Your AI Doctor is now live and ready for the world!** 🌍🩺
