import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Briefcase, 
  PlusCircle, 
  MapPin, 
  Clock, 
  Trash2, 
  Edit3, 
  Sparkles, 
  X, 
  Check, 
  Users,
  Search
} from 'lucide-react';
import { listJobs, createJob, updateJob, deleteJob } from '../services/api';

export default function JobDescriptions() {
  const navigate = useNavigate();
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [editingJob, setEditingJob] = useState(null);

  // Form State
  const [title, setTitle] = useState('');
  const [department, setDepartment] = useState('Engineering');
  const [location, setLocation] = useState('Remote');
  const [employmentType, setEmploymentType] = useState('Full-time');
  const [minExperience, setMinExperience] = useState(3.0);
  const [description, setDescription] = useState('');
  const [requiredSkills, setRequiredSkills] = useState([]);
  const [preferredSkills, setPreferredSkills] = useState([]);
  const [reqInput, setReqInput] = useState('');
  const [prefInput, setPrefInput] = useState('');

  useEffect(() => {
    fetchJobs();
  }, []);

  const fetchJobs = async () => {
    try {
      setLoading(true);
      const res = await listJobs();
      setJobs(res.data);
      setError(null);
    } catch (err) {
      console.error(err);
      setError('Could not load jobs.');
    } finally {
      setLoading(false);
    }
  };

  const openCreateModal = () => {
    setEditingJob(null);
    setTitle('');
    setDepartment('Engineering');
    setLocation('Remote');
    setEmploymentType('Full-time');
    setMinExperience(3.0);
    setDescription('');
    setRequiredSkills(['Python', 'FastAPI', 'PostgreSQL']);
    setPreferredSkills(['Docker', 'AWS']);
    setShowModal(true);
  };

  const openEditModal = (job) => {
    setEditingJob(job);
    setTitle(job.title);
    setDepartment(job.department || 'Engineering');
    setLocation(job.location || 'Remote');
    setEmploymentType(job.employment_type || 'Full-time');
    setMinExperience(job.min_experience_years || 0);
    setDescription(job.description);
    setRequiredSkills(job.required_skills || []);
    setPreferredSkills(job.preferred_skills || []);
    setShowModal(true);
  };

  const handleAddReqSkill = (e) => {
    if ((e.key === 'Enter' || e.key === ',') && reqInput.trim()) {
      e.preventDefault();
      const val = reqInput.trim().replace(/^,|,$/g, '');
      if (val && !requiredSkills.includes(val)) {
        setRequiredSkills([...requiredSkills, val]);
      }
      setReqInput('');
    }
  };

  const removeReqSkill = (skillToRemove) => {
    setRequiredSkills(requiredSkills.filter(s => s !== skillToRemove));
  };

  const handleAddPrefSkill = (e) => {
    if ((e.key === 'Enter' || e.key === ',') && prefInput.trim()) {
      e.preventDefault();
      const val = prefInput.trim().replace(/^,|,$/g, '');
      if (val && !preferredSkills.includes(val)) {
        setPreferredSkills([...preferredSkills, val]);
      }
      setPrefInput('');
    }
  };

  const removePrefSkill = (skillToRemove) => {
    setPreferredSkills(preferredSkills.filter(s => s !== skillToRemove));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title.trim() || !description.trim()) {
      alert('Please fill in title and description.');
      return;
    }

    const payload = {
      title,
      department,
      location,
      employment_type: employmentType,
      min_experience_years: parseFloat(minExperience) || 0,
      description,
      required_skills: requiredSkills,
      preferred_skills: preferredSkills,
    };

    try {
      if (editingJob) {
        await updateJob(editingJob.id, payload);
      } else {
        await createJob(payload);
      }
      setShowModal(false);
      fetchJobs();
    } catch (err) {
      console.error(err);
      alert('Failed to save job posting.');
    }
  };

  const handleDelete = async (jobId) => {
    if (!window.confirm('Are you sure you want to delete this job posting?')) return;
    try {
      await deleteJob(jobId);
      setJobs(jobs.filter(j => j.id !== jobId));
    } catch (err) {
      console.error(err);
      alert('Error deleting job posting.');
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Job Descriptions</h2>
          <p className="text-sm text-slate-500 mt-1">
            Define requirements, competencies, and experience thresholds used by the Sentence-BERT matcher.
          </p>
        </div>
        <button
          onClick={openCreateModal}
          className="inline-flex items-center gap-2 px-4 py-2.5 bg-brand-600 hover:bg-brand-700 text-white font-medium text-sm rounded-xl shadow-md transition-all self-start sm:self-auto"
        >
          <PlusCircle className="w-4 h-4" />
          Create New Job
        </button>
      </div>

      {/* Job Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {jobs.map((job) => (
          <div
            key={job.id}
            className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm hover:shadow-md transition-all flex flex-col justify-between space-y-4"
          >
            <div className="space-y-3">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <span className="text-[11px] font-bold uppercase tracking-wider text-brand-600 bg-brand-50 px-2 py-0.5 rounded-full border border-brand-100">
                    {job.department || 'Engineering'}
                  </span>
                  <h3 className="font-bold text-slate-900 text-lg mt-1">{job.title}</h3>
                </div>
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => openEditModal(job)}
                    className="p-1 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100"
                  >
                    <Edit3 className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(job.id)}
                    className="p-1 text-slate-400 hover:text-rose-600 rounded-lg hover:bg-rose-50"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>

              <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500 font-medium">
                <span className="flex items-center gap-1">
                  <MapPin className="w-3.5 h-3.5" /> {job.location || 'Remote'}
                </span>
                <span className="flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5" /> {job.min_experience_years}+ yrs exp
                </span>
                <span className="flex items-center gap-1 text-indigo-600 font-semibold">
                  <Users className="w-3.5 h-3.5" /> {job.candidate_count} screened
                </span>
              </div>

              <p className="text-xs text-slate-600 line-clamp-3 leading-relaxed">
                {job.description}
              </p>

              {/* Skills Tags */}
              <div className="space-y-1.5 pt-2">
                <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-wide">
                  Required Core Skills
                </p>
                <div className="flex flex-wrap gap-1">
                  {job.required_skills?.map((s, i) => (
                    <span
                      key={i}
                      className="text-[11px] font-medium px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-700 border border-emerald-100"
                    >
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Bottom Screen Button */}
            <div className="pt-4 border-t border-slate-100">
              <button
                onClick={() => navigate(`/rankings?jobId=${job.id}`)}
                className="w-full inline-flex items-center justify-center gap-2 px-4 py-2 bg-slate-900 hover:bg-brand-600 text-white font-medium text-xs rounded-xl shadow-sm transition-all"
              >
                <Sparkles className="w-3.5 h-3.5 text-brand-300" />
                Screen & Rank Candidates
              </button>
            </div>
          </div>
        ))}

        {jobs.length === 0 && !loading && (
          <div className="col-span-full bg-white rounded-2xl p-12 text-center border border-slate-200">
            <Briefcase className="w-12 h-12 text-slate-300 mx-auto mb-3" />
            <h3 className="font-bold text-slate-800 text-base">No job postings created yet</h3>
            <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
              Create your first job posting to start matching candidate resumes using Sentence-BERT.
            </p>
            <button
              onClick={openCreateModal}
              className="mt-4 px-4 py-2 bg-brand-600 text-white text-xs font-semibold rounded-xl"
            >
              Create Job Posting
            </button>
          </div>
        )}
      </div>

      {/* Create / Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] flex flex-col shadow-2xl border border-slate-200">
            <div className="p-6 border-b border-slate-200 flex items-center justify-between">
              <h3 className="font-bold text-slate-900 text-lg">
                {editingJob ? 'Edit Job Description' : 'Create New Job Description'}
              </h3>
              <button
                onClick={() => setShowModal(false)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-6 overflow-y-auto space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wide mb-1">
                  Job Title *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Senior Full Stack Engineer"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wide mb-1">
                    Department
                  </label>
                  <input
                    type="text"
                    value={department}
                    onChange={(e) => setDepartment(e.target.value)}
                    className="w-full px-3.5 py-2 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wide mb-1">
                    Location
                  </label>
                  <input
                    type="text"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    className="w-full px-3.5 py-2 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wide mb-1">
                    Min. Exp (Years)
                  </label>
                  <input
                    type="number"
                    step="0.5"
                    min="0"
                    value={minExperience}
                    onChange={(e) => setMinExperience(e.target.value)}
                    className="w-full px-3.5 py-2 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wide mb-1">
                  Required Core Skills (Press Enter or comma to add)
                </label>
                <div className="flex flex-wrap gap-1.5 p-2 rounded-xl border border-slate-300 bg-slate-50 min-h-[44px]">
                  {requiredSkills.map((sk, idx) => (
                    <span
                      key={idx}
                      className="inline-flex items-center gap-1 text-xs font-semibold px-2 py-1 rounded-md bg-emerald-100 text-emerald-800"
                    >
                      {sk}
                      <button type="button" onClick={() => removeReqSkill(sk)}>
                        <X className="w-3 h-3 hover:text-emerald-950" />
                      </button>
                    </span>
                  ))}
                  <input
                    type="text"
                    value={reqInput}
                    onChange={(e) => setReqInput(e.target.value)}
                    onKeyDown={handleAddReqSkill}
                    placeholder="Type skill & press Enter..."
                    className="bg-transparent border-none text-xs focus:outline-none flex-1 min-w-[120px]"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wide mb-1">
                  Preferred / Bonus Skills
                </label>
                <div className="flex flex-wrap gap-1.5 p-2 rounded-xl border border-slate-300 bg-slate-50 min-h-[44px]">
                  {preferredSkills.map((sk, idx) => (
                    <span
                      key={idx}
                      className="inline-flex items-center gap-1 text-xs font-semibold px-2 py-1 rounded-md bg-indigo-100 text-indigo-800"
                    >
                      {sk}
                      <button type="button" onClick={() => removePrefSkill(sk)}>
                        <X className="w-3 h-3 hover:text-indigo-950" />
                      </button>
                    </span>
                  ))}
                  <input
                    type="text"
                    value={prefInput}
                    onChange={(e) => setPrefInput(e.target.value)}
                    onKeyDown={handleAddPrefSkill}
                    placeholder="Type skill & press Enter..."
                    className="bg-transparent border-none text-xs focus:outline-none flex-1 min-w-[120px]"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wide mb-1">
                  Full Job Description *
                </label>
                <textarea
                  rows={6}
                  required
                  placeholder="Detail the responsibilities, technical expectations, architecture requirements, and day-to-day deliverables..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full p-3.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm leading-relaxed"
                ></textarea>
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 rounded-xl text-slate-600 hover:bg-slate-100 text-xs font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-brand-600 hover:bg-brand-700 text-white rounded-xl text-xs font-semibold shadow-md"
                >
                  Save Job Posting
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
