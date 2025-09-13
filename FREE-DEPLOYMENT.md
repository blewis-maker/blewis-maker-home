# 🆓 **FREE Deployment Guide - No Credit Card Required!**

Deploy your e-commerce platform completely free using Railway (backend) and Vercel (frontend).

## 🎯 **What You'll Get**

- **Backend API**: `https://your-app.railway.app`
- **Frontend Demo**: `https://your-app.vercel.app`
- **Database**: PostgreSQL (free tier)
- **CDN**: Global edge network
- **HTTPS**: Automatic SSL certificates

## 🚀 **Step 1: Deploy Backend to Railway (FREE)**

### 1.1 **Sign Up for Railway**
1. Go to [https://railway.app](https://railway.app)
2. Click "Sign up with GitHub"
3. Authorize Railway to access your repositories

### 1.2 **Deploy Your Backend**
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your `blewis-maker-home` repository
4. Railway will automatically detect it's a Django project

### 1.3 **Add PostgreSQL Database**
1. In your project dashboard, click "New"
2. Select "Database" > "PostgreSQL"
3. Railway will automatically set the `DATABASE_URL` environment variable

### 1.4 **Set Environment Variables**
In Railway dashboard, go to Variables tab and add:

```env
SECRET_KEY=your-super-secret-key-here-make-it-long-and-random
DEBUG=False
DATABASE_URL=postgresql://... (auto-set by Railway)
STRIPE_SECRET_KEY=sk_test_your_stripe_test_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

### 1.5 **Deploy**
1. Railway will automatically build and deploy
2. Wait for deployment to complete (5-10 minutes)
3. Copy your Railway URL (e.g., `https://your-app.railway.app`)

## 🎨 **Step 2: Deploy Frontend to Vercel (FREE)**

### 2.1 **Sign Up for Vercel**
1. Go to [https://vercel.com](https://vercel.com)
2. Click "Sign up with GitHub"
3. Authorize Vercel to access your repositories

### 2.2 **Deploy Your Frontend**
1. Click "New Project"
2. Select "Import Git Repository"
3. Choose your `blewis-maker-home` repository
4. Set **Root Directory** to `projects/frontend-demo`
5. Click "Deploy"

### 2.3 **Set Environment Variables**
In Vercel dashboard, go to Settings > Environment Variables:

```env
NEXT_PUBLIC_API_BASE_URL=https://your-app.railway.app
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
```

### 2.4 **Redeploy**
1. After setting environment variables, click "Redeploy"
2. Wait for deployment to complete
3. Copy your Vercel URL (e.g., `https://your-app.vercel.app`)

## 🔧 **Step 3: Configure Stripe (FREE Test Mode)**

### 3.1 **Get Stripe Keys**
1. Go to [https://stripe.com](https://stripe.com)
2. Sign up for free account
3. Go to Developers > API Keys
4. Copy your **Publishable key** (starts with `pk_test_`)
5. Copy your **Secret key** (starts with `sk_test_`)

### 3.2 **Set Up Webhooks**
1. Go to Developers > Webhooks
2. Click "Add endpoint"
3. URL: `https://your-app.railway.app/api/payments/webhook/`
4. Select events:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `charge.succeeded`
   - `charge.failed`
5. Copy the webhook secret (starts with `whsec_`)

## 🔄 **Step 4: Update CORS Settings**

### 4.1 **Update Backend CORS**
In Railway dashboard, update the `CORS_ALLOWED_ORIGINS` variable:
```env
CORS_ALLOWED_ORIGINS=https://your-app.vercel.app
```

### 4.2 **Redeploy Backend**
Railway will automatically redeploy when you update environment variables.

## 🧪 **Step 5: Test Your Deployment**

### 5.1 **Test Backend API**
```bash
# Test health endpoint
curl https://your-app.railway.app/api/health/

# Test products endpoint
curl https://your-app.railway.app/api/products/

# Test API documentation
open https://your-app.railway.app/api/docs/
```

### 5.2 **Test Frontend**
1. Open your Vercel URL
2. Try registering a new user
3. Browse products
4. Add items to cart
5. Test checkout (use Stripe test card: `4242 4242 4242 4242`)

## 📱 **Step 6: Update README with Live Links**

Update your `README.md` with the actual deployment URLs:

```markdown
## 🌟 **Live Demo**

- **Frontend Demo**: https://your-app.vercel.app
- **API Documentation**: https://your-app.railway.app/api/docs/
- **Admin Dashboard**: https://your-app.railway.app/admin/
```

## 🎉 **You're Live!**

Your e-commerce platform is now deployed and accessible worldwide!

### **What You've Accomplished:**
- ✅ **Free Backend**: Railway with PostgreSQL database
- ✅ **Free Frontend**: Vercel with global CDN
- ✅ **Free Database**: PostgreSQL with persistent storage
- ✅ **Free SSL**: Automatic HTTPS certificates
- ✅ **Free CDN**: Global edge network for fast loading
- ✅ **Production Ready**: Real-world deployment

### **Next Steps:**
1. **Share Your Demo**: Send links to potential employers
2. **Add to Portfolio**: Update your GitHub profile
3. **Monitor Performance**: Check Railway and Vercel dashboards
4. **Scale Up**: Upgrade plans only when needed

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

## 💡 **Pro Tips**

1. **Use Test Data**: Railway provides sample data for testing
2. **Monitor Usage**: Check Railway and Vercel dashboards
3. **Custom Domains**: Add your own domain (free on Vercel)
4. **Environment Variables**: Keep sensitive data in platform settings
5. **Automatic Deploys**: Both platforms auto-deploy on git push

---

## 🎯 **Success!**

You now have a **production-ready e-commerce platform** deployed for **FREE**!

**Perfect for:**
- 🎯 **Job Applications**: Show live demo to employers
- 💼 **Client Presentations**: Demonstrate your skills
- 🚀 **Portfolio Showcase**: Stand out from other developers
- 💰 **Freelance Work**: Prove your full-stack capabilities

**Your platform is live and ready to impress! 🚀**
