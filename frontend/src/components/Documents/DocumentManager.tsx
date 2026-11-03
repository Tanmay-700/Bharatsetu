import React, { useState, useEffect } from 'react';
import { Upload, FileText, CheckCircle2, AlertCircle, Loader2, Trash2, Database } from 'lucide-react';
import { documentsApi } from '../../api/documents';
import { DocumentItem, SUPPORTED_LANGUAGES } from '../../types';

export const DocumentManager: React.FC = () => {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [domain, setDomain] = useState('HR Policies');
  const [docType, setDocType] = useState('Company Policy');
  const [docLanguage, setDocLanguage] = useState('en');
  const [uploadMessage, setUploadMessage] = useState<string | null>(null);

  const fetchDocuments = async () => {
    try {
      const docs = await documentsApi.list();
      setDocuments(docs);
    } catch (err) {
      console.error('Failed to load documents:', err);
    }
  };

  useEffect(() => {
    fetchDocuments();
    // Poll every 5s if any document is processing
    const interval = setInterval(() => {
      setDocuments((prev) => {
        const hasProcessing = prev.some((d) => d.status === 'processing');
        if (hasProcessing) {
          fetchDocuments();
        }
        return prev;
      });
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;

    try {
      setIsUploading(true);
      setUploadMessage(null);
      await documentsApi.upload(selectedFile, domain, docType, docLanguage);
      setUploadMessage(`"${selectedFile.name}" uploaded successfully. Processing chunks in background...`);
      setSelectedFile(null);
      await fetchDocuments();
    } catch (err: any) {
      setUploadMessage(`Upload failed: ${err.message || 'Unknown error'}`);
    } finally {
      setIsUploading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this document and its vector chunks?')) return;
    try {
      await documentsApi.delete(id);
      await fetchDocuments();
    } catch (err) {
      console.error('Failed to delete document:', err);
    }
  };

  return (
    <div className="flex-1 overflow-y-auto p-6 max-w-5xl mx-auto w-full space-y-8">
      {/* Overview Banner */}
      <div className="bg-gradient-to-r from-slate-900 to-slate-800 text-white p-6 rounded-2xl shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight flex items-center gap-2">
            <Database className="w-5 h-5 text-brand-500" />
            Document Vault (Up to 20 PDFs)
          </h2>
          <p className="text-xs text-slate-300 mt-1 max-w-xl">
            Upload authorized company policies or educational textbooks (~100 pages each).
            Documents are parsed, chunked, and embedded into local ChromaDB with bge-m3.
          </p>
        </div>

        <div className="flex items-center space-x-3 bg-slate-800/80 border border-slate-700 px-4 py-2 rounded-xl text-xs">
          <div>
            <span className="text-slate-400 block">Total PDFs:</span>
            <span className="font-bold text-base text-white">{documents.length} / 20</span>
          </div>
          <div className="h-6 w-px bg-slate-700" />
          <div>
            <span className="text-slate-400 block">Total Chunks:</span>
            <span className="font-bold text-base text-brand-400">
              {documents.reduce((acc, d) => acc + (d.total_chunks || 0), 0)}
            </span>
          </div>
        </div>
      </div>

      {/* Upload Form */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs">
        <h3 className="font-semibold text-slate-800 text-base mb-4 flex items-center gap-2">
          <Upload className="w-4 h-4 text-brand-600" />
          Upload New Document (PDF)
        </h3>

        <form onSubmit={handleUpload} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Domain selector */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Domain / Subject
              </label>
              <input
                type="text"
                list="domain-options"
                value={domain}
                onChange={(e) => setDomain(e.target.value)}
                placeholder="e.g. HR Policies, Physics..."
                className="w-full text-xs bg-slate-50 border border-slate-300 rounded-lg p-2.5 focus:ring-2 focus:ring-brand-500 focus:outline-none"
                required
              />
              <datalist id="domain-options">
                <option value="HR Policies" />
                <option value="IT Security" />
                <option value="Compliance & Ethics" />
                <option value="Physics" />
                <option value="Chemistry" />
                <option value="Mathematics" />
              </datalist>
            </div>

            {/* Document Type */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Document Type
              </label>
              <select
                value={docType}
                onChange={(e) => setDocType(e.target.value)}
                className="w-full text-xs bg-slate-50 border border-slate-300 rounded-lg p-2.5 focus:ring-2 focus:ring-brand-500 focus:outline-none"
              >
                <option value="Company Policy">Company Policy</option>
                <option value="Standard Operating Procedure">Standard Operating Procedure</option>
                <option value="Educational Textbook">Educational Textbook</option>
                <option value="Legal Contract">Legal Contract</option>
                <option value="Compliance Guide">Compliance Guide</option>
              </select>
            </div>

            {/* Source Document Language */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Original Document Language
              </label>
              <select
                value={docLanguage}
                onChange={(e) => setDocLanguage(e.target.value)}
                className="w-full text-xs bg-slate-50 border border-slate-300 rounded-lg p-2.5 focus:ring-2 focus:ring-brand-500 focus:outline-none"
              >
                {SUPPORTED_LANGUAGES.map((l) => (
                  <option key={l.code} value={l.code}>
                    {l.name} ({l.native})
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* File Picker */}
          <div className="border-2 border-dashed border-slate-300 rounded-xl p-6 text-center hover:border-brand-500 transition-colors bg-slate-50/50">
            <input
              type="file"
              accept=".pdf"
              id="file-upload"
              className="hidden"
              onChange={handleFileChange}
              disabled={isUploading}
            />
            <label
              htmlFor="file-upload"
              className="cursor-pointer flex flex-col items-center justify-center space-y-2"
            >
              <FileText className="w-8 h-8 text-slate-400" />
              <span className="text-xs font-medium text-slate-700">
                {selectedFile ? (
                  <span className="text-brand-700 font-semibold">{selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)</span>
                ) : (
                  <span>Click to browse educational or company policy PDF</span>
                )}
              </span>
              <span className="text-[11px] text-slate-400">PDF up to ~100 pages (~20MB)</span>
            </label>
          </div>

          {uploadMessage && (
            <div className="p-3 bg-brand-50 border border-brand-200 text-brand-800 rounded-lg text-xs">
              {uploadMessage}
            </div>
          )}

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={!selectedFile || isUploading}
              className={`flex items-center space-x-2 px-5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                selectedFile && !isUploading
                  ? 'bg-brand-600 hover:bg-brand-500 text-white shadow-sm'
                  : 'bg-slate-200 text-slate-400 cursor-not-allowed'
              }`}
            >
              {isUploading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Uploading & Processing...</span>
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4" />
                  <span>Ingest & Embed Document</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Indexed Documents Table */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-slate-800 text-base">
            Indexed Documents in System
          </h3>
          <span className="text-xs text-slate-500">
            {documents.length} registered
          </span>
        </div>

        {documents.length === 0 ? (
          <div className="text-center py-10 text-xs text-slate-500 border border-slate-100 rounded-xl bg-slate-50/50">
            No documents uploaded yet. Upload your first PDF above.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-700">
              <thead className="bg-slate-50 text-slate-500 uppercase text-[10px] tracking-wider border-b border-slate-200">
                <tr>
                  <th className="py-3 px-3">Document</th>
                  <th className="py-3 px-3">Domain</th>
                  <th className="py-3 px-3">Type</th>
                  <th className="py-3 px-3">Lang</th>
                  <th className="py-3 px-3">Pages</th>
                  <th className="py-3 px-3">Chunks</th>
                  <th className="py-3 px-3">Status</th>
                  <th className="py-3 px-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {documents.map((doc) => (
                  <tr key={doc.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3 px-3 font-medium text-slate-800 flex items-center space-x-2">
                      <FileText className="w-4 h-4 text-brand-600 flex-shrink-0" />
                      <span className="truncate max-w-[200px]" title={doc.filename}>
                        {doc.filename}
                      </span>
                    </td>
                    <td className="py-3 px-3">
                      <span className="bg-brand-50 text-brand-700 border border-brand-200 px-2 py-0.5 rounded-full font-medium text-[10px]">
                        {doc.domain}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-slate-500">{doc.document_type}</td>
                    <td className="py-3 px-3 uppercase text-slate-600 font-mono text-[10px]">{doc.language}</td>
                    <td className="py-3 px-3 text-slate-600">{doc.total_pages || '-'}</td>
                    <td className="py-3 px-3 text-slate-600 font-semibold">{doc.total_chunks || '-'}</td>
                    <td className="py-3 px-3">
                      {doc.status === 'completed' && (
                        <span className="inline-flex items-center gap-1 text-emerald-600 font-medium text-[11px]">
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          Ready
                        </span>
                      )}
                      {doc.status === 'processing' && (
                        <span className="inline-flex items-center gap-1 text-amber-600 font-medium text-[11px]">
                          <Loader2 className="w-3.5 h-3.5 animate-spin" />
                          Processing
                        </span>
                      )}
                      {doc.status === 'failed' && (
                        <span className="inline-flex items-center gap-1 text-red-600 font-medium text-[11px]" title={doc.error_message}>
                          <AlertCircle className="w-3.5 h-3.5" />
                          Failed
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-3 text-right">
                      <button
                        onClick={() => handleDelete(doc.id)}
                        className="p-1 text-slate-400 hover:text-red-500 transition-colors"
                        title="Delete document and chunks"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
