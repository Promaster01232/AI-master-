#!/bin/bash

# AI Platform Deployment Script
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="my-ai-platform"
ENVIRONMENT=${1:-"production"}
DOCKER_COMPOSE_FILE="docker-compose.prod.yml"
BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"

echo -e "${GREEN}🚀 Deploying AI Platform (${ENVIRONMENT})${NC}\n"

# Create backup
create_backup() {
    echo -e "${YELLOW}📦 Creating backup...${NC}"
    mkdir -p $BACKUP_DIR
    
    # Backup database
    if [ -f "./database/main.db" ]; then
        cp ./database/main.db $BACKUP_DIR/
        echo "  Database backed up"
    fi
    
    # Backup documents
    if [ -d "./documents" ]; then
        tar -czf $BACKUP_DIR/documents.tar.gz ./documents
        echo "  Documents backed up"
    fi
    
    # Backup models
    if [ -d "./ai-models" ]; then
        tar -czf $BACKUP_DIR/models.tar.gz ./ai-models
        echo "  Models backed up"
    fi
    
    echo -e "${GREEN}✅ Backup created: ${BACKUP_DIR}${NC}"
}

# Stop existing services
stop_services() {
    echo -e "${YELLOW}🛑 Stopping existing services...${NC}"
    
    if [ -f "docker-compose.yml" ]; then
        docker-compose down || true
    fi
    
    if [ -f "$DOCKER_COMPOSE_FILE" ]; then
        docker-compose -f $DOCKER_COMPOSE_FILE down || true
    fi
    
    # Kill any processes on port 3000, 5000, 8000
    for port in 3000 5000 8000; do
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
    done
    
    echo -e "${GREEN}✅ Services stopped${NC}"
}

# Update code
update_code() {
    echo -e "${YELLOW}📥 Updating code...${NC}"
    
    # Pull latest code (if using git)
    if [ -d ".git" ]; then
        git pull origin main
        echo "  Code updated from git"
    fi
    
    # Update dependencies
    echo "  Updating dependencies..."
    
    # Backend
    if [ -f "./backend/requirements.txt" ]; then
        pip install -r ./backend/requirements.txt --upgrade
        echo "  Backend dependencies updated"
    fi
    
    # Frontend
    if [ -f "./frontend/package.json" ]; then
        cd ./frontend
        npm install --production
        npm run build
        cd ..
        echo "  Frontend dependencies updated and built"
    fi
    
    echo -e "${GREEN}✅ Code updated${NC}"
}

# Setup environment
setup_environment() {
    echo -e "${YELLOW}⚙️  Setting up environment...${NC}"
    
    # Copy environment files if they don't exist
    if [ ! -f ".env" ] && [ -f ".env.example" ]; then
        cp .env.example .env
        echo "  Created .env file from example"
    fi
    
    # Create necessary directories
    mkdir -p ./database ./documents ./logs ./uploads ./ai-models
    mkdir -p ./documents/raw ./documents/processed
    mkdir -p ./database/vector/chromadb
    mkdir -p ./training/datasets ./training/output ./training/checkpoints
    
    # Set permissions
    chmod -R 755 ./logs
    chmod -R 755 ./uploads
    
    echo -e "${GREEN}✅ Environment setup complete${NC}"
}

# Start services
start_services() {
    echo -e "${YELLOW}🚀 Starting services...${NC}"
    
    if [ "$ENVIRONMENT" = "production" ] && [ -f "$DOCKER_COMPOSE_FILE" ]; then
        echo "  Starting with Docker Compose (production)..."
        docker-compose -f $DOCKER_COMPOSE_FILE up -d --build
        
        # Wait for services to be ready
        sleep 10
        
        # Check if services are running
        if docker-compose -f $DOCKER_COMPOSE_FILE ps | grep -q "Up"; then
            echo -e "${GREEN}✅ Docker services started${NC}"
        else
            echo -e "${RED}❌ Docker services failed to start${NC}"
            docker-compose -f $DOCKER_COMPOSE_FILE logs
            exit 1
        fi
    else
        echo "  Starting in development mode..."
        
        # Start backend
        cd ./backend
        python main.py &
        BACKEND_PID=$!
        cd ..
        
        # Start frontend
        cd ./frontend
        npm start &
        FRONTEND_PID=$!
        cd ..
        
        echo "  Backend PID: $BACKEND_PID"
        echo "  Frontend PID: $FRONTEND_PID"
        
        # Save PIDs
        echo $BACKEND_PID > .backend.pid
        echo $FRONTEND_PID > .frontend.pid
        
        echo -e "${GREEN}✅ Development services started${NC}"
    fi
}

# Check health
check_health() {
    echo -e "${YELLOW}🔍 Checking service health...${NC}"
    
    # Wait a bit for services to start
    sleep 5
    
    # Check backend
    if curl -s http://localhost:5000/api/v1/health > /dev/null; then
        echo -e "  ${GREEN}✅ Backend is healthy${NC}"
    else
        echo -e "  ${RED}❌ Backend is not responding${NC}"
        return 1
    fi
    
    # Check frontend (if in production)
    if [ "$ENVIRONMENT" = "production" ]; then
        if curl -s http://localhost:3000 > /dev/null; then
            echo -e "  ${GREEN}✅ Frontend is healthy${NC}"
        else
            echo -e "  ${RED}❌ Frontend is not responding${NC}"
            return 1
        fi
    fi
    
    echo -e "${GREEN}✅ All services are healthy${NC}"
    return 0
}

# Setup models
setup_models() {
    echo -e "${YELLOW}🧠 Setting up AI models...${NC}"
    
    if [ -f "./backend/setup_models.py" ]; then
        python ./backend/setup_models.py
        echo -e "${GREEN}✅ Models setup complete${NC}"
    else
        echo -e "${YELLOW}⚠️  Model setup script not found${NC}"
    fi
}

# Main deployment
main() {
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}       AI Platform Deployment          ${NC}"
    echo -e "${GREEN}========================================${NC}\n"
    
    # Step 1: Backup
    create_backup
    
    # Step 2: Stop existing services
    stop_services
    
    # Step 3: Update code
    update_code
    
    # Step 4: Setup environment
    setup_environment
    
    # Step 5: Setup models (optional)
    if [ "$2" = "--setup-models" ]; then
        setup_models
    fi
    
    # Step 6: Start services
    start_services
    
    # Step 7: Check health
    if check_health; then
        echo -e "\n${GREEN}========================================${NC}"
        echo -e "${GREEN}     ✅ Deployment Successful!           ${NC}"
        echo -e "${GREEN}========================================${NC}"
        
        echo -e "\n🌐 Access URLs:"
        echo -e "   Frontend: http://localhost:3000"
        echo -e "   Backend API: http://localhost:5000"
        echo -e "   API Docs: http://localhost:5000/docs"
        
        echo -e "\n📊 Services:"
        if [ "$ENVIRONMENT" = "production" ]; then
            docker-compose -f $DOCKER_COMPOSE_FILE ps
        else
            echo -e "   Backend: Running (PID: $(cat .backend.pid 2>/dev/null || echo 'Not found'))"
            echo -e "   Frontend: Running (PID: $(cat .frontend.pid 2>/dev/null || echo 'Not found'))"
        fi
        
        echo -e "\n🔧 Next steps:"
        echo -e "   1. Open http://localhost:3000 in your browser"
        echo -e "   2. Login with admin credentials"
        echo -e "   3. Upload documents or start chatting"
        
    else
        echo -e "\n${RED}========================================${NC}"
        echo -e "${RED}     ❌ Deployment Failed!               ${NC}"
        echo -e "${RED}========================================${NC}"
        exit 1
    fi
}

# Run main function
main "$@"