import React, { useState } from 'react';
import { FileText, ChevronDown, ChevronUp, Languages } from 'lucide-react';
import { SourceCitation } from '../../types';

interface CitationCardProps {
  citation: SourceCitation;
  index: number;
  onTranslate: (text: string) => void;
}

export const CitationCard: React.FC<CitationCardProps> = ({
  citation,
  index,
  onTranslate,
}) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 text-xs text-slate-700 shadow-sm transition-all hover:border-slate-300">
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center space-x-2 truncate">
          <span className="flex-shrink-0 w-5 h-5 rounded-full bg-slate-200 text-slate-700 font-semibold flex items-center justify-center text-[10px]">
            {index}
          </span>
          <FileText className="w-3.5 h-3.5 text-brand-600 flex-shrink-0" />
          <span className="font-semibold text-slate-800 truncate" title={citation.document_name}>
            {citation.document_name}
          </span>
        </div>

        <div className="flex items-center space-x-2 flex-shrink-0">
          <span className="bg-blue-50 text-blue-700 border border-blue-200 px-1.5 py-0.5 rounded font-medium text-[10px]">
            Pg {citation.page_number}
          </span>
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-slate-400 hover:text-slate-600 p-0.5"
            title={expanded ? "Show less" : "Show preview"}
          >
            {expanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      <div className="mt-1 flex items-center gap-2 text-[11px] text-slate-500">
        <span className="font-medium text-slate-600">{citation.section}</span>
        <span>•</span>
        <span className="text-[10px] bg-slate-200 text-slate-600 px-1.5 py-0.2 rounded">
          {citation.domain}
        </span>
      </div>

      {expanded && (
        <div className="mt-2.5 pt-2 border-t border-slate-200 text-slate-600 bg-white p-2 rounded border border-slate-100 font-mono text-[11px] leading-relaxed">
          <p className="whitespace-pre-wrap">{citation.content_preview}</p>
          <div className="mt-2 flex justify-end">
            <button
              onClick={() => onTranslate(citation.content_preview)}
              className="inline-flex items-center gap-1 px-2 py-1 bg-brand-50 hover:bg-brand-100 text-brand-700 rounded text-[11px] font-medium transition-colors"
            >
              <Languages className="w-3 h-3" />
              <span>Translate Passage</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
