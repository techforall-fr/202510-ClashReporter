#!/bin/bash
# Smart Clash Reporter - Quick Start Script (Linux/Mac)

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Parse arguments
MOCK_MODE=true
if [ "$1" == "--live" ]; then
    MOCK_MODE=false
fi

echo -e "${CYAN}==========================================================${NC}"
echo -e "${YELLOW}  Smart Clash Reporter - Quick Start${NC}"
echo -e "${CYAN}==========================================================${NC}"
echo ""

MODE="MOCK"
if [ "$MOCK_MODE" == false ]; then
    MODE="LIVE"
fi

echo -e "Mode: ${GREEN}$MODE${NC}"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found. Please install Python 3.11+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✓ Python detected: $PYTHON_VERSION${NC}"
echo ""

# Check if requirements exist
if [ ! -f "backend/requirements.txt" ]; then
    echo -e "${RED}✗ Backend requirements.txt not found${NC}"
    exit 1
fi

if [ ! -f "frontend/requirements.txt" ]; then
    echo -e "${RED}✗ Frontend requirements.txt not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Dependencies files found${NC}"
echo ""

# Create directories
mkdir -p exports captures
echo -e "${GREEN}✓ Created storage directories${NC}"
echo ""

# Set environment
if [ "$MOCK_MODE" == true ]; then
    export USE_MOCK=true
fi

echo -e "${YELLOW}Starting services...${NC}"
echo ""

# Start Backend
echo -e "${CYAN}→ Starting Backend (port 8000)...${NC}"
cd backend
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend
echo "   Waiting for backend to initialize..."
sleep 5

# Start Frontend
echo -e "${CYAN}→ Starting Frontend (port 8501)...${NC}"
cd frontend
export API_BASE_URL=http://localhost:8000
python3 -m streamlit run streamlit_app.py --server.port 8501 &
FRONTEND_PID=$!
cd ..

# Wait for frontend
echo "   Waiting for frontend to initialize..."
sleep 8

echo ""
echo -e "${GREEN}==========================================================${NC}"
echo -e "${YELLOW}  Services are running!${NC}"
echo -e "${GREEN}==========================================================${NC}"
echo ""
echo -e "Frontend UI:  ${CYAN}http://localhost:8501${NC}"
echo -e "Backend API:  ${CYAN}http://localhost:8000${NC}"
echo -e "API Docs:     ${CYAN}http://localhost:8000/docs${NC}"
echo ""
echo -e "${GREEN}==========================================================${NC}"
echo ""

# Open browser (if available)
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:8501 &
elif command -v open &> /dev/null; then
    open http://localhost:8501 &
fi

echo -e "${GREEN}✓ Smart Clash Reporter is ready!${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Wait for Ctrl+C
trap "echo ''; echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; exit 0" INT
wait
