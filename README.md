# 🚀 Full-Stack E-Commerce Platform

A complete, production-ready e-commerce platform built with Django REST API and Next.js frontend.

## 🌟 **Live Demo**

- **Frontend Demo**: [https://your-frontend-demo.vercel.app](https://your-frontend-demo.vercel.app)
- **API Documentation**: [https://your-api-docs.vercel.app](https://your-api-docs.vercel.app)

## 🎯 **Project Overview**

This project demonstrates expertise in:
- **Backend Development**: Django REST Framework, PostgreSQL, JWT Authentication
- **Frontend Development**: Next.js 15, TypeScript, Tailwind CSS, React Query
- **Payment Processing**: Stripe integration with webhooks
- **Database Design**: Complex e-commerce data models with relationships
- **API Design**: RESTful APIs with comprehensive documentation

## 🛠️ **Tech Stack**

### Backend
- Django 5.0 + Django REST Framework
- PostgreSQL with PostGIS extension
- JWT Authentication
- Stripe API integration
- Redis for caching
- Celery for background tasks

### Frontend
- Next.js 15 with App Router
- TypeScript
- Tailwind CSS
- React Query + Context API
- React Hook Form + Zod validation
- Stripe Elements

## 🚀 **Quick Start**

### Backend Setup

1. **Clone and setup**
   ```bash
   git clone https://github.com/yourusername/blewis-maker-home.git
   cd blewis-maker-home/projects/django-ecommerce
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Database setup**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```

### Frontend Setup

1. **Setup frontend**
   ```bash
   cd ../frontend-demo
   npm install
   npm run dev
   ```

2. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Admin: http://localhost:8000/admin

## 🔧 **Features**

### 🛍️ **E-Commerce Features**
- Product Catalog with categories, brands, variants
- Shopping Cart with real-time updates
- Order Management with status tracking
- Payment Processing with Stripe
- User Management and authentication
- Search & Filters
- Responsive Design

### 🔐 **Security Features**
- JWT Authentication
- Password Security with bcrypt
- CORS Protection
- Input Validation
- SQL Injection Protection

## 📚 **API Endpoints**

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `GET /api/auth/profile/` - Get user profile

### Products
- `GET /api/products/` - List products
- `GET /api/products/{id}/` - Get product details
- `GET /api/categories/` - List categories

### Cart & Orders
- `GET /api/cart/` - Get user's cart
- `POST /api/cart/add/` - Add item to cart
- `GET /api/orders/` - List user's orders
- `POST /api/orders/` - Create new order

### Payments
- `POST /api/payments/create-payment-intent/` - Create Stripe payment
- `POST /api/payments/webhook/` - Stripe webhook handler

## 🧪 **Testing**

### Backend Tests
```bash
cd projects/django-ecommerce
python manage.py test
```

### Frontend Tests
```bash
cd projects/frontend-demo
npm run test
```

## 🚀 **Deployment**

### Backend (Railway/Heroku)
```bash
python manage.py collectstatic
python manage.py migrate
# Deploy to your preferred platform
```

### Frontend (Vercel)
```bash
npm install -g vercel
vercel
```

## 📁 **Project Structure**

```
blewis-maker-home/
├── projects/
│   ├── django-ecommerce/          # Backend API
│   │   ├── accounts/              # User management
│   │   ├── products/              # Product catalog
│   │   ├── cart/                  # Shopping cart
│   │   ├── orders/                # Order management
│   │   └── payments/              # Payment processing
│   └── frontend-demo/             # Next.js frontend
│       ├── src/app/               # Next.js App Router
│       ├── src/components/        # React components
│       └── src/contexts/          # React contexts
└── README.md
```

## 🎯 **Portfolio Highlights**

This project demonstrates:

✅ **Full-Stack Development**: Complete e-commerce solution  
✅ **Modern Technologies**: Django, Next.js, TypeScript  
✅ **Production Ready**: Error handling, testing, deployment  
✅ **Security Best Practices**: JWT, validation, CORS  
✅ **Payment Integration**: Stripe payment processing  
✅ **Responsive Design**: Mobile-first UI/UX  

**Perfect for showcasing skills to potential employers!** 🚀

## 👨‍💻 **Author**

**Brandan Lewis**
- GitHub: [@brandanlewis](https://github.com/brandanlewis)
- LinkedIn: [Brandan Lewis](https://linkedin.com/in/brandanlewis)

## 📄 **License**

MIT License - see LICENSE file for details.