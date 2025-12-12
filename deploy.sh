#!/bin/bash

# Hetzner VPS Deployment Script
# This script automates the deployment process on a fresh Hetzner VPS

set -e  # Exit on error

echo "==================================="
echo "Supermarket Scraper Deployment"
echo "==================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root${NC}"
    exit 1
fi

echo -e "${GREEN}Step 1: Updating system...${NC}"
apt update && apt upgrade -y

echo -e "${GREEN}Step 2: Installing required packages...${NC}"
apt install -y git curl wget ufw htop

echo -e "${GREEN}Step 3: Setting up firewall...${NC}"
ufw --force enable
ufw allow 22    # SSH
ufw allow 80    # HTTP
ufw allow 443   # HTTPS
ufw allow 8080  # API (optional)

echo -e "${GREEN}Step 4: Installing Docker...${NC}"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
else
    echo "Docker already installed"
fi

echo -e "${GREEN}Step 5: Installing Docker Compose...${NC}"
if ! command -v docker compose &> /dev/null; then
    apt install -y docker-compose-plugin
else
    echo "Docker Compose already installed"
fi

echo -e "${GREEN}Step 6: Setting up volume directories...${NC}"
mkdir -p /mnt/clickhouse-data/clickhouse
mkdir -p /mnt/clickhouse-data/dumps
chmod -R 777 /mnt/clickhouse-data

echo -e "${GREEN}Step 7: Creating application directory...${NC}"
mkdir -p /opt/supermarket-scraper
cd /opt/supermarket-scraper

echo ""
echo -e "${YELLOW}==================================="
echo "Manual Steps Required:"
echo "===================================${NC}"
echo ""
echo "1. Copy your project files to /opt/supermarket-scraper/"
echo "   Example: scp -r /local/path root@YOUR_SERVER_IP:/opt/supermarket-scraper/"
echo ""
echo "2. Create .env file with your configuration:"
echo "   cd /opt/supermarket-scraper"
echo "   nano .env"
echo ""
echo "3. Start the application:"
echo "   docker compose -f docker-compose.prod.yml up -d"
echo ""
echo "4. Check logs:"
echo "   docker compose -f docker-compose.prod.yml logs -f"
echo ""
echo -e "${GREEN}Deployment preparation complete!${NC}"
