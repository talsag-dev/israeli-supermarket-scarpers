# Docker Setup Guide

## Quick Start

### 1. Start MongoDB Only (Test First)
```bash
docker compose up -d mongodb
```

Check MongoDB is running:
```bash
docker compose ps
docker compose logs mongodb
```

### 2. Build and Start the Scraper
```bash
docker compose build scraper
docker compose up scraper
```

This will:
- Scrape **ALL** supermarkets (no limit by default)
- Save files to `./dumps/` directory
- Store status in MongoDB

### 3. View Logs
```bash
# Follow scraper logs in real-time
docker compose logs -f scraper

# View MongoDB logs
docker compose logs mongodb
```

## Configuration Options

Edit `docker-compose.yml` to customize scraping:

### Limit to Specific Supermarkets
Uncomment and modify:
```yaml
ENABLED_SCRAPERS: "BAREKET,YAYNO_BITAN,SHUFERSAL,MEGA"
```

### Limit Files Per Scraper
Uncomment:
```yaml
LIMIT: 10  # Download max 10 files per supermarket
```

### Specify File Types
Uncomment:
```yaml
ENABLED_FILE_TYPES: "STORE_FILE,PRICE_FILE"
```

Available file types:
- `STORE_FILE` - Store information
- `PRICE_FILE` - Price data
- `PROMO_FILE` - Promotions
- Check `il_supermarket_scarper/utils/file_types.py` for all types

## MongoDB Access

### Connect to MongoDB
```bash
docker exec -it supermarket-mongo mongosh -u admin -p supermarket123
```

### View Scraped Data
```javascript
// Switch to database
use supermarket_scraper

// Show all collections (each task has its own collection)
show collections

// View recent downloads
db.verified_downloads.find().limit(10)

// View task status (replace YYYYMMDDHHMMSS with actual task ID)
db.getCollection('20251206120000').find().pretty()

// Count total files downloaded
db.verified_downloads.countDocuments()
```

## Useful Commands

### Stop Everything
```bash
docker compose down
```

### Stop and Remove All Data
```bash
docker compose down -v  # WARNING: Deletes all MongoDB data!
```

### Restart Scraper
```bash
docker compose restart scraper
```

### View Downloaded Files
```bash
ls -lh ./dumps/
```

## Environment Variables

You can also set environment variables instead of editing docker-compose.yml:

```bash
# Create .env file
cat > .env << EOF
MONGO_URL=mongodb://admin:supermarket123@mongodb:27017/
ENABLED_SCRAPERS=BAREKET,SHUFERSAL
LIMIT=5
EOF

# Then run
docker compose up scraper
```

## Troubleshooting

### Scraper exits immediately
Check logs:
```bash
docker compose logs scraper
```

### MongoDB connection failed
1. Check MongoDB is running: `docker compose ps`
2. Check MongoDB logs: `docker compose logs mongodb`
3. Verify connection string in docker-compose.yml

### Permission errors on dumps folder
```bash
sudo chown -R $USER:$USER ./dumps/
chmod -R 755 ./dumps/
```

## Next Steps

Once this works:
1. ✅ MongoDB is storing scraping status
2. ✅ Files are being downloaded to `./dumps/`
3. 🚀 Ready to add REST API
4. 🚀 Ready to add scheduler for automatic runs
