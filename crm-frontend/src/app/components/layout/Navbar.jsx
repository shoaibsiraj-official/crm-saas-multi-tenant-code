'use client';
import Link from 'next/link';
import { useTheme } from 'next-themes';
import { Moon, Sun, User } from 'lucide-react';
import { useEffect, useState } from 'react';

export default function Navbar() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => setMounted(true), []);

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 backdrop-blur-md bg-white/30 dark:bg-blue-300 border-b border-slate-200/50 dark:border-slate-700/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link href="/" className="text-xl font-bold text-slate-900 dark:text-white tracking-tight">
            SaaS<span className="text-primary-500">Kit</span>
          </Link>
          
          <div className="flex items-center space-x-4">
            <Link href="/login" className="text-sm font-medium text-black hover:text-slate-900 dark:text-black-300 dark:hover:text-white transition-colors">
              Sign In
            </Link>
            <Link href="/register">
              <button className="px-4 py-2 text-sm font-medium bg-slate-900 text-white rounded-lg hover:bg-slate-800 dark:bg-white dark:text-slate-900 dark:hover:bg-slate-100 transition-colors">
                Get Started
              </button>
            </Link>
            
            {mounted && (
              <button 
                onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
                className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              >
                {theme === 'dark' ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
              </button>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}