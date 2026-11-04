import React, { useState, useEffect } from 'react';
import { 
  BarChart3, 
  TrendingUp, 
  Users, 
  Briefcase, 
  PieChart as PieIcon, 
  FileCheck2,
  Sparkles,
  Download
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  Cell,
  PieChart,
  Pie,
  Legend
} from 'recharts';
import { getAnalyticsOverview } from '../services/api';

export default function Analytics() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const res = await getAnalyticsOverview();
      setData(res.data);
      setError(null);
    } catch (err) {
      console.error(err);
      setError('Could not load analytics metrics.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-4 border-brand-200 border-t-brand-600 rounded-full animate-spin"></div>
          <p className="text-sm text-slate-500">Compiling recruitment analytics...</p>
        </div>
      </div>
    );
  }

  const distributionColors = ['#94a3b8', '#64748b', '#6366f1', '#4f46e5', '#10b981'];

  // Categories for pie chart
  const categoryCounts = {};
  (data?.top_candidate_skills || []).forEach((s) => {
    categoryCounts[s.category] = (categoryCounts[s.category] || 0) + s.count;
  });
  const pieData = Object.entries(categoryCounts).map(([name, value]) => ({ name, value }));
  const pieColors = ['#4f46e5', '#06b6d4', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6'];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Recruitment Analytics & Insights</h2>
          <p className="text-sm text-slate-500 mt-1">
            Data-driven visual overview of talent distribution, technical competencies, and algorithmic screening patterns.
          </p>
        </div>
      </div>

      {/* Primary KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm">
          <p className="text-xs font-semibold text-slate-500 uppercase">Screening Evaluations</p>
          <p className="text-3xl font-extrabold text-slate-900 mt-2">{data?.total_screenings || 0}</p>
          <p className="text-[11px] text-emerald-600 font-semibold mt-1">S-BERT embeddings computed</p>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm">
          <p className="text-xs font-semibold text-slate-500 uppercase">Mean Compatibility Score</p>
          <p className="text-3xl font-extrabold text-brand-600 mt-2">{data?.average_score || 0}%</p>
          <p className="text-[11px] text-slate-400 font-medium mt-1">Across all active postings</p>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm">
          <p className="text-xs font-semibold text-slate-500 uppercase">Total Candidates</p>
          <p className="text-3xl font-extrabold text-slate-900 mt-2">{data?.total_candidates || 0}</p>
          <p className="text-[11px] text-slate-400 font-medium mt-1">Parsed and indexed</p>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm">
          <p className="text-xs font-semibold text-slate-500 uppercase">Active Jobs</p>
          <p className="text-3xl font-extrabold text-slate-900 mt-2">{data?.active_jobs || 0}</p>
          <p className="text-[11px] text-slate-400 font-medium mt-1">Configured hiring criteria</p>
        </div>
      </div>

      {/* Main Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Score Distribution */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm space-y-4">
          <div>
            <h3 className="font-bold text-slate-800 text-base">Candidate Score Distribution</h3>
            <p className="text-xs text-slate-400">Histogram of composite compatibility across all screenings</p>
          </div>

          <div className="h-64 w-full">
            {data?.score_distribution && data.score_distribution.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.score_distribution}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="range_label" tick={{ fill: '#64748b', fontSize: 12 }} />
                  <YAxis tick={{ fill: '#64748b', fontSize: 12 }} allowDecimals={false} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#1e293b', borderRadius: '8px', color: '#fff', border: 'none' }}
                  />
                  <Bar dataKey="count" radius={[6, 6, 0, 0]} name="Candidates">
                    {data.score_distribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={distributionColors[index % distributionColors.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-slate-400 text-xs">
                No score data recorded yet.
              </div>
            )}
          </div>
        </div>

        {/* Top Extracted Candidate Skills */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm space-y-4">
          <div>
            <h3 className="font-bold text-slate-800 text-base">Top Candidate Competencies</h3>
            <p className="text-xs text-slate-400">Most frequently extracted skills from resume pool</p>
          </div>

          <div className="h-64 w-full">
            {data?.top_candidate_skills && data.top_candidate_skills.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.top_candidate_skills.slice(0, 7)} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis type="number" tick={{ fill: '#64748b', fontSize: 12 }} allowDecimals={false} />
                  <YAxis type="category" dataKey="skill" tick={{ fill: '#64748b', fontSize: 12 }} width={90} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#1e293b', borderRadius: '8px', color: '#fff', border: 'none' }}
                  />
                  <Bar dataKey="count" fill="#4f46e5" radius={[0, 6, 6, 0]} name="Candidates" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-slate-400 text-xs">
                No skills detected yet. Upload resumes to see skill frequency.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Secondary Charts: Category Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Domain Distribution */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm space-y-4">
          <div>
            <h3 className="font-bold text-slate-800 text-base">Competency Domains Share</h3>
            <p className="text-xs text-slate-400">Breakdown by technical engineering category</p>
          </div>

          <div className="h-64 w-full">
            {pieData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    label
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={pieColors[index % pieColors.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-slate-400 text-xs">
                No domain data available.
              </div>
            )}
          </div>
        </div>

        {/* Screening Metrics Summary Card */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm space-y-4 flex flex-col justify-between">
          <div>
            <h3 className="font-bold text-slate-800 text-base">Methodology & AI Architecture</h3>
            <p className="text-xs text-slate-400 mt-1">Core architectural parameters powering ResumeIQ</p>

            <div className="mt-4 space-y-3 text-xs">
              <div className="flex justify-between p-3 bg-slate-50 rounded-xl">
                <span className="text-slate-600 font-medium">Embedding Architecture</span>
                <span className="font-bold font-mono text-slate-800">Sentence-BERT (384-d)</span>
              </div>
              <div className="flex justify-between p-3 bg-slate-50 rounded-xl">
                <span className="text-slate-600 font-medium">Entity Extraction Model</span>
                <span className="font-bold font-mono text-slate-800">spaCy NLP + Regex + Matcher</span>
              </div>
              <div className="flex justify-between p-3 bg-slate-50 rounded-xl">
                <span className="text-slate-600 font-medium">Document Format Parsers</span>
                <span className="font-bold font-mono text-slate-800">PyMuPDF (fitz) + python-docx</span>
              </div>
              <div className="flex justify-between p-3 bg-slate-50 rounded-xl">
                <span className="text-slate-600 font-medium">Database Dual-Mode</span>
                <span className="font-bold font-mono text-slate-800">PostgreSQL / SQLite + MongoDB</span>
              </div>
            </div>
          </div>

          <div className="pt-2 text-[11px] text-slate-400 border-t border-slate-100">
            All similarity measurements run locally on Apple Silicon without third-party external APIs.
          </div>
        </div>
      </div>
    </div>
  );
}
