import React, { useState, useEffect, useRef } from 'react';
import { 
  UploadCloud, 
  FileText, 
  CheckCircle2, 
  AlertCircle, 
  Trash2, 
  Eye, 
  Sparkles, 
  Clock, 
  X
} from 'lucide-react';
import { uploadResumes, listResumes, deleteResume, getResume } from '../services/api';

export default function UploadResumes() {
  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStatus, setUploadStatus] = useState('');
  const [error, setError] = useState(null);
  const [newlyUploaded, setNewlyUploaded] = useState([]);
  const [previewDoc, setPreviewDoc] = useState(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    loadResumes();
  }, []);

  const loadResumes = async () => {
    try {
      setLoading(true);
      const res = await listResumes();
      setResumes(res.data);
      setError(null);
    } catch (err) {
      console.error(err);
      setError('Could not fetch existing resumes.');
    } finally {
      setLoading(false);
    }
  };

  const handleFiles = async (files) => {
    if (!files || files.length === 0) return;

    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }

    try {
      setUploading(true);
      setUploadProgress(10);
      setUploadStatus(`Parsing ${files.length} document(s) with spaCy & PyMuPDF...`);

      const res = await uploadResumes(formData, (progress) => {
        setUploadProgress(progress);
      });

      setUploadStatus('Extraction complete! Candidate profiles generated.');
      setNewlyUploaded(res.data);
      await loadResumes();
      setError(null);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Failed to upload and parse resumes.');
    } finally {
      setUploading(false);
      setUploadProgress(0);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleDelete = async (resumeId) => {
    if (!window.confirm('Are you sure you want to delete this resume?')) return;
    try {
      await deleteResume(resumeId);
      setResumes(resumes.filter(r => r.id !== resumeId));
      setNewlyUploaded(newlyUploaded.filter(r => r.resume_doc_id !== resumeId));
    } catch (err) {
      console.error(err);
      alert('Error deleting resume.');
    }
  };

  const handleViewDetails = async (resumeId) => {
    try {
      const res = await getResume(resumeId);
      setPreviewDoc(res.data);
    } catch (err) {
      console.error(err);
      alert('Could not load resume preview.');
    }
  };

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Upload & Parse Resumes</h2>
        <p className="text-sm text-slate-500 mt-1">
          Upload PDF, DOCX, or TXT documents. Our automated NLP pipeline extracts entities, contacts, skills, and work history.
        </p>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-sm flex items-center gap-2">
          <AlertCircle className="w-5 h-5 shrink-0 text-rose-600" />
          <span>{error}</span>
        </div>
      )}

      {/* Upload Dropzone */}
      <div
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-2xl p-10 text-center transition-all bg-white ${
          uploading
            ? 'border-brand-400 bg-brand-50/20'
            : 'border-slate-300 hover:border-brand-500 hover:bg-slate-50/50'
        }`}
      >
        <div className="max-w-md mx-auto space-y-4">
          <div className="w-16 h-16 rounded-2xl bg-brand-50 border border-brand-100 text-brand-600 flex items-center justify-center mx-auto shadow-sm">
            <UploadCloud className="w-8 h-8" />
          </div>

          <div>
            <h3 className="font-bold text-slate-800 text-lg">
              {uploading ? 'Processing Resumes...' : 'Drag & drop resumes here'}
            </h3>
            <p className="text-xs text-slate-500 mt-1">
              Supports multiple files simultaneously • PDF, DOCX, or TXT (Max 10MB each)
            </p>
          </div>

          {uploading ? (
            <div className="space-y-2 pt-2">
              <div className="w-full bg-slate-200 rounded-full h-2.5 overflow-hidden">
                <div
                  className="bg-brand-600 h-2.5 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress || 60}%` }}
                ></div>
              </div>
              <p className="text-xs text-brand-700 font-medium">{uploadStatus}</p>
            </div>
          ) : (
            <div>
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept=".pdf,.docx,.doc,.txt"
                className="hidden"
                id="resume-file-input"
                onChange={(e) => handleFiles(e.target.files)}
              />
              <label
                htmlFor="resume-file-input"
                className="inline-flex items-center gap-2 px-5 py-2.5 bg-brand-600 hover:bg-brand-700 text-white font-medium text-sm rounded-xl cursor-pointer shadow-md transition-all"
              >
                <FileText className="w-4 h-4" />
                Select Files from Computer
              </label>
            </div>
          )}
        </div>
      </div>

      {/* Newly Uploaded & Parsed Resumes Summary */}
      {newlyUploaded.length > 0 && (
        <div className="bg-emerald-50/60 border border-emerald-200 rounded-2xl p-6 space-y-4">
          <div className="flex items-center gap-2 text-emerald-800 font-bold text-base">
            <CheckCircle2 className="w-5 h-5 text-emerald-600" />
            <span>Successfully Extracted {newlyUploaded.length} Candidate Profile(s)</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {newlyUploaded.map((item, idx) => (
              <div key={idx} className="bg-white rounded-xl p-4 border border-emerald-100 shadow-sm space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-slate-900 text-sm">{item.candidate_name}</span>
                  <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-brand-50 text-brand-700 border border-brand-200">
                    {item.parsed_data.estimated_experience_years} yrs exp
                  </span>
                </div>
                <p className="text-xs text-slate-500">{item.parsed_data.email || 'No email detected'}</p>
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {item.parsed_data.skills.slice(0, 6).map((sk, sidx) => (
                    <span
                      key={sidx}
                      className="text-[10px] font-medium px-2 py-0.5 rounded-md bg-slate-100 text-slate-700"
                    >
                      {sk.canonical_name}
                    </span>
                  ))}
                  {item.parsed_data.skills.length > 6 && (
                    <span className="text-[10px] text-slate-400 self-center">
                      +{item.parsed_data.skills.length - 6} more
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Existing Resumes Table */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden">
        <div className="p-6 border-b border-slate-200 flex items-center justify-between">
          <div>
            <h3 className="font-bold text-slate-800 text-base">Repository of Parsed Resumes</h3>
            <p className="text-xs text-slate-400">Total of {resumes.length} document(s) in repository</p>
          </div>
        </div>

        <div className="overflow-x-auto">
          {resumes.length > 0 ? (
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 text-slate-600 text-xs font-semibold uppercase tracking-wider">
                <tr>
                  <th className="py-3.5 px-6">File Name</th>
                  <th className="py-3.5 px-6">Extracted Candidate</th>
                  <th className="py-3.5 px-6">Skills Detected</th>
                  <th className="py-3.5 px-6">Est. Experience</th>
                  <th className="py-3.5 px-6 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {resumes.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-4 px-6 font-medium text-slate-900 flex items-center gap-2">
                      <FileText className="w-4 h-4 text-brand-600 shrink-0" />
                      <span className="truncate max-w-xs">{r.filename}</span>
                    </td>
                    <td className="py-4 px-6 text-slate-700">
                      <div>
                        <p className="font-semibold text-slate-900">{r.candidate_name}</p>
                        <p className="text-xs text-slate-400">{r.candidate_email || '—'}</p>
                      </div>
                    </td>
                    <td className="py-4 px-6">
                      <span className="inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-1 rounded-lg bg-indigo-50 text-indigo-700">
                        <Sparkles className="w-3.5 h-3.5" />
                        {r.skills_count} skills
                      </span>
                    </td>
                    <td className="py-4 px-6 text-slate-600 font-medium">
                      {r.experience_years} years
                    </td>
                    <td className="py-4 px-6 text-right space-x-2">
                      <button
                        onClick={() => handleViewDetails(r.id)}
                        className="p-1.5 rounded-lg text-slate-500 hover:text-brand-600 hover:bg-brand-50 transition-colors"
                        title="View Raw / Parsed Text"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(r.id)}
                        className="p-1.5 rounded-lg text-slate-500 hover:text-rose-600 hover:bg-rose-50 transition-colors"
                        title="Delete Document"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="p-10 text-center text-slate-400 text-sm">
              No resumes uploaded yet. Drag and drop resumes above to get started.
            </div>
          )}
        </div>
      </div>

      {/* Preview Modal */}
      {previewDoc && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-3xl w-full max-h-[85vh] flex flex-col shadow-2xl border border-slate-200">
            <div className="p-6 border-b border-slate-200 flex items-center justify-between">
              <div>
                <h3 className="font-bold text-slate-900 text-base">
                  {previewDoc.raw?.filename || 'Resume Document'}
                </h3>
                <p className="text-xs text-slate-500">Extracted Raw Text & Parsing Metadata</p>
              </div>
              <button
                onClick={() => setPreviewDoc(null)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 overflow-y-auto space-y-4 text-xs font-mono bg-slate-900 text-slate-200 rounded-b-2xl whitespace-pre-wrap leading-relaxed">
              {previewDoc.raw?.raw_text || 'No text extracted.'}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
