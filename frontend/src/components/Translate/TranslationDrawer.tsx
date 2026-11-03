import React, { useState } from 'react';
import { Languages, ArrowRight, Copy, Check, Loader2 } from 'lucide-react';
import { translateApi } from '../../api/translate';
import { SUPPORTED_LANGUAGES } from '../../types';

interface TranslationDrawerProps {
  initialText?: string;
}

export const TranslationDrawer: React.FC<TranslationDrawerProps> = ({ initialText = '' }) => {
  const [sourceText, setSourceText] = useState(initialText);
  const [targetLang, setTargetLang] = useState('ta');
  const [sourceLang, setSourceLang] = useState('en');
  const [translatedText, setTranslatedText] = useState('');
  const [isTranslating, setIsTranslating] = useState(false);
  const [copied, setCopied] = useState(false);

  React.useEffect(() => {
    if (initialText) {
      setSourceText(initialText);
    }
  }, [initialText]);

  const handleTranslate = async () => {
    if (!sourceText.trim()) return;
    try {
      setIsTranslating(true);
      const res = await translateApi.translate(sourceText, targetLang, sourceLang);
      setTranslatedText(res.translated_text);
    } catch (err) {
      console.error('Translation failed:', err);
    } finally {
      setIsTranslating(false);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(translatedText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="flex-1 overflow-y-auto p-6 max-w-4xl mx-auto w-full space-y-6">
      <div className="border-b border-slate-200 pb-4">
        <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2">
          <Languages className="w-5 h-5 text-brand-600" />
          Passage & Citation Translator
        </h2>
        <p className="text-xs text-slate-500 mt-1">
          Faithfully translate specific textbook clauses, policy passages, or paragraphs between all 8 supported languages.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Source Text Area */}
        <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs flex flex-col h-[340px]">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <span className="text-xs font-semibold text-slate-700">Source Text</span>
            <select
              value={sourceLang}
              onChange={(e) => setSourceLang(e.target.value)}
              className="text-xs bg-slate-100 border border-slate-200 rounded-lg px-2 py-1 text-slate-700"
            >
              <option value="auto">Auto Detect</option>
              {SUPPORTED_LANGUAGES.map((l) => (
                <option key={l.code} value={l.code}>
                  {l.name}
                </option>
              ))}
            </select>
          </div>

          <textarea
            value={sourceText}
            onChange={(e) => setSourceText(e.target.value)}
            placeholder="Paste textbook paragraph or policy clause here..."
            className="w-full flex-1 resize-none py-3 text-sm text-slate-800 placeholder-slate-400 focus:outline-none"
          />

          <div className="pt-2 border-t border-slate-100 flex justify-end">
            <button
              onClick={handleTranslate}
              disabled={!sourceText.trim() || isTranslating}
              className={`flex items-center space-x-1.5 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                sourceText.trim() && !isTranslating
                  ? 'bg-brand-600 hover:bg-brand-500 text-white shadow-xs'
                  : 'bg-slate-200 text-slate-400 cursor-not-allowed'
              }`}
            >
              {isTranslating ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Translating...</span>
                </>
              ) : (
                <>
                  <span>Translate</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </>
              )}
            </button>
          </div>
        </div>

        {/* Translated Result Area */}
        <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs flex flex-col h-[340px]">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <span className="text-xs font-semibold text-slate-700">Translated Result</span>
            <select
              value={targetLang}
              onChange={(e) => setTargetLang(e.target.value)}
              className="text-xs bg-slate-100 border border-slate-200 rounded-lg px-2 py-1 text-slate-700 font-semibold"
            >
              {SUPPORTED_LANGUAGES.map((l) => (
                <option key={l.code} value={l.code}>
                  {l.name} ({l.native})
                </option>
              ))}
            </select>
          </div>

          <div className="w-full flex-1 py-3 text-sm text-slate-800 overflow-y-auto font-sans leading-relaxed">
            {translatedText ? (
              <p className="whitespace-pre-wrap">{translatedText}</p>
            ) : (
              <span className="text-slate-400 text-xs italic">
                Translation will appear here...
              </span>
            )}
          </div>

          <div className="pt-2 border-t border-slate-100 flex justify-end">
            {translatedText && (
              <button
                onClick={handleCopy}
                className="flex items-center space-x-1 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-medium transition-colors"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-brand-600" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copied ? 'Copied' : 'Copy'}</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
