import { cn } from '@/lib/utils';

export default function Card({ children, className, hover = false }) {
  return (
    <div className={cn(
      "bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden",
      hover && "hover:shadow-md transition-shadow duration-200 cursor-pointer",
      className
    )}>
      {children}
    </div>
  );
}