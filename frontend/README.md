# Supermarket Data Hub - Frontend

Modern React-based UI for querying and managing Israeli supermarket data.

## Features

- **Natural Language Queries**: Ask questions about supermarket data in plain English
- **Control Panel**: Manage scraper and data import operations
- **Premium Design**: Glassmorphism effects, gradients, and smooth animations
- **Real-time Status**: Live health checks and operation status

## Development

```bash
# Install dependencies
npm install

# Start dev server (http://localhost:3000)
npm run dev

# Build for production
npm run build
```

## Environment Variables

Create a `.env` file (gitignored) with:

```
VITE_API_URL=http://localhost:8080
```

## Docker Deployment

The frontend is included in the main docker-compose setup:

```bash
# From project root
docker-compose up frontend
```

The UI will be available at `http://localhost:3000`

## Tech Stack

- React 18
- Vite
- Axios for API calls
- Custom CSS with design system
