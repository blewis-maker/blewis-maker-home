# 🚀 Deployment Guide

This guide will help you deploy the full-stack e-commerce platform to production.

## 📋 **Prerequisites**

- GitHub account
- Vercel account (for frontend)
- Railway/Heroku account (for backend)
- Stripe account (for payments)
- Domain name (optional)

## 🔧 **Backend Deployment (Railway)**

### 1. Prepare Backend

```bash
cd projects/django-ecommerce

# Create production requirements
pip freeze > requirements.txt

# Create .env.production
cp .env.example .env.production
```

### 2. Environment Variables

Set these in Railway dashboard:

```env
DEBUG=False
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@host:port/dbname
REDIS_URL=redis://host:port
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
ALLOWED_HOSTS=your-domain.com,api.your-domain.com
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

### 3. Deploy to Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### 4. Database Migration

```bash
# Run migrations
railway run python manage.py migrate
railway run python manage.py createsuperuser
```

## 🎨 **Frontend Deployment (Vercel)**

### 1. Prepare Frontend

```bash
cd projects/frontend-demo

# Create production environment
cp .env.local.example .env.production
```

### 2. Environment Variables

Set these in Vercel dashboard:

```env
NEXT_PUBLIC_API_BASE_URL=https://your-api.railway.app
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_...
```

### 3. Deploy to Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel
```

### 4. Configure Domain (Optional)

- Go to Vercel dashboard
- Select your project
- Go to Settings > Domains
- Add your custom domain

## 🐳 **Docker Deployment (Alternative)**

### 1. Backend with Docker

```bash
cd projects/django-ecommerce

# Build and run
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

### 2. Frontend with Docker

```bash
cd projects/frontend-demo

# Create Dockerfile
cat > Dockerfile << EOF
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
EOF

# Build and run
docker build -t frontend-demo .
docker run -p 3000:3000 frontend-demo
```

## 🔐 **Stripe Configuration**

### 1. Webhook Setup

1. Go to Stripe Dashboard > Webhooks
2. Add endpoint: `https://your-api.railway.app/api/payments/webhook/`
3. Select events:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `charge.succeeded`
   - `charge.failed`
4. Copy webhook secret to environment variables

### 2. Test Payments

```bash
# Test with Stripe CLI
stripe listen --forward-to localhost:8000/api/payments/webhook/
stripe trigger payment_intent.succeeded
```

## 📊 **Monitoring Setup**

### 1. Sentry (Error Tracking)

```bash
# Install Sentry
pip install sentry-sdk

# Add to settings.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True
)
```

### 2. Health Checks

```python
# Add to urls.py
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({"status": "healthy"})

urlpatterns = [
    path('health/', health_check),
    # ... other patterns
]
```

## 🚀 **CI/CD Pipeline**

### 1. GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Railway
        run: railway up

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Vercel
        run: vercel --prod
```

## 🔍 **Post-Deployment Checklist**

### Backend
- [ ] Database migrations applied
- [ ] Static files collected
- [ ] Environment variables set
- [ ] CORS configured
- [ ] Stripe webhooks working
- [ ] Health check endpoint responding

### Frontend
- [ ] Environment variables set
- [ ] API endpoints accessible
- [ ] Stripe payments working
- [ ] All pages loading correctly
- [ ] Mobile responsive

### Security
- [ ] HTTPS enabled
- [ ] Security headers configured
- [ ] CORS properly set
- [ ] Environment variables secure
- [ ] Database credentials secure

## 📈 **Performance Optimization**

### Backend
```python
# Add to settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
    }
}

# Database optimization
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'OPTIONS': {
            'MAX_CONNS': 20,
        }
    }
}
```

### Frontend
```javascript
// next.config.js
module.exports = {
  images: {
    domains: ['your-api.railway.app'],
    formats: ['image/webp', 'image/avif'],
  },
  compress: true,
  poweredByHeader: false,
}
```

## 🆘 **Troubleshooting**

### Common Issues

1. **CORS Errors**
   - Check CORS_ALLOWED_ORIGINS in backend
   - Verify frontend URL is correct

2. **Database Connection**
   - Check DATABASE_URL format
   - Verify database is accessible

3. **Stripe Webhooks**
   - Check webhook URL is correct
   - Verify webhook secret matches

4. **Static Files**
   - Run `collectstatic` command
   - Check STATIC_URL configuration

### Debug Commands

```bash
# Check backend logs
railway logs

# Check frontend logs
vercel logs

# Test API endpoints
curl https://your-api.railway.app/api/products/

# Test database connection
railway run python manage.py dbshell
```

## 📞 **Support**

If you encounter issues:

1. Check the logs first
2. Verify environment variables
3. Test endpoints individually
4. Check Stripe dashboard for webhook events
5. Review this guide for common solutions

---

**Your e-commerce platform is now live! 🎉**
