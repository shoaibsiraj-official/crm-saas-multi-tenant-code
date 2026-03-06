'use client';
import { cn } from '../../../lib/utils';

export default function AuthCard({ children, className }) {
  return (
    <div className={cn(
      "w-full max-w-md p-8 rounded-2xl glass-card",
      className
    )}>
      {children}
    </div>
  );
}