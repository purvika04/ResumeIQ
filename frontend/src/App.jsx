import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';
import Overview from './pages/Overview';
import UploadResumes from './pages/UploadResumes';
import JobDescriptions from './pages/JobDescriptions';
import CandidateRankings from './pages/CandidateRankings';
import CandidateDetails from './pages/CandidateDetails';
import Analytics from './pages/Analytics';
import { checkHealth } from './services/api';

export default function App() {
  const [health, setHealth] = useState(null);

  useEffect(() => {
    checkHealth()
      .then((res) => setHealth(res.data))
      .catch((err) => console.log('Backend not connected yet:', err.message));
  }, []);

  return (
    <BrowserRouter>
      <div className="flex min-h-screen bg-slate-50 font-['Plus_Jakarta_Sans',sans-serif]">
        {/* Navigation Sidebar */}
        <Sidebar health={health} />

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col min-w-0">
          <Navbar health={health} />

          <main className="flex-1 p-8 max-w-7xl w-full mx-auto">
            <Routes>
              <Route path="/" element={<Overview />} />
              <Route path="/upload" element={<UploadResumes />} />
              <Route path="/jobs" element={<JobDescriptions />} />
              <Route path="/rankings" element={<CandidateRankings />} />
              <Route path="/candidates/:id" element={<CandidateDetails />} />
              <Route path="/analytics" element={<Analytics />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  );
}
