import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { ShoppingCart, RotateCcw } from 'lucide-react';
import QueryView from './components/QueryView';
import LanguageSwitcher from './components/LanguageSwitcher';
import './App.css';

export default function App() {
  const { t, i18n } = useTranslation();
  const [history, setHistory] = useState([]);
  const [conversationHistory, setConversationHistory] = useState([]);

  useEffect(() => {
    document.documentElement.dir = i18n.language === 'heb' ? 'rtl' : 'ltr';
  }, [i18n.language]);

  const handleNewConversation = () => {
    setHistory([]);
    setConversationHistory([]);
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div className="header-main">
            <div className="logo">
              <ShoppingCart className="logo-icon" size={32} strokeWidth={2.5} />
              <div className="logo-text">
                <h1>{t('app.title')}</h1>
                <p className="header-subtitle">{t('app.subtitle')}</p>
              </div>
            </div>
            
            <div className="header-controls">
              <div className="header-actions">
                {history.length > 0 && (
                  <button 
                    onClick={handleNewConversation} 
                    className="btn btn-secondary btn-sm"
                    style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
                  >
                    <RotateCcw size={16} />
                    {t('query.newConversation')}
                  </button>
                )}
                <LanguageSwitcher />
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="app-main">
        <QueryView 
          history={history}
          setHistory={setHistory}
          conversationHistory={conversationHistory}
          setConversationHistory={setConversationHistory}
        />
      </main>
    </div>
  );
}
