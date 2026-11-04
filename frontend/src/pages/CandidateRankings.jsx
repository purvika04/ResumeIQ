import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { 
  Trophy, 
  Sparkles, 
  Filter, 
  Sliders, 
  Search, 
  AlertCircle, 
  CheckCircle2, 
  ArrowUpDown, 
  ChevronRight,
  TrendingUp,
  RotateCcw
} from 'lucide-react';
import { listJobs, getScreeningResults, runScreening } from '../services/api';

export default function CandidateRankings() {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();

  const [jobs, setJobs] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState(searchParams.get('jobId') || '');
  const [rankingsData, setRankingsData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [screening, setScreening] = useState(false);
  const [error, setError] = useState(null);

  // Filters & Sorting
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('score');
  const [sortOrder, setSortOrder] = useState('desc');
  const [minScore, setMinScore] = useState(0);
  const [flaggedOnly, setFlaggedOnly] = useState(false);

  // Custom Scoring Weights Drawer / Sliders
  const [showWeights, setShowWeights] = useState(false);
  const [weights, setWeights] = useState({
    weight_semantic: 0.40,
    weight_required_skills: 0.35,
    weight_preferred_skills: 0.15,
    weight_experience: 0.10,
  });

  useEffect(() => {
    loadJobs();
  }, []);

  useEffect(() => {
    if (selectedJobId) {
      loadResults(selectedJobId);
    }
  }, [selectedJobId, sortBy, sortOrder, minScore, flaggedOnly]);

  const loadJobs = async () => {
    try {
      const res = await listJobs();
      setJobs(res.data);
      if (res.data.length > 0 && !selectedJobId) {
        const firstId = res.data[0].id;
        setSelectedJobId(firstId);
        setSearchParams({ jobId: firstId });
      }
    } catch (err) {
      console.error(err);
      setError('Could not fetch jobs list.');
    }
  };

  const loadResults = async (jobId) => {
    try {
      setLoading(true);
      const res = await getScreeningResults(jobId, {
        sort_by: sortBy,
        sort_order: sortOrder,
        min_score: minScore,
        flagged_only: flaggedOnly,
      });
      setRankingsData(res.data);
      setError(null);
    } catch (err) {
      console.error(err);
      setError('Failed to fetch screening rankings.');
    } finally {
      setLoading(false);
    }
  };

  const handleJobChange = (e) => {
    const newId = e.target.value;
    setSelectedJobId(newId);
    setSearchParams({ jobId: newId });
  };

  const handleRunScreening = async () => {
    if (!selectedJobId) return;
    try {
      setScreening(true);
      const res = await runScreening({
        job_id: selectedJobId,
        weights: weights,
      });
      setRankingsData(res.data);
      setError(null);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Error running screening.');
    } finally {
      setScreening(false);
    }
  };

  const resetWeights = () => {
    setWeights({
      weight_semantic: 0.40,
      weight_required_skills: 0.35,
      weight_preferred_skills: 0.15,
      weight_experience: 0.10,
    });
  };

  // Filter candidates by search query
  const filteredCandidates = (rankingsData?.rankings || []).filter((c) => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    const matchesName = c.candidate_name.toLowerCase().includes(q);
    const matchesSkill = c.matched_required_skills.some(s => s.toLowerCase().includes(q));
    return matchesName || matchesSkill;
  });

  const getRankBadge = (rank) => {
    if (rank === 1) {
      return (
        <span className="w-7 h-7 rounded-full bg-amber-100 text-amber-800 border border-amber-300 font-extrabold text-xs flex items-center justify-center shadow-sm">
          🥇 1
        </span>
      );
    }
    if (rank === 2) {
      return (
        <span className="w-7 h-7 rounded-full bg-slate-200 text-slate-800 border border-slate-300 font-extrabold text-xs flex items-center justify-center shadow-sm">
          🥈 2
        </span>
      );
    }
    if (rank === 3) {
      return (
        <span className="w-7 h-7 rounded-full bg-orange-100 text-orange-800 border border-orange-300 font-extrabold text-xs flex items-center justify-center shadow-sm">
          🥉 3
        </span>
      );
    }
    return (
      <span className="w-7 h-7 rounded-full bg-slate-100 text-slate-600 font-bold text-xs flex items-center justify-center">
        #{rank}
      </span>
    );
  };

  return (
    <div className="space-y-8">
      {/* Header & Job Selector */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Candidate Rankings</h2>
          <p className="text-sm text-slate-500 mt-1">
            Automated multi-factor evaluation combining Sentence-BERT semantic similarity with strict skill constraints.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Job Dropdown */}
          <select
            value={selectedJobId}
            onChange={handleJobChange}
            className="px-3.5 py-2.5 rounded-xl border border-slate-300 bg-white text-sm font-semibold text-slate-800 shadow-sm focus:outline-none focus:ring-2 focus:ring-brand-500 min-w-[240px]"
          >
            {jobs.map((j) => (
              <option key={j.id} value={j.id}>
                {j.title} ({j.department})
              </option>
            ))}
          </select>

          {/* Toggle Scoring Weights */}
          <button
            onClick={() => setShowWeights(!showWeights)}
            className={`inline-flex items-center gap-2 px-3.5 py-2.5 rounded-xl text-xs font-semibold border transition-all ${
              showWeights
                ? 'bg-brand-50 border-brand-200 text-brand-700'
                : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50'
            }`}
          >
            <Sliders className="w-4 h-4" />
            Scoring Weights
          </button>

          {/* Run Screening Action */}
          <button
            onClick={handleRunScreening}
            disabled={screening || !selectedJobId}
            className="inline-flex items-center gap-2 px-4 py-2.5 bg-brand-600 hover:bg-brand-700 disabled:bg-slate-300 text-white font-semibold text-xs rounded-xl shadow-md transition-all"
          >
            <Sparkles className={`w-4 h-4 ${screening ? 'animate-spin' : ''}`} />
            {screening ? 'Evaluating with S-BERT...' : 'Re-Run AI Screening'}
          </button>
        </div>
      </div>

      {/* Configurable Weights Drawer */}
      {showWeights && (
        <div className="bg-white rounded-2xl p-6 border border-brand-100 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-bold text-slate-900 text-sm">Fine-Tune Hybrid Ranking Weights</h3>
              <p className="text-xs text-slate-500">
                Formula: Final Score = w₁·Semantic + w₂·ReqSkills + w₃·PrefSkills + w₄·Experience
              </p>
            </div>
            <button
              onClick={resetWeights}
              className="text-xs font-medium text-slate-500 hover:text-brand-600 flex items-center gap-1"
            >
              <RotateCcw className="w-3.5 h-3.5" /> Reset Defaults
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 pt-2">
            <div>
              <div className="flex justify-between text-xs font-semibold mb-1.5">
                <span className="text-slate-700">Semantic Similarity</span>
                <span className="text-brand-600 font-mono">{(weights.weight_semantic * 100).toFixed(0)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={weights.weight_semantic}
                onChange={(e) => setWeights({ ...weights, weight_semantic: parseFloat(e.target.value) })}
                className="w-full accent-brand-600"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs font-semibold mb-1.5">
                <span className="text-slate-700">Required Core Skills</span>
                <span className="text-brand-600 font-mono">{(weights.weight_required_skills * 100).toFixed(0)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={weights.weight_required_skills}
                onChange={(e) => setWeights({ ...weights, weight_required_skills: parseFloat(e.target.value) })}
                className="w-full accent-brand-600"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs font-semibold mb-1.5">
                <span className="text-slate-700">Preferred / Bonus Skills</span>
                <span className="text-brand-600 font-mono">{(weights.weight_preferred_skills * 100).toFixed(0)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={weights.weight_preferred_skills}
                onChange={(e) => setWeights({ ...weights, weight_preferred_skills: parseFloat(e.target.value) })}
                className="w-full accent-brand-600"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs font-semibold mb-1.5">
                <span className="text-slate-700">Relevant Experience</span>
                <span className="text-brand-600 font-mono">{(weights.weight_experience * 100).toFixed(0)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={weights.weight_experience}
                onChange={(e) => setWeights({ ...weights, weight_experience: parseFloat(e.target.value) })}
                className="w-full accent-brand-600"
              />
            </div>
          </div>
        </div>
      )}

      {/* Summary Stats Banner */}
      {rankingsData && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase">Screened Candidates</p>
              <p className="text-2xl font-bold text-slate-900 mt-1">{rankingsData.total_screened}</p>
            </div>
            <div className="p-3 bg-brand-50 rounded-xl text-brand-600">
              <Trophy className="w-5 h-5" />
            </div>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase">Average Compatibility</p>
              <p className="text-2xl font-bold text-slate-900 mt-1">{rankingsData.average_score}%</p>
            </div>
            <div className="p-3 bg-indigo-50 rounded-xl text-indigo-600">
              <TrendingUp className="w-5 h-5" />
            </div>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase">Top Match Score</p>
              <p className="text-2xl font-bold text-emerald-600 mt-1">{rankingsData.highest_score}%</p>
            </div>
            <div className="p-3 bg-emerald-50 rounded-xl text-emerald-600">
              <Sparkles className="w-5 h-5" />
            </div>
          </div>
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-sm flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-2 flex-1 min-w-[200px]">
          <Search className="w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search candidate name or skill..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full text-xs text-slate-800 placeholder-slate-400 focus:outline-none"
          />
        </div>

        <div className="flex flex-wrap items-center gap-4 text-xs">
          {/* Min Score Filter */}
          <div className="flex items-center gap-2">
            <span className="text-slate-500 font-medium">Min Score:</span>
            <input
              type="range"
              min="0"
              max="90"
              step="10"
              value={minScore}
              onChange={(e) => setMinScore(parseFloat(e.target.value))}
              className="w-20 accent-brand-600"
            />
            <span className="font-semibold text-slate-700 w-8">{minScore}%</span>
          </div>

          {/* Flagged Only Toggle */}
          <label className="flex items-center gap-1.5 cursor-pointer font-medium text-slate-600">
            <input
              type="checkbox"
              checked={flaggedOnly}
              onChange={(e) => setFlaggedOnly(e.target.checked)}
              className="rounded text-brand-600 focus:ring-brand-500"
            />
            <span>Review Flagged Only</span>
          </label>

          {/* Sort Selector */}
          <div className="flex items-center gap-1.5 pl-2 border-l border-slate-200">
            <span className="text-slate-500 font-medium">Sort:</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="bg-transparent font-semibold text-slate-700 focus:outline-none cursor-pointer"
            >
              <option value="score">Final Score</option>
              <option value="semantic">Semantic Similarity</option>
              <option value="required_skills">Required Skills</option>
              <option value="experience">Experience</option>
            </select>
          </div>
        </div>
      </div>

      {/* Ranked Candidate Table */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          {filteredCandidates.length > 0 ? (
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 text-slate-600 text-xs font-semibold uppercase tracking-wider">
                <tr>
                  <th className="py-4 px-6">Rank</th>
                  <th className="py-4 px-6">Candidate Details</th>
                  <th className="py-4 px-6">Match Compatibility</th>
                  <th className="py-4 px-6">Required Skills Matched</th>
                  <th className="py-4 px-6">Skill Gaps</th>
                  <th className="py-4 px-6">Review Status</th>
                  <th className="py-4 px-6 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredCandidates.map((cand) => (
                  <tr
                    key={cand.candidate_id}
                    className="hover:bg-slate-50/80 transition-colors group"
                  >
                    <td className="py-4 px-6 font-semibold">
                      {getRankBadge(cand.rank)}
                    </td>

                    <td className="py-4 px-6">
                      <div>
                        <p className="font-bold text-slate-900 group-hover:text-brand-600 transition-colors">
                          {cand.candidate_name}
                        </p>
                        <p className="text-xs text-slate-500">{cand.current_role || 'Software Engineer'}</p>
                        <p className="text-[11px] text-slate-400">{cand.total_experience_years} years experience</p>
                      </div>
                    </td>

                    <td className="py-4 px-6">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span
                            className={`font-black text-sm ${
                              cand.overall_score >= 80
                                ? 'text-emerald-600'
                                : cand.overall_score >= 60
                                ? 'text-indigo-600'
                                : cand.overall_score >= 40
                                ? 'text-amber-600'
                                : 'text-rose-600'
                            }`}
                          >
                            {cand.overall_score.toFixed(1)}%
                          </span>
                          <span className="text-[10px] text-slate-400">
                            (S-BERT: {cand.semantic_score.toFixed(0)}%)
                          </span>
                        </div>
                        <div className="w-28 bg-slate-100 rounded-full h-2 overflow-hidden">
                          <div
                            className={`h-full rounded-full ${
                              cand.overall_score >= 80
                                ? 'bg-emerald-500'
                                : cand.overall_score >= 60
                                ? 'bg-indigo-500'
                                : cand.overall_score >= 40
                                ? 'bg-amber-500'
                                : 'bg-rose-500'
                            }`}
                            style={{ width: `${Math.min(100, cand.overall_score)}%` }}
                          ></div>
                        </div>
                      </div>
                    </td>

                    <td className="py-4 px-6">
                      <div className="flex flex-wrap gap-1 max-w-xs">
                        {cand.matched_required_skills.slice(0, 4).map((s, idx) => (
                          <span
                            key={idx}
                            className="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-700 border border-emerald-200"
                          >
                            ✓ {s}
                          </span>
                        ))}
                        {cand.matched_required_skills.length === 0 && (
                          <span className="text-xs text-slate-400 italic">None matched</span>
                        )}
                        {cand.matched_required_skills.length > 4 && (
                          <span className="text-[10px] text-slate-400 self-center">
                            +{cand.matched_required_skills.length - 4}
                          </span>
                        )}
                      </div>
                    </td>

                    <td className="py-4 px-6">
                      <div className="flex flex-wrap gap-1 max-w-xs">
                        {cand.missing_required_skills.slice(0, 3).map((s, idx) => (
                          <span
                            key={idx}
                            className="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-rose-50 text-rose-700 border border-rose-200"
                          >
                            ✕ {s}
                          </span>
                        ))}
                        {cand.missing_required_skills.length === 0 && (
                          <span className="text-xs text-emerald-600 font-medium">None (All Met)</span>
                        )}
                      </div>
                    </td>

                    <td className="py-4 px-6">
                      {cand.flagged_for_review ? (
                        <div className="flex items-center gap-1.5" title={cand.flag_reason || 'Manual review required'}>
                          <span className="inline-flex items-center gap-1 text-[11px] font-semibold px-2.5 py-1 rounded-full bg-amber-50 text-amber-700 border border-amber-200">
                            <AlertCircle className="w-3.5 h-3.5 text-amber-500" /> Human Review
                          </span>
                        </div>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-[11px] font-semibold px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" /> Screened
                        </span>
                      )}
                    </td>

                    <td className="py-4 px-6 text-right">
                      <button
                        onClick={() => navigate(`/candidates/${cand.candidate_id}?jobId=${selectedJobId}`)}
                        className="inline-flex items-center gap-1 text-xs font-semibold px-3 py-1.5 rounded-xl bg-brand-50 hover:bg-brand-100 text-brand-700 transition-colors"
                      >
                        Inspect Profile <ChevronRight className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="p-12 text-center text-slate-400 text-sm">
              {loading ? (
                <div className="flex flex-col items-center gap-2">
                  <div className="w-6 h-6 border-2 border-brand-500 border-t-transparent rounded-full animate-spin"></div>
                  <p>Calculating semantic embeddings and rankings...</p>
                </div>
              ) : (
                'No candidates ranked for this job yet. Click "Re-Run AI Screening" to analyze available resumes.'
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
