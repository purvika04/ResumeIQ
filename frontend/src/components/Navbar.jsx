import React from 'react';
import { Sparkles, CheckCircle2 } from 'lucide-react';

export default function Navbar({ health }) {
  return (
    <header className="h-16 bg-white border-b border-slate-200 px-8 flex items-center justify-between shrink-0 sticky top-0 z-10">
      <div className="flex items-center gap-3">
        <h1 className="text-base font-semibold text-slate-800">
          AI Candidate Screening & Intelligence
        </h1>
        <span className="hidden sm:inline-flex items-center gap-1 text-xs px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 font-medium">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
          Engine Online
        </span>
      </div>

      <div className="flex items-center gap-4">
        {/* Recruiter info */}
        <div className="flex items-center gap-3 pl-4 border-l border-slate-200">
          <div className="w-9 h-9 rounded-full bg-brand-100 border border-brand-200 text-brand-700 flex items-center justify-center font-bold text-sm shadow-sm">
            AM
          </div>
          <div className="hidden md:block text-left">
            <p className="text-xs font-semibold text-slate-800 leading-tight">Alex Mercer</p>
            <p className="text-[11px] text-slate-600">Lead Technical Recruiter</p>
          </div>
        </div>
      </div>
    </header>
  );
}
