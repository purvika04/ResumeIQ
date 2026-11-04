import React, { useState, useEffect } from 'react';
import { useParams, useSearchParams, Link } from 'react-router-dom';
import { 
  ArrowLeft, 
  Mail, 
  Phone, 
  Linkedin, 
  Github, 
  MapPin, 
  Briefcase, 
  GraduationCap, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  FileText, 
  Quote, 
  Sparkles,
  Award,
  Layers
} from 'lucide-react';
import { 
  Radar, 
  RadarChart, 
  PolarGrid, 
  PolarAngleAxis, 
  PolarRadiusAxis, 
  ResponsiveContainer 
} from 'recharts';
import { getCandidate } from '../services/api';

export default function CandidateDetails() {
  const { id } = useParams();
  const [searchParams] = useSearchParams();
  const selectedJobId = searchParams.get('jobId');

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('evaluation'); // evaluation, history, raw_text

  useEffect(() => {
    fetchCandidate();
  }, [id]);

  const fetchCandidate = async () => {
    try {
      setLoading(true);
      const res = await getCandidate(id);
      setData(res.data);
      setError(null);
    } catch (err) {
      console.error(err);
      setError('Could not load candidate profile.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-4 border-brand-200 border-t-brand-600 rounded-full animate-spin"></div>
          <p className="text-sm text-slate-500">Loading comprehensive candidate profile...</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-8 text-center space-y-4">
        <p className="text-rose-600 font-semibold">{error || 'Candidate not found.'}</p>
        <Link to="/rankings" className="text-sm text-brand-600 font-bold hover:underline">
          ← Return to Rankings
        </Link>
      </div>
    );
  }

  const { candidate, parsed_document, raw_text, screening_history } = data;

  // Active screening result to display (either for selectedJobId or latest)
  let activeScreening = null;
  if (selectedJobId && screening_history?.length > 0) {
    activeScreening = screening_history.find((s) => s.job_id === selectedJobId);
  }
  if (!activeScreening && screening_history?.length > 0) {
    activeScreening = screening_history[0];
  }

  const radarData = activeScreening ? [
    { subject: 'Semantic Context', score: activeScreening.semantic_score, fullMark: 100 },
    { subject: 'Required Skills', score: activeScreening.required_skill_score, fullMark: 100 },
    { subject: 'Preferred Skills', score: activeScreening.preferred_skill_score, fullMark: 100 },
    { subject: 'Experience Fit', score: activeScreening.experience_score, fullMark: 100 },
  ] : [];

  return (
    <div className="space-y-8">
      {/* Back button & Title */}
      <div className="flex items-center justify-between">
        <Link
          to={selectedJobId ? `/rankings?jobId=${selectedJobId}` : '/rankings'}
          className="inline-flex items-center gap-2 text-xs font-semibold text-slate-500 hover:text-slate-900 bg-white px-3 py-2 rounded-xl border border-slate-200 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Rankings
        </Link>
        <div className="text-xs text-slate-400 font-mono">ID: {candidate.id.slice(0, 8)}</div>
      </div>

      {/* Candidate Header Profile Card */}
      <div className="bg-white rounded-2xl p-8 border border-slate-200/80 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="flex items-start gap-5">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-brand-600 to-indigo-600 text-white flex items-center justify-center font-extrabold text-2xl shadow-md shadow-brand-500/20 shrink-0">
            {candidate.name.charAt(0)}
          </div>
          <div className="space-y-1.5">
            <div className="flex items-center gap-3 flex-wrap">
              <h2 className="text-2xl font-bold text-slate-900 tracking-tight">{candidate.name}</h2>
              {activeScreening?.flagged_for_review && (
                <span className="inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-0.5 rounded-full bg-amber-50 text-amber-700 border border-amber-200">
                  <AlertTriangle className="w-3.5 h-3.5 text-amber-500" /> Human Review Advised
                </span>
              )}
            </div>
            <p className="text-sm font-semibold text-brand-600">{candidate.current_role || 'Software Engineer'}</p>

            <div className="flex flex-wrap items-center gap-4 text-xs text-slate-500 pt-1">
              {candidate.email && (
                <span className="flex items-center gap-1.5">
                  <Mail className="w-3.5 h-3.5 text-slate-400" /> {candidate.email}
                </span>
              )}
              {candidate.phone && (
                <span className="flex items-center gap-1.5">
                  <Phone className="w-3.5 h-3.5 text-slate-400" /> {candidate.phone}
                </span>
              )}
              {candidate.linkedin_url && (
                <a
                  href={candidate.linkedin_url}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center gap-1.5 text-brand-600 hover:underline"
                >
                  <Linkedin className="w-3.5 h-3.5" /> LinkedIn
                </a>
              )}
              {candidate.github_url && (
                <a
                  href={candidate.github_url}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center gap-1.5 text-slate-800 hover:underline"
                >
                  <Github className="w-3.5 h-3.5" /> GitHub
                </a>
              )}
            </div>
          </div>
        </div>

        {/* Overall Score Badge */}
        {activeScreening && (
          <div className="bg-slate-50 p-5 rounded-2xl border border-slate-200/80 flex flex-col items-center justify-center shrink-0 min-w-[150px]">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
              Compatibility Score
            </span>
            <span
              className={`text-4xl font-black mt-1 ${
                activeScreening.overall_score >= 80
                  ? 'text-emerald-600'
                  : activeScreening.overall_score >= 60
                  ? 'text-indigo-600'
                  : activeScreening.overall_score >= 40
                  ? 'text-amber-600'
                  : 'text-rose-600'
              }`}
            >
              {activeScreening.overall_score.toFixed(1)}%
            </span>
            <span className="text-[11px] font-medium text-slate-400 mt-0.5">
              Target: {activeScreening.job_title}
            </span>
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-200 gap-6 text-sm font-semibold text-slate-500">
        <button
          onClick={() => setActiveTab('evaluation')}
          className={`pb-3 transition-colors border-b-2 flex items-center gap-2 ${
            activeTab === 'evaluation'
              ? 'border-brand-600 text-brand-700 font-bold'
              : 'border-transparent hover:text-slate-800'
          }`}
        >
          <Sparkles className="w-4 h-4" /> AI Evaluation & Explainability
        </button>
        <button
          onClick={() => setActiveTab('resume_details')}
          className={`pb-3 transition-colors border-b-2 flex items-center gap-2 ${
            activeTab === 'resume_details'
              ? 'border-brand-600 text-brand-700 font-bold'
              : 'border-transparent hover:text-slate-800'
          }`}
        >
          <Briefcase className="w-4 h-4" /> Work History & Credentials
        </button>
        <button
          onClick={() => setActiveTab('raw_text')}
          className={`pb-3 transition-colors border-b-2 flex items-center gap-2 ${
            activeTab === 'raw_text'
              ? 'border-brand-600 text-brand-700 font-bold'
              : 'border-transparent hover:text-slate-800'
          }`}
        >
          <FileText className="w-4 h-4" /> Raw Resume Document
        </button>
      </div>

      {/* Tab 1: AI Evaluation & Explainability */}
      {activeTab === 'evaluation' && (
        <div className="space-y-6">
          {activeScreening ? (
            <>
              {/* Human-in-the-loop Advisory Banner */}
              <div className="bg-indigo-50/60 border border-indigo-100 rounded-2xl p-4 flex items-start gap-3 text-xs text-indigo-900 leading-relaxed">
                <Sparkles className="w-5 h-5 text-indigo-600 shrink-0 mt-0.5" />
                <div>
                  <span className="font-bold">Transparent Explainable AI (XAI): </span>
                  Scores indicate job-description alignment for recruiter evaluation, not general human intelligence or ability. Protected demographics are excluded from inference.
                </div>
              </div>

              {/* Score Breakdown & Radar Chart */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Radar Chart */}
                <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm flex flex-col items-center justify-center">
                  <h4 className="font-bold text-slate-800 text-sm mb-2 self-start">
                    Compatibility Dimension Breakdown
                  </h4>
                  <div className="w-full h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
                        <PolarGrid stroke="#e2e8f0" />
                        <PolarAngleAxis dataKey="subject" tick={{ fill: '#64748b', fontSize: 11 }} />
                        <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#cbd5e1" />
                        <Radar
                          name="Candidate"
                          dataKey="score"
                          stroke="#6366f1"
                          fill="#818cf8"
                          fillOpacity={0.5}
                        />
                      </RadarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Sub-Score Progress Bars */}
                <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm lg:col-span-2 space-y-5">
                  <h4 className="font-bold text-slate-800 text-sm">Component Score Breakdown</h4>

                  <div className="space-y-4">
                    {/* Semantic */}
                    <div className="space-y-1.5">
                      <div className="flex justify-between text-xs font-semibold">
                        <span className="text-slate-700">Semantic Similarity (Sentence-BERT all-MiniLM-L6-v2)</span>
                        <span className="text-indigo-600 font-mono font-bold">
                          {activeScreening.semantic_score.toFixed(1)}%
                        </span>
                      </div>
                      <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
                        <div
                          className="bg-indigo-600 h-2.5 rounded-full"
                          style={{ width: `${Math.min(100, activeScreening.semantic_score)}%` }}
                        ></div>
                      </div>
                      <p className="text-[11px] text-slate-400">
                        Contextual similarity between resume content and job description objectives.
                      </p>
                    </div>

                    {/* Required Skills */}
                    <div className="space-y-1.5">
                      <div className="flex justify-between text-xs font-semibold">
                        <span className="text-slate-700">Required Skills Coverage</span>
                        <span className="text-emerald-600 font-mono font-bold">
                          {activeScreening.required_skill_score.toFixed(1)}%
                        </span>
                      </div>
                      <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
                        <div
                          className="bg-emerald-500 h-2.5 rounded-full"
                          style={{ width: `${Math.min(100, activeScreening.required_skill_score)}%` }}
                        ></div>
                      </div>
                      <p className="text-[11px] text-slate-400">
                        Percentage of mandatory core technical skills verified in candidate resume.
                      </p>
                    </div>

                    {/* Preferred Skills */}
                    <div className="space-y-1.5">
                      <div className="flex justify-between text-xs font-semibold">
                        <span className="text-slate-700">Preferred / Bonus Qualifications</span>
                        <span className="text-violet-600 font-mono font-bold">
                          {activeScreening.preferred_skill_score.toFixed(1)}%
                        </span>
                      </div>
                      <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
                        <div
                          className="bg-violet-500 h-2.5 rounded-full"
                          style={{ width: `${Math.min(100, activeScreening.preferred_skill_score)}%` }}
                        ></div>
                      </div>
                    </div>

                    {/* Experience */}
                    <div className="space-y-1.5">
                      <div className="flex justify-between text-xs font-semibold">
                        <span className="text-slate-700">Relevant Experience Fit</span>
                        <span className="text-sky-600 font-mono font-bold">
                          {activeScreening.experience_score.toFixed(1)}%
                        </span>
                      </div>
                      <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
                        <div
                          className="bg-sky-500 h-2.5 rounded-full"
                          style={{ width: `${Math.min(100, activeScreening.experience_score)}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Natural Language Explanation Box */}
              <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm space-y-2">
                <h4 className="font-bold text-slate-800 text-sm flex items-center gap-2">
                  <Quote className="w-4 h-4 text-brand-600" />
                  Algorithm Evaluation Rationale
                </h4>
                <p className="text-xs text-slate-600 leading-relaxed font-normal bg-slate-50 p-4 rounded-xl border border-slate-200">
                  {activeScreening.explanation}
                </p>
              </div>

              {/* Matched vs Missing Skills */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Matched Skills */}
                <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm space-y-3">
                  <div className="flex items-center gap-2 text-emerald-700 font-bold text-sm">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                    <span>Matched Competencies ({activeScreening.matched_required_skills.length})</span>
                  </div>
                  <div className="flex flex-wrap gap-2 pt-1">
                    {activeScreening.matched_required_skills.map((s, idx) => (
                      <span
                        key={idx}
                        className="text-xs font-semibold px-2.5 py-1 rounded-lg bg-emerald-50 text-emerald-800 border border-emerald-200"
                      >
                        ✓ {s}
                      </span>
                    ))}
                    {activeScreening.matched_required_skills.length === 0 && (
                      <p className="text-xs text-slate-400 italic">No required competencies detected.</p>
                    )}
                  </div>
                </div>

                {/* Missing Skills */}
                <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm space-y-3">
                  <div className="flex items-center gap-2 text-rose-700 font-bold text-sm">
                    <XCircle className="w-4 h-4 text-rose-600" />
                    <span>Identified Skill Gaps ({activeScreening.missing_required_skills.length})</span>
                  </div>
                  <div className="flex flex-wrap gap-2 pt-1">
                    {activeScreening.missing_required_skills.map((s, idx) => (
                      <span
                        key={idx}
                        className="text-xs font-semibold px-2.5 py-1 rounded-lg bg-rose-50 text-rose-800 border border-rose-200"
                      >
                        ✕ {s}
                      </span>
                    ))}
                    {activeScreening.missing_required_skills.length === 0 && (
                      <p className="text-xs text-emerald-600 font-medium">All mandatory skills matched!</p>
                    )}
                  </div>
                </div>
              </div>

              {/* Evidence Snippets from Resume */}
              {activeScreening.evidence_snippets && Object.keys(activeScreening.evidence_snippets).length > 0 && (
                <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm space-y-3">
                  <h4 className="font-bold text-slate-800 text-sm flex items-center gap-2">
                    <FileText className="w-4 h-4 text-brand-600" />
                    Verifiable Evidence Snippets Extracted from Resume
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2">
                    {Object.entries(activeScreening.evidence_snippets).map(([skill, snippet], idx) => (
                      <div
                        key={idx}
                        className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 text-xs space-y-1.5"
                      >
                        <span className="font-bold text-brand-700 px-2 py-0.5 rounded bg-brand-50 border border-brand-200 inline-block text-[11px]">
                          {skill}
                        </span>
                        <p className="text-slate-600 italic">"{snippet}"</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="bg-white p-12 text-center rounded-2xl border border-slate-200 text-slate-400 text-sm">
              This candidate has not been screened against a job yet. Navigate to Job Descriptions or Candidate Rankings to run screening.
            </div>
          )}
        </div>
      )}

      {/* Tab 2: Work History & Credentials */}
      {activeTab === 'resume_details' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Work Experience */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm space-y-4">
            <h4 className="font-bold text-slate-800 text-sm flex items-center gap-2">
              <Briefcase className="w-4 h-4 text-brand-600" /> Work Experience Timeline
            </h4>

            {parsed_document?.work_experience && parsed_document.work_experience.length > 0 ? (
              <div className="space-y-4 border-l-2 border-brand-200 ml-2 pl-4">
                {parsed_document.work_experience.map((w, idx) => (
                  <div key={idx} className="space-y-1 relative">
                    <div className="w-2.5 h-2.5 bg-brand-600 rounded-full absolute -left-[21px] top-1"></div>
                    <p className="font-bold text-slate-900 text-sm">{w.title}</p>
                    <p className="text-xs font-semibold text-brand-600">{w.company || 'Company'}</p>
                    <p className="text-[11px] text-slate-400">{w.duration}</p>
                    {w.description && (
                      <p className="text-xs text-slate-600 pt-1 leading-relaxed">{w.description}</p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-400">No structured work experience parsed.</p>
            )}
          </div>

          {/* Education & Certifications */}
          <div className="space-y-6">
            {/* Education */}
            <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm space-y-4">
              <h4 className="font-bold text-slate-800 text-sm flex items-center gap-2">
                <GraduationCap className="w-4 h-4 text-brand-600" /> Academic Qualifications
              </h4>

              {parsed_document?.education && parsed_document.education.length > 0 ? (
                <div className="space-y-3">
                  {parsed_document.education.map((e, idx) => (
                    <div key={idx} className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs space-y-1">
                      <p className="font-bold text-slate-900">{e.degree}</p>
                      <p className="text-slate-600">{e.institution}</p>
                      {e.graduation_year && (
                        <p className="text-[11px] text-slate-400">Graduation: {e.graduation_year}</p>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-400">No education credentials detected.</p>
              )}
            </div>

            {/* Certifications */}
            <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm space-y-3">
              <h4 className="font-bold text-slate-800 text-sm flex items-center gap-2">
                <Award className="w-4 h-4 text-brand-600" /> Licenses & Certifications
              </h4>

              {parsed_document?.certifications && parsed_document.certifications.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {parsed_document.certifications.map((c, idx) => (
                    <span
                      key={idx}
                      className="text-xs font-semibold px-3 py-1 rounded-lg bg-indigo-50 text-indigo-800 border border-indigo-200"
                    >
                      {c}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-400">No industry certifications detected.</p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Tab 3: Raw Text */}
      {activeTab === 'raw_text' && (
        <div className="bg-slate-900 text-slate-200 p-6 rounded-2xl font-mono text-xs overflow-x-auto whitespace-pre-wrap leading-relaxed border border-slate-800 shadow-inner">
          {raw_text || 'No raw text stored.'}
        </div>
      )}
    </div>
  );
}
