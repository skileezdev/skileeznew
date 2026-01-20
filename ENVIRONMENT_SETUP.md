# Environment Variables Setup Guide

## Local Development

### Option 1: Using .env file (Recommended)

1. **Create a `.env` file** in your project root:

```bash
# Video functionality has been removed from this application
# LiveKit configuration is no longer needed

# Option 3: Development mode (uses mock mode)
# Leave these commented out to use mock mode for development
```

2. **Make sure python-dotenv is installed** (already in requirements.txt):
```bash
pip install python-dotenv
```

### Option 2: System Environment Variables

**Windows (PowerShell):**
```powershell
# LiveKit configuration removed - video functionality no longer available
```

**Windows (Command Prompt):**
```cmd
# LiveKit configuration removed - video functionality no longer available
```

**macOS/Linux:**
```bash
# LiveKit configuration removed - video functionality no longer available
```

## Production Deployment

### Render Deployment

1. **Go to your Render dashboard**
2. **Select your web service**
3. **Go to "Environment" tab**
4. **Add these environment variables:**

```
# LiveKit configuration removed - video functionality no longer available
```

5. **Click "Save Changes"**
6. **Your service will automatically redeploy**

### Heroku Deployment

```bash
# LiveKit configuration removed - video functionality no longer available
```

### Docker Deployment

**Docker Compose:**
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      # LiveKit configuration removed - video functionality no longer available
```

**Docker Run:**
```bash
docker run -d \
  -p 5000:5000 \
  # LiveKit configuration removed - video functionality no longer available
  your-app-image
```

## Video Functionality Removed

Video calling functionality has been completely removed from this application. LiveKit integration is no longer available.
