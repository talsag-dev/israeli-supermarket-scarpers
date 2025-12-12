import { useTranslation } from 'react-i18next';
import { Languages } from 'lucide-react';
import './LanguageSwitcher.css';

export default function LanguageSwitcher() {
  const { i18n } = useTranslation();

  const toggleLanguage = () => {
    const newLang = i18n.language === 'en' ? 'heb' : 'en';
    i18n.changeLanguage(newLang);
    localStorage.setItem('language', newLang);
    
    // Update document direction for RTL support
    document.documentElement.dir = newLang === 'heb' ? 'rtl' : 'ltr';
  };

  return (
    <button 
      onClick={toggleLanguage} 
      className="language-switcher"
      title={i18n.language === 'en' ? 'Switch to Hebrew' : 'עבור לאנגלית'}
    >
      <Languages size={20} strokeWidth={2.5} />
      <span>{i18n.language === 'en' ? 'עב' : 'EN'}</span>
    </button>
  );
}
