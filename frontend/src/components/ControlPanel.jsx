import { useState, useEffect } from 'react';
import axios from 'axios';
import './ControlPanel.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080';

export default function ControlPanel() {
  const [health, setHealth] = useState(null);
  const [scrapeStatus, setScrapeStatus] = useState('idle');
  const [importStatus, setImportStatus] = useState('idle');
  const [message, setMessage] = useState('');

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  const checkHealth = async () => {
    try {
      const response = await axios.get(`${API_URL}/health`);
      setHealth(response.data);
    } catch (error) {
      setHealth({ status: 'error', error: error.message });
    }
  };

  const triggerScrape = async () => {
    setScrapeStatus('loading');
    setMessage('');
    try {
      const response = await axios.post(`${API_URL}/scrape`);
      setMessage(response.data.message);
      setScrapeStatus('success');
      setTimeout(() => setScrapeStatus('idle'), 3000);
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Failed to start scraper');
      setScrapeStatus('error');
      setTimeout(() => setScrapeStatus('idle'), 3000);
    }
  };

  const triggerImport = async () => {
    setImportStatus('loading');
    setMessage('');
    try {
      const response = await axios.post(`${API_URL}/import`);
      setMessage(response.data.message);
      setImportStatus('success');
      setTimeout(() => setImportStatus('idle'), 3000);
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Failed to start importer');
      setImportStatus('error');
      setTimeout(() => setImportStatus('idle'), 3000);
    }
  };

  return (
    <div className="control-panel">
      <div className="control-header">
        <h2>Control Panel</h2>
        <p className="text-secondary">Manage scraper and data import operations</p>
      </div>

      <div className="control-grid">
        <div className="glass-card health-card">
          <h3>System Health</h3>
          <div className="health-status">
            {health === null ? (
              <div className="flex items-center gap-sm">
                <div className="spinner"></div>
                <span className="text-muted">Checking...</span>
              </div>
            ) : health.status === 'ok' ? (
              <div className="status-indicator status-success">
                <span className="status-dot"></span>
                <span>All Systems Operational</span>
              </div>
            ) : (
              <div className="status-indicator status-error">
                <span className="status-dot"></span>
                <span>System Error: {health.error}</span>
              </div>
            )}
          </div>
        </div>

        <div className="glass-card action-card">
          <h3>Data Scraper</h3>
          <p className="text-muted mb-md">Fetch latest data from supermarket sources</p>
          <button
            className="btn btn-primary full-width"
            onClick={triggerScrape}
            disabled={scrapeStatus === 'loading'}
          >
            {scrapeStatus === 'loading' ? (
              <span className="flex items-center justify-center gap-sm">
                <div className="spinner-small"></div>
                Running...
              </span>
            ) : scrapeStatus === 'success' ? (
              '✓ Started'
            ) : scrapeStatus === 'error' ? (
              '✗ Failed'
            ) : (
              'Start Scraper'
            )}
          </button>
        </div>

        <div className="glass-card action-card">
          <h3>Data Importer</h3>
          <p className="text-muted mb-md">Import scraped data into ClickHouse database</p>
          <button
            className="btn btn-success full-width"
            onClick={triggerImport}
            disabled={importStatus === 'loading'}
          >
            {importStatus === 'loading' ? (
              <span className="flex items-center justify-center gap-sm">
                <div className="spinner-small"></div>
                Running...
              </span>
            ) : importStatus === 'success' ? (
              '✓ Started'
            ) : importStatus === 'error' ? (
              '✗ Failed'
            ) : (
              'Start Import'
            )}
          </button>
        </div>
      </div>

      {message && (
        <div className={`message-box fade-in ${
          scrapeStatus === 'error' || importStatus === 'error' ? 'error' : 'success'
        }`}>
          {message}
        </div>
      )}

      <div className="glass-card info-section mt-lg">
        <h3>How It Works</h3>
        <div className="info-grid">
          <div className="info-item">
            <div className="info-number">1</div>
            <div>
              <strong>Scrape</strong>
              <p className="text-muted">Downloads price and store data from Israeli supermarket chains</p>
            </div>
          </div>
          <div className="info-item">
            <div className="info-number">2</div>
            <div>
              <strong>Import</strong>
              <p className="text-muted">Processes and loads the scraped data into ClickHouse for querying</p>
            </div>
          </div>
          <div className="info-item">
            <div className="info-number">3</div>
            <div>
              <strong>Query</strong>
              <p className="text-muted">Use natural language to ask questions about the imported data</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
