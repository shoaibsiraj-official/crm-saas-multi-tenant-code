import { cn } from '@/lib/utils';

export default function Avatar({ src, name, className }) {
  const initials = name?.split(' ').map(n => n[0]).join('').substring(0, 2);
  
  return (
    <div className={cn(
      "relative inline-flex items-center justify-center w-8 h-8 rounded-full bg-slate-200 dark:bg-slate-700 text-xs font-medium text-slate-600 dark:text-slate-300 overflow-hidden",
      className
    )}>
      {src ? <img src={src} alt={name} className="w-full h-full object-cover" /> : initials}
    </div>
  );
}