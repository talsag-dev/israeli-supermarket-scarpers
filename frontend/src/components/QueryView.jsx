import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { User, Bot, MessageSquare, RotateCcw } from 'lucide-react';
import { format } from 'date-fns';
import './QueryView.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080';

const SUGGESTIONS = [
  'cheapestMilk',
  'pastaPrices',
  'tlvStores'
];

export default function QueryView({ history, setHistory, conversationHistory, setConversationHistory }) {
  const { t } = useTranslation();
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    const userQuestion = question;
    setQuestion('');
    setLoading(true);

    // Add user question to UI history
    setHistory(prev => [...prev, { type: 'question', content: userQuestion }]);

    try {
      const response = await axios.post(`${API_URL}/query`, {
        question: userQuestion,
        conversation_history: conversationHistory
      });

      const sqlGenerated = response.data.sql;

      // Add response to UI history
      setHistory(prev => [...prev, {
        type: 'answer',
        question: userQuestion,
        sql: sqlGenerated,
        data: response.data.data,
        columns: response.data.columns,
        error: response.data.error
      }]);

      // Update conversation history for OpenAI with natural language context
      // This helps the LLM understand what was asked and maintain context
      setConversationHistory(prev => [
        ...prev,
        { role: 'user', content: userQuestion },
        { role: 'assistant', content: `I searched for: ${userQuestion}. The SQL query was: ${sqlGenerated}` }
      ]);
    } catch (error) {
      setHistory(prev => [...prev, {
        type: 'answer',
        error: error.response?.data?.detail || error.message || 'Failed to process query'
      }]);
    } finally {
      setLoading(false);
    }
  };



  return (
    <div className="query-view">
      <div className="query-header">
        <div>
          <h2>{t('query.header')}</h2>
          <p className="text-secondary">{t('query.description')}</p>
        </div>

      </div>

      <div className="chat-container">
        {history.length === 0 && (
          <div className="empty-state">
            <MessageSquare className="empty-icon" size={64} strokeWidth={1.5} />
            <h3>{t('query.emptyStateTitle')}</h3>
            <p className="text-muted">{t('query.emptyStateHint')}</p>
            <div className="suggestions-container">
              {SUGGESTIONS.map((key) => (
                <button 
                  key={key} 
                  className="suggestion-chip"
                  onClick={() => setQuestion(t(`suggestions.${key}`))}
                >
                  {t(`suggestions.${key}`)}
                </button>
              ))}
            </div>
          </div>
        )}

        {history.map((item, idx) => (
          <div key={idx} className="fade-in">
            {item.type === 'question' ? (
              <div className="message user-message">
                <div className="message-icon">
                  <User size={20} strokeWidth={2.5} />
                </div>
                <div className="message-content">
                  <p>{item.content}</p>
                </div>
              </div>
            ) : (
              <div className="message bot-message">
                <div className="message-icon">
                  <Bot size={20} strokeWidth={2.5} />
                </div>
                <div className="message-content">
                  {item.error ? (
                    <div className="error-box">
                      <strong>{t('query.error')}</strong> {item.error}
                    </div>
                  ) : (
                    <>
                      {item.data && item.data.length > 0 && (
                        <div className="results-container">
                          <div className="table-scroll">
                            <table className="results-table">
                              <thead>
                                <tr>
                                  {item.columns.map((col, i) => (
                                    <th key={i}>{t(`columns.${col}`, col)}</th>
                                  ))}
                                </tr>
                              </thead>
                              <tbody>
                                {item.data.map((row, i) => (
                                  <tr key={i}>
                                    {row.map((cell, j) => {
                                      const colName = item.columns[j];
                                      
                                      // Price Formatting
                                      const isPrice = ['ItemPrice', 'price', 'ItemPrice'].includes(colName);
                                      
                                      // Date Formatting
                                      const isDate = ['LastUpdate', 'last_update'].includes(colName);

                                      let cellValue = 'N/A';
                                      if (cell !== null) {
                                        if (isPrice && typeof cell === 'number') {
                                            cellValue = cell.toFixed(2);
                                        } else if (isDate) {
                                            try {
                                                cellValue = format(new Date(cell), 'dd/MM/yyyy HH:mm');
                                            } catch (e) {
                                                cellValue = String(cell); // Fallback if invalid date
                                            }
                                        } else {
                                            cellValue = String(cell);
                                        }
                                      }
                                      
                                      return (
                                        <td key={j}>{cellValue}</td>
                                      )
                                    })}
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>
                      )}

                      {item.data && item.data.length === 0 && (
                        <div className="info-box">
                          {t('query.noResults')}
                        </div>
                      )}
                    </>
                  )}
                </div>
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="message bot-message fade-in">
            <div className="message-icon">
              <Bot size={20} strokeWidth={2.5} />
            </div>
            <div className="message-content">
              <div className="flex items-center gap-sm">
                <div className="spinner"></div>
                <span className="text-muted">{t('query.processingMessage')}</span>
              </div>
            </div>
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="query-form">
        <input
          type="text"
          className="input"
          placeholder={t('query.placeholder')}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          disabled={loading}
        />
        <button type="submit" className="btn btn-primary" disabled={loading || !question.trim()}>
          {loading ? t('query.processing') : t('query.askButton')}
        </button>
      </form>
    </div>
  );
}
