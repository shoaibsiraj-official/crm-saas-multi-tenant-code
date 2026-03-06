'use client';
import { cn } from '../../../lib/utils';
import { Loader2 } from 'lucide-react';

export default function Button({ 
  children, 
  className, 
  variant = 'primary', 
  isLoading, 
  disabled, 
  ...props 
}) {
  const baseStyles = "relative inline-flex items-center justify-center px-6 py-3 text-sm font-medium rounded-xl transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed";
  
  const variants = {
    primary: "bg-slate-900 text-white hover:bg-slate-800 dark:bg-white dark:text-slate-900 dark:hover:bg-slate-100 shadow-md hover:shadow-lg transform hover:-translate-y-0.5",
    secondary: "bg-slate-100 text-slate-900 hover:bg-slate-200 dark:bg-slate-800 dark:text-white dark:hover:bg-slate-700",
    outline: "border border-slate-300 text-slate-700 hover:bg-slate-50 dark:border-slate-600 dark:text-slate-300 dark:hover:bg-slate-800",
  };

  return (
    <button 
      className={cn(baseStyles, variants[variant], className)} 
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
      ) : null}
      {children}
    </button>
  );
}