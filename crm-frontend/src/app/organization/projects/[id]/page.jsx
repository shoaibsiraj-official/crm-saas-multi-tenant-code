'use client';
import { CalendarDays, CheckCircle, ListTodo } from 'lucide-react';
import Card from '@/app/components/ui/Card';

export default function ProjectOverview({ params }) {
  // In real app, you'd fetch this or use context from layout
  // For simplicity, we are using passed data or re-fetching.
  // Ideally, layout passes data down via context or query client.
  // Here we simulate static display. 
  
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2">
        <Card className="p-6">
          <h3 className="font-semibold text-slate-900 dark:text-white mb-4">Project Description</h3>
          <p className="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">
            This is the project description area. It details the scope, goals, and deliverables of the project. 
            In a real implementation, this data would be fetched from the layout context.
          </p>
          
          <div className="mt-6 pt-6 border-t border-slate-100 dark:border-slate-700 grid grid-cols-2 gap-4">
            <div className="flex items-center gap-2 text-sm">
              <CalendarDays className="w-4 h-4 text-slate-400" />
              <span className="text-slate-600 dark:text-slate-400">Start: Jan 1, 2024</span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <CalendarDays className="w-4 h-4 text-slate-400" />
              <span className="text-slate-600 dark:text-slate-400">Deadline: Dec 31, 2024</span>
            </div>
          </div>
        </Card>
      </div>

      <div className="space-y-6">
        <Card className="p-6">
          <h3 className="font-semibold text-slate-900 dark:text-white mb-4">Progress</h3>
          <div className="flex items-center justify-center">
            <div className="relative w-32 h-32">
              <svg className="w-full h-full transform -rotate-90">
                <circle cx="64" cy="64" r="56" stroke="currentColor" strokeWidth="12" fill="none" className="text-slate-100 dark:text-slate-700"/>
                <circle cx="64" cy="64" r="56" stroke="currentColor" strokeWidth="12" fill="none" 
                  strokeDasharray="351.86" strokeDashoffset="87.965" className="text-indigo-600"/>
              </svg>
              <span className="absolute inset-0 flex items-center justify-center text-2xl font-bold text-slate-900 dark:text-white">75%</span>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <h3 className="font-semibold text-slate-900 dark:text-white mb-4">Statistics</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm text-slate-500">
                <ListTodo className="w-4 h-4" /> Total Tasks
              </div>
              <span className="font-semibold">12</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm text-slate-500">
                <CheckCircle className="w-4 h-4" /> Completed
              </div>
              <span className="font-semibold text-green-600">9</span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}