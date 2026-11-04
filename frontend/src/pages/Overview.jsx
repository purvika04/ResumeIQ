import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  FileText, 
  Users, 
  Briefcase, 
  TrendingUp, 
  UploadCloud, 
  PlusCircle, 
  ArrowRight,
  Sparkles,
  AlertCircle,
  CheckCircle2
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Cell 
} from 'recharts';
import { getAnalyticsOverview } from '../services/api';

export default function Overview() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchOverview();
  }, []);

  const fetchOverview = async () => {
    try {
      setLoading(true);
      const res = await getAnalyticsOverview();
      setData(res.data);
      setError(null);
    } catch (err) {
      console.error(err);
      setError('Failed to load analytics overview. Make sure the backend server is running.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-4 border-brand-200 border-t-brand-600 rounded-full animate-spin"></div>
          <p className="text-sm text-slate-500">Loading intelligence dashboard...</p>
        </div>
      </div>
    );
  }

  const statCards = [
    {
      title: 'Resumes Analyzed',
      value: data?.total_resumes || 0,
      icon: FileText,
      color: 'text-indigo-600',
      bg: 'bg-indigo-50 border-indigo-100',
      change: '+100% genuine NLP parse',
    },
    {
      title: 'Active Candidates',
      value: data?.total_candidates || 0,
      icon: Users,
      color: 'text-violet-600',
      bg: 'bg-violet-50 border-violet-100',
      change: 'Extracted skills & history',
    },
    {
      title: 'Active Job Openings',
      value: data?.active_jobs || 0,
      icon: Briefcase,
      color: 'text-sky-600',
      bg: 'bg-sky-50 border-sky-100',
      change: 'Configured requirements',
    },
    {
      title: 'Avg. Match Score',
      value: `${data?.average_score || 0}%`,
      icon: TrendingUp,
      color: 'text-emerald-600',
      bg: 'bg-emerald-50 border-emerald-100',
      change: 'Hybrid AI/ML compatibility',
    },
  ];

  const distributionColors = ['#94a3b8', '#64748b', '#6366f1', '#4f46e5', '#10b981'];

  return (
    <div className="space-y-8">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-brand-900 via-indigo-900 to-slate-900 text-white rounded-2xl p-8 shadow-xl relative overflow-hidden">
        <div className="relative z-10 max-w-2xl space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 text-white text-xs font-semibold backdrop-blur-sm border border-white/10">
            <Sparkles className="w-3.5 h-3.5 text-brand-300" />
            <span>Powered by Sentence-BERT & spaCy NLP</span>
          </div>
          <h2 className="text-3xl font-extrabold tracking-tight">
            AI-Powered Resume Screening & Candidate Ranking
          </h2>
          <p className="text-slate-300 text-sm leading-relaxed">
            Welcome to ResumeIQ. Upload batches of resumes, define granular job competencies, and leverage semantic embeddings to instantly rank candidates with transparent, explainable evidence.
          </p>

          <div className="flex flex-wrap gap-3 pt-2">
            <Link
              to="/upload"
              className="inline-flex items-center gap-2 px-4 py-2.5 bg-brand-500 hover:bg-brand-600 text-white font-medium text-xs rounded-xl shadow-md transition-all"
            >
              <UploadCloud className="w-4 h-4" />
              Upload Resumes
            </Link>
            <Link
              to="/jobs"
              className="inline-flex items-center gap-2 px-4 py-2.5 bg-white/10 hover:bg-white/20 text-white font-medium text-xs rounded-xl backdrop-blur-sm border border-white/20 transition-all"
            >
              <PlusCircle className="w-4 h-4" />
              Create Job Posting
            </Link>
          </div>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {statCards.map((stat, i) => {
          const Icon = stat.icon;
          return (
            <div
              key={i}
              className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-500 tracking-wide uppercase">
                  {stat.title}
                </span>
                <div className={`p-2.5 rounded-xl border ${stat.bg}`}>
                  <Icon className={`w-5 h-5 ${stat.color}`} />
                </div>
              </div>
              <div className="mt-4">
                <p className="text-3xl font-bold text-slate-900 tracking-tight">{stat.value}</p>
                <p className="mt-1 text-xs text-slate-400 font-medium">{stat.change}</p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Score Distribution Chart */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-bold text-slate-800 text-base">Candidate Score Distribution</h3>
              <p className="text-xs text-slate-400">Multi-factor hybrid compatibility spread</p>
            </div>
            <span className="text-xs font-medium px-2.5 py-1 bg-slate-100 text-slate-600 rounded-lg">
              {data?.total_screenings || 0} Total Screens
            </span>
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
                    itemStyle={{ color: '#818cf8' }}
                  />
                  <Bar dataKey="count" radius={[6, 6, 0, 0]} name="Candidates">
                    {data.score_distribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={distributionColors[index % distributionColors.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-slate-400 text-sm">
                No screening data yet. Upload resumes and run screening.
              </div>
            )}
          </div>
        </div>

        {/* Top Demanded Skills Chart */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-bold text-slate-800 text-base">Most Demanded Skills</h3>
              <p className="text-xs text-slate-400">Extracted from active job requirements</p>
            </div>
            <span className="text-xs font-medium px-2.5 py-1 bg-brand-50 text-brand-600 rounded-lg">
              NLP Taxonomy
            </span>
          </div>

          <div className="h-64 w-full">
            {data?.top_demanded_skills && data.top_demanded_skills.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.top_demanded_skills.slice(0, 6)} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis type="number" tick={{ fill: '#64748b', fontSize: 12 }} allowDecimals={false} />
                  <YAxis type="category" dataKey="skill" tick={{ fill: '#64748b', fontSize: 12 }} width={90} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#1e293b', borderRadius: '8px', color: '#fff', border: 'none' }}
                  />
                  <Bar dataKey="count" fill="#6366f1" radius={[0, 6, 6, 0]} name="Job Postings" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-slate-400 text-sm">
                No job postings created yet. Create jobs to see skill demands.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Recent Screening Activity */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden">
        <div className="p-6 border-b border-slate-200 flex items-center justify-between">
          <div>
            <h3 className="font-bold text-slate-800 text-base">Recent Screening Activity</h3>
            <p className="text-xs text-slate-400">Latest candidate evaluation records</p>
          </div>
          <Link
            to="/rankings"
            className="text-xs font-semibold text-brand-600 hover:text-brand-700 flex items-center gap-1"
          >
            View all rankings <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="overflow-x-auto">
          {data?.recent_screenings && data.recent_screenings.length > 0 ? (
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 text-slate-600 text-xs font-semibold uppercase tracking-wider">
                <tr>
                  <th className="py-3.5 px-6">Candidate</th>
                  <th className="py-3.5 px-6">Target Role</th>
                  <th className="py-3.5 px-6">Compatibility Score</th>
                  <th className="py-3.5 px-6">Review Status</th>
                  <th className="py-3.5 px-6 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {data.recent_screenings.map((item, idx) => (
                  <tr key={idx} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-4 px-6 font-semibold text-slate-900">
                      {item.candidate_name}
                    </td>
                    <td className="py-4 px-6 text-slate-600">
                      {item.job_title}
                    </td>
                    <td className="py-4 px-6">
                      <div className="flex items-center gap-3">
                        <div className="w-24 bg-slate-100 rounded-full h-2 overflow-hidden">
                          <div
                            className={`h-full rounded-full ${
                              item.overall_score >= 80
                                ? 'bg-emerald-500'
                                : item.overall_score >= 60
                                ? 'bg-indigo-500'
                                : item.overall_score >= 40
                                ? 'bg-amber-500'
                                : 'bg-rose-500'
                            }`}
                            style={{ width: `${Math.min(100, item.overall_score)}%` }}
                          ></div>
                        </div>
                        <span className="font-bold text-xs text-slate-700">
                          {item.overall_score.toFixed(1)}%
                        </span>
                      </div>
                    </td>
                    <td className="py-4 px-6">
                      {item.flagged ? (
                        <span className="inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full bg-amber-50 text-amber-700 border border-amber-200">
                          <AlertCircle className="w-3 h-3 text-amber-500" /> Review Flagged
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
                          <CheckCircle2 className="w-3 h-3 text-emerald-500" /> Verified Match
                        </span>
                      )}
                    </td>
                    <td className="py-4 px-6 text-right">
                      <Link
                        to={`/candidates/${item.candidate_id}`}
                        className="text-xs font-semibold text-brand-600 hover:text-brand-800"
                      >
                        Inspect Profile →
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="p-8 text-center text-slate-400 text-sm">
              No recent screenings recorded yet. Upload resumes and screen against jobs to populate this table.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
