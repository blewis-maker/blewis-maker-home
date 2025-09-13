# 🚀 **Quick Free Deployment Guide**

Deploy your e-commerce platform for FREE in 15 minutes!

## 🎯 **What You'll Get**
- **Backend**: `https://your-app.railway.app`
- **Frontend**: `https://your-app.vercel.app`
- **Database**: PostgreSQL (free)
- **HTTPS**: Automatic SSL

## 📋 **Step 1: Deploy Backend (Railway) - 5 minutes**

### 1.1 **Sign Up & Deploy**
1. Go to [https://railway.app](https://railway.app)
2. Click "Sign up with GitHub"
3. Click "New Project" > "Deploy from GitHub repo"
4. Select your `blewis-maker-home` repository
5. Railway will auto-detect Django and start building

### 1.2 **Add Database**
1. In your project, click "New"
2. Select "Database" > "PostgreSQL"
3. Railway sets `DATABASE_URL` automatically

### 1.3 **Set Environment Variables**
In Railway dashboard > Variables tab, add:

```env
SECRET_KEY=django-insecure-your-super-secret-key-here-make-it-long
DEBUG=False
STRIPE_SECRET_KEY=sk_test_your_stripe_test_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

### 1.4 **Wait for Deployment**
- Railway will build and deploy automatically
- Copy your Railway URL (e.g., `https://your-app.railway.app`)

## 🎨 **Step 2: Deploy Frontend (Vercel) - 5 minutes**

### 2.1 **Sign Up & Deploy**
1. Go to [https://vercel.com](https://vercel.com)
2. Click "Sign up with GitHub"
3. Click "New Project" > "Import Git Repository"
4. Select your `blewis-maker-home` repository
5. **IMPORTANT**: Set **Root Directory** to `projects/frontend-demo`

### 2.2 **Set Environment Variables**
In Vercel dashboard > Settings > Environment Variables:

```env
NEXT_PUBLIC_API_BASE_URL=https://your-app.railway.app
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
```

### 2.3 **Deploy**
1. Click "Deploy"
2. Wait for deployment (2-3 minutes)
3. Copy your Vercel URL (e.g., `https://your-app.vercel.app`)

## 💳 **Step 3: Get Stripe Keys (2 minutes)**

### 3.1 **Sign Up for Stripe**
1. Go to [https://stripe.com](https://stripe.com)
2. Sign up for free account
3. Go to Developers > API Keys
4. Copy your **Publishable key** (`pk_test_...`)
5. Copy your **Secret key** (`sk_test_...`)

### 3.2 **Set Up Webhook**
1. Go to Developers > Webhooks
2. Click "Add endpoint"
3. URL: `https://your-app.railway.app/api/payments/webhook/`
4. Select events: `payment_intent.succeeded`, `payment_intent.payment_failed`
5. Copy webhook secret (`whsec_...`)

## 🔄 **Step 4: Update CORS (1 minute)**

### 4.1 **Update Backend CORS**
In Railway dashboard, update `CORS_ALLOWED_ORIGINS`:
```env
CORS_ALLOWED_ORIGINS=https://your-app.vercel.app
```

### 4.2 **Redeploy**
Railway will automatically redeploy when you save environment variables.

## 🧪 **Step 5: Test Your Deployment (2 minutes)**

### 5.1 **Test Backend**
```bash
# Test health endpoint
curl https://your-app.railway.app/api/health/

# Test API docs
open https://your-app.railway.app/api/docs/
```

### 5.2 **Test Frontend**
1. Open your Vercel URL
2. Try registering a new user
3. Browse products
4. Test checkout with Stripe test card: `4242 4242 4242 4242`

## 🎉 **You're Live!**

Your e-commerce platform is now deployed and accessible worldwide!

### **Update Your README**
Replace the placeholder URLs in your `README.md`:

```markdown
## 🌟 **Live Demo**

- **Frontend Demo**: https://your-app.vercel.app
- **API Documentation**: https://your-app.railway.app/api/docs/
- **Admin Dashboard**: https://your-app.railway.app/admin/
```

## 🆘 **Troubleshooting**

### **Common Issues:**

1. **CORS Errors**
   - Check `CORS_ALLOWED_ORIGINS` in Railway
   - Make sure frontend URL is correct

2. **Database Connection**
   - Check `DATABASE_URL` in Railway
   - Verify PostgreSQL service is running

3. **Stripe Payments Not Working**
   - Check webhook URL is correct
   - Verify webhook secret matches
   - Use test mode keys

4. **Frontend Not Loading**
   - Check `NEXT_PUBLIC_API_BASE_URL` in Vercel
   - Verify backend is accessible

### **Debug Commands:**
```bash
# Check Railway logs
railway logs

# Check Vercel logs
vercel logs

# Test API endpoints
curl https://your-app.railway.app/api/health/
```

## 🎯 **Success!**

You now have a **production-ready e-commerce platform** deployed for **FREE**!

**Perfect for:**
- 🎯 **Job Applications**: Show live demo to employers
- 💼 **Client Presentations**: Demonstrate your skills
- 🚀 **Portfolio Showcase**: Stand out from other developers
- 💰 **Freelance Work**: Prove your full-stack capabilities

**Your platform is live and ready to impress! 🚀**
