'use client';

import { useEffect, useState } from 'react';
import axios from '@/lib/axios';
import Card from '@/app/components/ui/Card';
import { 
  DollarSign, 
  Clock, 
  Folder, 
  Users, 
  CheckCircle, 
  Activity,
  TrendingUp 
} from 'lucide-react';

export default function OrganizationDashboard() {

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {

        // ✅ FIXED ENDPOINT
        const response = await axios.get('/projects/admin/analytics/');

        // ✅ FIXED ENVELOPE EXTRACTION
        setData(response.data?.data || {});

      } catch (error) {
        console.error('Failed to fetch analytics:', error.response?.data || error);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, []);

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount || 0);
  };

  // Backend structure ke hisaab se values extract karo
  const projectData = data?.projects || {};
  const taskData = data?.tasks || {};
  const clientData = data?.clients || {};

  const taskProgress = taskData?.completion_rate || 0;

  const stats = [
    {
      label: 'Total Projects',
      value: projectData.total || 0,
      icon: Folder,
      iconBg: 'bg-blue-100 dark:bg-blue-900/30',
      iconColor: 'text-blue-600 dark:text-blue-400',
    },
    {
      label: 'Active Projects',
      value: projectData.active || 0,
      icon: Activity,
      iconBg: 'bg-indigo-100 dark:bg-indigo-900/30',
      iconColor: 'text-indigo-600 dark:text-indigo-400',
    },
    {
      label: 'Completed Projects',
      value: projectData.completed || 0,
      icon: CheckCircle,
      iconBg: 'bg-green-100 dark:bg-green-900/30',
      iconColor: 'text-green-600 dark:text-green-400',
    },
    {
      label: 'Total Clients',
      value: clientData.total_clients || 0,
      icon: Users,
      iconBg: 'bg-cyan-100 dark:bg-cyan-900/30',
      iconColor: 'text-cyan-600 dark:text-cyan-400',
    },
    {
      label: 'Total Tasks',
      value: taskData.total || 0,
      icon: Clock,
      iconBg: 'bg-purple-100 dark:bg-purple-900/30',
      iconColor: 'text-purple-600 dark:text-purple-400',
    },
    {
      label: 'Completion Rate',
      value: `${taskProgress}%`,
      icon: TrendingUp,
      iconBg: 'bg-pink-100 dark:bg-pink-900/30',
      iconColor: 'text-pink-600 dark:text-pink-400',
    },
  ];

  const LoadingSkeleton = () => (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {[1,2,3,4,5,6].map((i) => (
        <Card key={i} className="p-6 animate-pulse h-24" />
      ))}
    </div>
  );

  return (
    <div className="space-y-8">

      <div>
        <h1 className="text-2xl font-bold">Dashboard Overview</h1>
        <p className="text-sm text-slate-500">
          Analyze your organization's performance metrics.
        </p>
      </div>

      {loading ? (
        <LoadingSkeleton />
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {stats.map((stat, index) => (
              <Card key={index} className="p-6">
                <div className="flex justify-between items-center">
                  <div>
                    <p className="text-sm text-slate-500">{stat.label}</p>
                    <p className="text-2xl font-bold">{stat.value}</p>
                  </div>
                  <div className={`p-3 rounded-xl ${stat.iconBg}`}>
                    <stat.icon className={`w-6 h-6 ${stat.iconColor}`} />
                  </div>
                </div>
              </Card>
            ))}
          </div>

          {/* Task Progress */}
          <Card className="p-6">
            <div className="flex justify-between mb-3">
              <div>
                <h3 className="font-semibold">Task Completion</h3>
                <p className="text-sm text-slate-500">
                  {taskData.done || 0} of {taskData.total || 0} completed
                </p>
              </div>
              <span className="font-bold">{taskProgress}%</span>
            </div>

            <div className="w-full bg-slate-200 rounded-full h-3">
              <div
                className="bg-indigo-600 h-3 rounded-full transition-all duration-500"
                style={{ width: `${taskProgress}%` }}
              />
            </div>
          </Card>
        </>
      )}
    </div>
  );
}