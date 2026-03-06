'use client';
import { forwardRef } from 'react';
import { cn } from '../../../lib/utils';

const InputField = forwardRef(({ label, error, icon: Icon, className, type = 'text', ...props }, ref) => {
  return (
    <div className="w-full">
      <div className="relative">
        {Icon && (
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Icon className="h-5 w-5 text-slate-400" />
          </div>
        )}
        <input
          type={type}
          ref={ref}
          className={cn(
            "block w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white/50 dark:bg-slate-800/50 text-slate-900 dark:text-white placeholder-transparent focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 peer",
            Icon && "pl-10",
            error && "border-red-500 focus:ring-red-500",
            className
          )}
          placeholder={label}
          {...props}
        />
        <label 
          className={cn(
            "absolute left-3 -top-2.5 text-xs text-slate-500 dark:text-slate-400 bg-white dark:bg-slate-900 px-1 transition-all peer-placeholder-shown:text-base peer-placeholder-shown:text-slate-400 peer-placeholder-shown:top-3 peer-placeholder-shown:left-3 peer-focus:-top-2.5 peer-focus:text-xs peer-focus:text-primary-600 peer-focus:left-3",
            Icon && "peer-placeholder-shown:left-10 peer-focus:left-3"
          )}
        >
          {label}
        </label>
      </div>
      {error && <p className="mt-1.5 text-xs text-red-500 pl-1">{error}</p>}
    </div>
  );
});

InputField.displayName = 'InputField';
export default InputField;