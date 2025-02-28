#!/bin/bash
# Script to run the PlagiaTech application

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a process is running on a port
port_in_use() {
    lsof -i:"$1" >/dev/null 2>&1
}

# Check for required commands
echo -e "${YELLOW}Checking dependencies...${NC}"
MISSING_DEPS=0

if ! command_exists python3; then
    echo -e "${RED}Error: python3 is not installed${NC}"
    MISSING_DEPS=1
fi

if ! command_exists pip3; then
    echo -e "${RED}Error: pip3 is not installed${NC}"
    MISSING_DEPS=1
fi

if ! command_exists redis-server; then
    echo -e "${RED}Warning: redis-server is not installed${NC}"
    echo -e "${YELLOW}You can install Redis with:${NC}"
    echo -e "  - macOS: brew install redis"
    echo -e "  - Ubuntu/Debian: sudo apt install redis-server"
    echo -e "  - CentOS/RHEL: sudo yum install redis"
    MISSING_DEPS=1
fi

if [ $MISSING_DEPS -eq 1 ]; then
    echo -e "${RED}Please install missing dependencies and try again${NC}"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Warning: .env file not found. Creating a default one...${NC}"
    cat > .env << EOF
# API Keys
COPYLEAKS_API_KEY=demo_key
OPENAI_API_KEY=demo_key

# JWT Settings
JWT_SECRET_KEY=development_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis Settings
REDIS_URL=redis://localhost:6379/0

# Server Settings
PORT=8000
DEBUG=True
ENVIRONMENT=development

# Rate Limiting
RATE_LIMIT_DEFAULT=100/hour
RATE_LIMIT_FREE_TIER=10/day
EOF
    echo -e "${GREEN}Created default .env file${NC}"
fi

# Check if requirements are installed
echo -e "${YELLOW}Checking Python dependencies...${NC}"
if ! pip3 freeze | grep -q "fastapi"; then
    echo -e "${YELLOW}Installing Python dependencies...${NC}"
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error installing dependencies${NC}"
        exit 1
    fi
    echo -e "${GREEN}Dependencies installed successfully${NC}"
else
    echo -e "${GREEN}Dependencies already installed${NC}"
fi

# Check if ports are available
if port_in_use 8000; then
    echo -e "${RED}Error: Port 8000 is already in use${NC}"
    echo -e "${YELLOW}Please stop the service using port 8000 and try again${NC}"
    exit 1
fi

if port_in_use 3000; then
    echo -e "${RED}Error: Port 3000 is already in use${NC}"
    echo -e "${YELLOW}Please stop the service using port 3000 and try again${NC}"
    exit 1
fi

# Start Redis if not running
echo -e "${YELLOW}Checking Redis server...${NC}"
if ! redis-cli ping > /dev/null 2>&1; then
    echo -e "${YELLOW}Starting Redis server...${NC}"
    redis-server --daemonize yes
    sleep 1
    if ! redis-cli ping > /dev/null 2>&1; then
        echo -e "${RED}Error: Failed to start Redis server${NC}"
        exit 1
    fi
    echo -e "${GREEN}Redis server started${NC}"
else
    echo -e "${GREEN}Redis server is already running${NC}"
fi

# Start Celery worker
echo -e "${YELLOW}Starting Celery worker...${NC}"
celery -A celery_worker worker --loglevel=info > celery.log 2>&1 &
CELERY_PID=$!
echo -e "${GREEN}Celery worker started (PID: $CELERY_PID)${NC}"

# Start FastAPI server
echo -e "${YELLOW}Starting FastAPI server...${NC}"
uvicorn main:app --reload > api.log 2>&1 &
API_PID=$!
echo -e "${GREEN}FastAPI server started (PID: $API_PID)${NC}"

# Wait for API to start
echo -e "${YELLOW}Waiting for API to start...${NC}"
MAX_RETRIES=10
RETRY_COUNT=0
API_READY=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    sleep 1
    if curl -s http://localhost:8000/health > /dev/null; then
        API_READY=1
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT+1))
    echo -e "${YELLOW}Waiting for API to start (attempt $RETRY_COUNT/$MAX_RETRIES)...${NC}"
done

if [ $API_READY -eq 0 ]; then
    echo -e "${RED}Error: API failed to start${NC}"
    echo -e "${YELLOW}Check api.log for details${NC}"
    kill $CELERY_PID
    kill $API_PID
    exit 1
fi

echo -e "${GREEN}API is ready!${NC}"

# Start frontend server
echo -e "${YELLOW}Starting frontend server...${NC}"
python3 serve_frontend.py > frontend.log 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}Frontend server started (PID: $FRONTEND_PID)${NC}"

# Print summary
echo -e "\n${GREEN}PlagiaTech is now running:${NC}"
echo -e "  - API: http://localhost:8000"
echo -e "  - API Documentation: http://localhost:8000/api/docs"
echo -e "  - Frontend: http://localhost:3000"
echo -e "\n${YELLOW}Process IDs:${NC}"
echo -e "  - API Server: $API_PID"
echo -e "  - Celery Worker: $CELERY_PID"
echo -e "  - Frontend Server: $FRONTEND_PID"
echo -e "\n${YELLOW}Log files:${NC}"
echo -e "  - API: api.log"
echo -e "  - Celery: celery.log"
echo -e "  - Frontend: frontend.log"
echo -e "\n${YELLOW}Press Ctrl+C to stop all services${NC}"

# Function to clean up on exit
cleanup() {
    echo -e "\n${YELLOW}Stopping services...${NC}"
    kill $FRONTEND_PID 2>/dev/null
    kill $API_PID 2>/dev/null
    kill $CELERY_PID 2>/dev/null
    echo -e "${GREEN}Services stopped${NC}"
    exit 0
}

# Set up trap to catch Ctrl+C
trap cleanup INT

# Wait for user to press Ctrl+C
while true; do
    sleep 1
done
