#!/bin/bash

echo "🚀 Deploying E-Commerce Platform..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Step 1: Preparing Backend for Railway...${NC}"
cd projects/django-ecommerce

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}Virtual environment not found. Please run setup first.${NC}"
    exit 1
fi

# Activate virtual environment and install dependencies
source venv/bin/activate
pip install -r requirements.txt

# Run migrations
echo -e "${YELLOW}Running database migrations...${NC}"
python manage.py migrate

# Collect static files
echo -e "${YELLOW}Collecting static files...${NC}"
python manage.py collectstatic --noinput

echo -e "${GREEN}Backend ready for deployment!${NC}"

echo -e "${YELLOW}Step 2: Preparing Frontend for Vercel...${NC}"
cd ../frontend-demo

# Install dependencies
npm install

# Build the project
echo -e "${YELLOW}Building frontend...${NC}"
npm run build

echo -e "${GREEN}Frontend ready for deployment!${NC}"

echo -e "${YELLOW}Step 3: Deployment Instructions${NC}"
echo ""
echo "Backend (Railway):"
echo "1. Go to https://railway.app"
echo "2. Sign up with GitHub"
echo "3. Click 'New Project' > 'Deploy from GitHub repo'"
echo "4. Select your repository"
echo "5. Set environment variables:"
echo "   - SECRET_KEY=your-secret-key"
echo "   - DATABASE_URL=postgresql://..."
echo "   - STRIPE_SECRET_KEY=sk_test_..."
echo "   - STRIPE_WEBHOOK_SECRET=whsec_..."
echo ""
echo "Frontend (Vercel):"
echo "1. Go to https://vercel.com"
echo "2. Sign up with GitHub"
echo "3. Click 'New Project' > 'Import Git Repository'"
echo "4. Select your repository"
echo "5. Set root directory to 'projects/frontend-demo'"
echo "6. Set environment variables:"
echo "   - NEXT_PUBLIC_API_BASE_URL=https://your-railway-app.railway.app"
echo "   - NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_..."
echo ""
echo -e "${GREEN}Deployment preparation complete! 🎉${NC}"
