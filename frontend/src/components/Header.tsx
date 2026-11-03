import React from 'react';
import { Globe, Database, Sparkles } from 'lucide-react';
import { SUPPORTED_LANGUAGES } from '../types';

interface HeaderProps {
  title: string;
  selectedLanguage: string;
  onLanguageChange: (lang: string) => void;
  activeDomain?: string;
}

export const Header: React.FC<HeaderProps> = ({
  title,
  selectedLanguage,
  onLanguageChange,
  activeDomain,
}) => {
  return (
    <header className="h-16 bg-white border-b border-slate-200 px-6 flex items-center justify-between shadow-sm flex-shrink-0 z-20">
      <div className="flex items-center space-x-3">
        <h2 className="font-semibold text-slate-800 text-lg tracking-tight truncate max-w-md">
          {title}
        </h2>
        {activeDomain && (
          <span className="inline-flex items-center gap-1 text-xs font-medium bg-brand-50 text-brand-700 border border-brand-200 px-2.5 py-0.5 rounded-full">
            <Sparkles className="w-3 h-3 text-brand-600" />
            Jev: {activeDomain}
          </span>
        )}
      </div>

      <div className="flex items-center space-x-4">
        {/* Vector DB status */}
        <div className="hidden sm:flex items-center space-x-1.5 text-xs text-slate-500 bg-slate-100 px-2.5 py-1 rounded-md">
          <Database className="w-3.5 h-3.5 text-slate-600" />
          <span>ChromaDB Ready</span>
        </div>

        {/* Global Target Answer Language Selector */}
        <div className="flex items-center space-x-2">
          <Globe className="w-4 h-4 text-slate-500" />
          <span className="text-xs font-medium text-slate-600 hidden md:inline">Answer Language:</span>
          <select
            value={selectedLanguage}
            onChange={(e) => onLanguageChange(e.target.value)}
            className="text-xs font-semibold bg-slate-100 hover:bg-slate-200/80 text-slate-800 border border-slate-300 rounded-lg px-2.5 py-1.5 focus:outline-none focus:ring-2 focus:ring-brand-500 cursor-pointer"
          >
            {SUPPORTED_LANGUAGES.map((lang) => (
              <option key={lang.code} value={lang.code}>
                {lang.name} ({lang.native})
              </option>
            ))}
          </select>
        </div>
      </div>
    </header>
  );
};
