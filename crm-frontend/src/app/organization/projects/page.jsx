'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Plus, Search } from 'lucide-react';
import { getProjects } from '@/lib/project';
import Card from '@/app/components/ui/Card';
import Badge from '@/app/components/ui/Badge';
import Avatar from '@/app/components/ui/Avatar';
import Button from '@/app/components/ui/Button';
import EmptyState from '@/app/components/ui/EmptyState';
import Skeleton from '@/app/components/ui/Skeleton';
import toast from 'react-hot-toast';

export default function ProjectListPage() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchProjects();
  }, [search, filter]);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      const res = await getProjects({
        search,
        status: filter === 'all' ? '' : filter.toUpperCase(),
      });
      setProjects(res);
    } catch (e) {
      toast.error('Failed to fetch projects');
    } finally {
      setLoading(false);
    }
  };

  const statusColors = {
    active: 'success',
    completed: 'primary',
    archived: 'default',
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
            Projects
          </h1>
          <p className="text-slate-500 dark:text-slate-400 text-sm">
            Manage your active work
          </p>
        </div>

        <Link href="/organization/projects/create">
          <Button>
            <Plus className="w-4 h-4 mr-2" /> Create Project
          </Button>
        </Link>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search projects..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 focus:ring-2 focus:ring-indigo-500 text-sm"
          />
        </div>

        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm focus:ring-2 focus:ring-indigo-500"
        >
          <option value="all">All Status</option>
          <option value="active">Active</option>
          <option value="completed">Completed</option>
          <option value="archived">Archived</option>
        </select>
      </div>

      {/* Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="p-5 space-y-4">
              <Skeleton className="h-5 w-3/4" />
              <Skeleton className="h-3 w-full" />
              <Skeleton className="h-2 w-1/2" />
            </Card>
          ))}
        </div>
      ) : projects.length === 0 ? (
        <EmptyState
          title="No projects found"
          description="Try adjusting your search or create a new project."
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project) => (
            <Link
              key={project.id}
              href={`/organization/projects/${project.id}/kanban`}
            >
              <Card hover className="p-5 h-full flex flex-col cursor-pointer">
                <div className="flex justify-between items-start mb-3">
                  <h3 className="font-semibold text-slate-900 dark:text-white truncate mr-2">
                    {project.name}
                  </h3>

                  <Badge
                    variant={
                      statusColors[project.status?.toLowerCase()] || 'default'
                    }
                  >
                    {project.status}
                  </Badge>
                </div>

                <p className="text-sm text-slate-500 dark:text-slate-400 mb-4 line-clamp-2 flex-grow">
                  {project.description || 'No description provided.'}
                </p>

                {/* Progress */}
                <div className="mb-4">
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-slate-500">Progress</span>
                    <span className="font-medium text-slate-700 dark:text-slate-300">
                      {project.progress || 0}%
                    </span>
                  </div>

                  <div className="w-full bg-slate-100 dark:bg-slate-700 rounded-full h-1.5">
                    <div
                      className="bg-indigo-500 h-1.5 rounded-full transition-all duration-300"
                      style={{ width: `${project.progress || 0}%` }}
                    />
                  </div>
                </div>

                <div className="flex items-center justify-between border-t border-slate-100 dark:border-slate-700 pt-4">
                  <div className="flex -space-x-2">
                    {project.members?.slice(0, 3).map((m) => (
                      <Avatar
                        key={m.id}
                        name={m.full_name || m.email}
                        className="border-2 border-white dark:border-slate-800"
                      />
                    ))}

                    {project.members?.length > 3 && (
                      <div className="w-8 h-8 rounded-full bg-slate-100 dark:bg-slate-600 flex items-center justify-center text-xs border-2 border-white dark:border-slate-800">
                        +{project.members.length - 3}
                      </div>
                    )}
                  </div>
                  

                  <span className="text-xs text-slate-400">
                    {new Date(project.created_at).toLocaleDateString()}
                  </span>
                </div>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}