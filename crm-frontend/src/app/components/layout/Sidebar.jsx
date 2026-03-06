'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, Building2, Users, Settings } from 'lucide-react';
import { cn } from '@/lib/utils'; // Assuming cn utility exists

const navItems = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Organization', href: '/organization', icon: Building2 },
  { name: 'Members', href: '/organization/members', icon: Users },
  { name: 'invites', href: '/organization/invites', icon: Settings },
  { name: 'Projects', href: '/organization/projects', icon: LayoutDashboard },
  { name: 'Contacts', href: '/organization/contacts', icon: Users },
  { name: 'Settings', href: '/organization/settings', icon: Settings },
  { name: 'Clients', href: '/clients', icon: Building2 },
  { name: 'Invoices', href: '/organization/invoices', icon: LayoutDashboard },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-700 h-screen flex flex-col">
      <div className="p-6">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-brand-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">S</span>
          </div>
          <span className="font-bold text-lg text-slate-900 dark:text-white">SaaSKit</span>
        </div>
      </div>

      <nav className="flex-1 px-4 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link 
              key={item.name} 
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200",
                isActive 
                  ? "bg-slate-100 dark:bg-blue-700 text-white dark:text-brand-400" 
                  : "text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-blue-700 hover:text-white dark:hover:text-white"
              )}
            >
              <item.icon className="w-5 h-5" />
              {item.name}
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-slate-200 dark:border-slate-700">
        <div className="flex items-center gap-3 px-3 py-2 rounded-xl bg-slate-50 dark:bg-green-400">
          <div className="w-8 h-8 rounded-full bg-slate-300 dark:bg-slate-600 flex items-center justify-center text-xs font-medium">
            JD
          </div>
          <div className="flex- overflow-hidden">
            <p className="text-sm font-medium text-slate-900 dark:text-white truncate">John Doe</p>
            <p className="text-xs text-slate-500 dark:text-slate-400 truncate">Admin</p>
          </div>
        </div>
      </div>
    </aside>
  );
}