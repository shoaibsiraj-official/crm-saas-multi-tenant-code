'use client';
import { Edit, Calendar, Users, CreditCard } from 'lucide-react';
import Skeleton from '@/app/components/ui/Skeleton';

export default function OrganizationCard({ data, loading, onEdit }) {
  if (loading) {
    return (
      <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden">
        <div className="h-32 bg-slate-200 dark:bg-slate-700" />
        <div className="p-6 space-y-4">
          <Skeleton className="h-6 w-1/3" />
          <Skeleton className="h-4 w-1/2" />
          <Skeleton className="h-4 w-1/4" />
        </div>
      </div>
    );
  }

  const usagePercent = data?.seat_limit ? (data.members_count / data.seat_limit) * 100 : 0;

  return (
    <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden hover:shadow-md transition-shadow duration-300">
      {/* Gradient Header */}
      <div className="h-32 bg-gradient-to-r from-brand-600 to-indigo-500 relative p-6 flex items-end">
        <div className="absolute inset-0 bg-black/10" />
        <div className="relative flex items-end justify-between w-full">
          <div>
            <h2 className="text-2xl font-bold text-white">{data?.name}</h2>
            <p className="text-brand-100 text-sm mt-1">Organization ID: {data?.id}</p>
          </div>
          <button 
            onClick={onEdit}
            className="p-2 bg-white/20 backdrop-blur-sm rounded-lg text-white hover:bg-white/30 transition-colors"
          >
            <Edit className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="p-6 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="flex items-start gap-3">
          <div className="p-2 bg-blue-50 dark:bg-blue-900/30 rounded-lg">
            <CreditCard className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          </div>
          <div>
            <p className="text-xs text-slate-500 dark:text-slate-400 uppercase font-medium">Plan</p>
            <p className="text-sm font-semibold text-slate-900 dark:text-white capitalize">{data?.subscription_plan || 'Free'}</p>
          </div>
        </div>

        <div className="flex items-start gap-3">
          <div className="p-2 bg-green-50 dark:bg-green-900/30 rounded-lg">
            <Users className="w-5 h-5 text-green-600 dark:text-green-400" />
          </div>
          <div>
            <p className="text-xs text-slate-500 dark:text-slate-400 uppercase font-medium">Seats Used</p>
            <p className="text-sm font-semibold text-slate-900 dark:text-white">
              {data?.members_count} / {data?.seat_limit || 'Unlimited'}
            </p>
            {data?.seat_limit && (
              <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-1.5 mt-2">
                <div 
                  className={`h-1.5 rounded-full ${usagePercent > 90 ? 'bg-red-500' : 'bg-green-500'}`} 
                  style={{ width: `${Math.min(usagePercent, 100)}%` }} 
                />
              </div>
            )}
          </div>
        </div>

        <div className="flex items-start gap-3">
          <div className="p-2 bg-purple-50 dark:bg-purple-900/30 rounded-lg">
            <Calendar className="w-5 h-5 text-purple-600 dark:text-purple-400" />
          </div>
          <div>
            <p className="text-xs text-slate-500 dark:text-slate-400 uppercase font-medium">Created</p>
            <p className="text-sm font-semibold text-slate-900 dark:text-white">
              {new Date(data?.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}