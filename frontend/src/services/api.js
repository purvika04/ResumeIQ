import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 60000,
});

export const checkHealth = () => api.get('/health');

export const getAnalyticsOverview = () => api.get('/analytics/overview');

export const listResumes = () => api.get('/resumes');
export const getResume = (id) => api.get(`/resumes/${id}`);
export const deleteResume = (id) => api.delete(`/resumes/${id}`);
export const uploadResumes = (formData, onProgress) => {
  return api.post('/resumes/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onProgress(percent);
      }
    },
  });
};

export const listJobs = () => api.get('/jobs');
export const getJob = (id) => api.get(`/jobs/${id}`);
export const createJob = (data) => api.post('/jobs', data);
export const updateJob = (id, data) => api.put(`/jobs/${id}`, data);
export const deleteJob = (id) => api.delete(`/jobs/${id}`);

export const runScreening = (data) => api.post('/screening/run', data);
export const getScreeningResults = (jobId, params) => api.get(`/screening/results/${jobId}`, { params });

export const listCandidates = () => api.get('/candidates');
export const getCandidate = (id) => api.get(`/candidates/${id}`);

export default api;
