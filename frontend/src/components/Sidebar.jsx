import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  UploadCloud, 
  Briefcase, 
  Trophy, 
  BarChart3, 
  Sparkles,
  Cpu,
  Database
} from 'lucide-react';

export default function Sidebar({ health }) {
  const navItems = [
    { name: 'Overview', path: '/', icon: LayoutDashboard },
    { name: 'Upload Resumes', path: '/upload', icon: UploadCloud },
    { name: 'Job Postings', path: '/jobs', icon: Briefcase },
    { name: 'Candidate Rankings', path: '/rankings', icon: Trophy },
    { name: 'Analytics', path: '/analytics', icon: BarChart3 },
  ];

  return (
    <aside className="w-64 bg-white border-r border-slate-200 min-h-screen flex flex-col shrink-0">
      {/* Brand Logo */}
      <div className="h-16 flex items-center px-6 border-b border-slate-200 gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-500 flex items-center justify-center text-white shadow-md shadow-brand-500/20">
          <Sparkles className="w-5 h-5" />
        </div>
        <div>
          <div className="flex items-center gap-1.5">
            <span className="font-bold text-lg text-slate-900 tracking-tight">ResumeIQ</span>
            <span className="text-[10px] font-bold uppercase tracking-wider bg-brand-50 text-brand-600 px-1.5 py-0.5 rounded-full border border-brand-200">
              AI
            </span>
          </div>
          <p className="text-xs text-slate-500">Recruitment Intelligence</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="p-4 space-y-1.5 flex-1">
        <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-600 px-3 py-1">
          Menu
        </p>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-brand-50 text-brand-700 shadow-sm border border-brand-100 font-semibold'
                    : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                }`
              }
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span>{item.name}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* System Status Footprint */}
      <div className="p-4 border-t border-slate-200 bg-slate-50/50">
        <div className="bg-white p-3 rounded-xl border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-700">
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              AI Core
            </span>
            <span className="text-[11px] text-brand-600 font-mono">S-BERT</span>
          </div>

          <div className="text-[11px] text-slate-500 space-y-1">
            <div className="flex items-center gap-1.5 truncate">
              <Cpu className="w-3.5 h-3.5 text-slate-600 shrink-0" />
              <span className="truncate" title="all-MiniLM-L6-v2">all-MiniLM-L6-v2</span>
            </div>
            <div className="flex items-center gap-1.5 truncate">
              <Database className="w-3.5 h-3.5 text-slate-600 shrink-0" />
              <span className="truncate">
                {health?.database?.type?.includes('Postgre') ? 'Supabase PG' : 'Local SQLite'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
}
