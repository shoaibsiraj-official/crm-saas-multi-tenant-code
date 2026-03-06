import { FolderOpen } from 'lucide-react';

export default function EmptyState({ title = "No data found", description = "Get started by creating a new item." }) {
  return (
    <div className="text-center py-16 px-4">
      <div className="mx-auto w-16 h-16 bg-slate-100 dark:bg-slate-700 rounded-full flex items-center justify-center mb-4">
        <FolderOpen className="w-8 h-8 text-slate-400" />
      </div>
      <h3 className="text-lg font-medium text-slate-900 dark:text-white">{title}</h3>
      <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">{description}</p>
    </div>
  );
}