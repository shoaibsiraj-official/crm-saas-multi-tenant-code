'use client';

import { use, useEffect, useState } from 'react';
import { getProject } from '@/lib/project';
import { useRouter } from 'next/navigation';
import Card from '@/app/components/ui/Card';
import toast from 'react-hot-toast';
import Link from 'next/link';

export default function ProjectLayout({ children, params }) {
  const resolvedParams = use(params);
  const projectId = resolvedParams.id;

  const router = useRouter();
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!projectId) return;

    getProject(projectId)
      .then((res) => {
        setProject(res);
      })
      .catch(() => {
        toast.error('Failed to fetch project');
        router.push('/organization/projects');
      })
      .finally(() => setLoading(false));
  }, [projectId]);

  if (loading) {
    return <div className="p-6">Loading project...</div>;
  }

  if (!project) {
    return null;
  }

  return (
    <div className="space-y-6">

      {/* 🔥 Project Header */}
      <Card className="p-6">
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
          {project.name}
        </h1>
        <p className="text-sm text-slate-500 mt-2">
          {project.name} is currently <strong>{project.status}</strong>. Start date: {project.start_date}, Deadline: {project.deadline}.
          {project.description || 'No description provided'}
        </p>
      </Card>

      {/* 🔥 Tabs Navigation */}
      <div className="flex gap-6 border-b border-slate-200 dark:border-slate-700 pb-2 text-sm font-medium">
        <Link href={`/organization/projects/${projectId}`} className="hover:text-indigo-600">
          Overview
        </Link>

        <Link href={`/organization/projects/${projectId}/tasks`} className="hover:text-indigo-600">
          Tasks
        </Link>

        <Link href={`/organization/projects/${projectId}/settings`} className="hover:text-indigo-600">
          Settings
        </Link>
      </div>

      {/* 🔥 Page Content */}
      <div>
        {children}
      </div>
    </div>
  );
}