# Docker Base Image Strategy for Elecantro

## 🎯 Problem Solved
Stop rebuilding all dependencies every time! This approach creates a **base Docker image** with all Python packages pre-installed, so updating `requirements.txt` only requires rebuilding the base image once.

## 📁 Files Created

```
docker/
├── base.Dockerfile      # Base image with all dependencies
├── backend.Dockerfile   # Backend using base image
├── worker.Dockerfile    # Worker using base image
├── build-base.sh       # Build script (Linux/Mac)
└── build-base.ps1      # Build script (Windows)
```

## 🚀 Quick Start

### 1. Build Base Image (Once)
```bash
# Windows PowerShell
.\docker\build-base.ps1

# Linux/Mac
chmod +x docker/build-base.sh
./docker/build-base.sh
```

### 2. Use Production Compose
```bash
docker compose -f docker-compose.prod.yml up --build
```

## 🔄 Workflow

### When `requirements.txt` Changes:
1. **Rebuild base image only:**
   ```bash
   .\docker\build-base.ps1
   ```

2. **Restart services (no rebuild needed):**
   ```bash
   docker compose -f docker-compose.prod.yml restart
   ```

### Benefits:
- ⚡ **Faster builds** - Dependencies installed once
- 🔄 **Reusable** - Same base for dev/prod
- 💾 **Layer caching** - Only rebuild changed layers
- 🎯 **Consistent** - Same environment everywhere

## 🏷️ Image Tags

Default: `elecantro/base:latest`

Custom tag:
```bash
.\docker\build-base.ps1 -Tag "elecantro/base:v1.2.0"
```

## 📊 Comparison

| Approach | Build Time | Docker Layers | Reusability |
|----------|------------|---------------|--------------|
| Traditional | 3-5 min | All layers | ❌ |
| Base Image | 1-2 min | Shared layers | ✅ |

## 🔧 Customization

### Add System Dependencies
Edit `docker/base.Dockerfile`:
```dockerfile
RUN apt-get install -y \
    build-essential \
    curl \
    git \
    # Add your packages here
```

### Environment Variables
Base image includes:
- `PYTHONDONTWRITEBYTECODE=1`
- `PYTHONUNBUFFERED=1`  
- `EVENTLET_MONKEY_PATCH=1`

## 🐛 Troubleshooting

### Base image not found:
```bash
# Build it first
.\docker\build-base.ps1
```

### Permission issues:
```bash
# Ensure appuser ownership
RUN chown -R appuser:appuser /app
```

### Cache issues:
```bash
# Force rebuild without cache
docker build --no-cache -f docker/base.Dockerfile -t elecantro/base:latest .
```

## 🎉 Result

Your development workflow is now optimized:
1. Update `requirements.txt`
2. Run `.\docker\build-base.ps1` 
3. Restart containers
4. ✅ All dependencies installed instantly!
