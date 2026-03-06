'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Plus, Search, Building2, Mail, Phone } from 'lucide-react';
import { getClients } from '@/lib/client';
import Card from '../components/ui/Card';
import Badge from '../components/ui/Badge';
import Button from '../components/ui/Button';
import Avatar from '../components/ui/Avatar';
import EmptyState from '../components/ui/EmptyState';
import Skeleton from '../components/ui/Skeleton';
import toast from 'react-hot-toast';

export default function ClientListPage() {
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  useEffect(() => {
    fetchClients();
  }, [search, statusFilter]);

  const fetchClients = async () => {
    try {
      setLoading(true);
      const res = await getClients({ search, status: statusFilter });
      setClients(res.results || res); // Handle pagination or plain array
    } catch (error) {
      toast.error('Failed to fetch clients');
    } finally {
      setLoading(false);
    }
  };

  const statusColors = {
    active: 'success',
    lead: 'primary',
    inactive: 'warning',
    archived: 'default',
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Clients</h1>
          <p className="text-slate-500 dark:text-slate-400 text-sm">Manage your customer relationships</p>
        </div>
        <Link href="/clients/new">
          <Button><Plus className="w-4 h-4 mr-2" /> Add Client</Button>
        </Link>
      </div>

      {/* Filters */}
      <Card className="p-4">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input 
              type="text"
              placeholder="Search by name, email, or company..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 focus:ring-2 focus:ring-indigo-500 text-sm"
            />
          </div>
          <select 
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="lead">Lead</option>
            <option value="inactive">Inactive</option>
          </select>
        </div>
      </Card>

      {/* Table/Grid */}
      <Card className="overflow-hidden">
        {loading ? (
          <div className="p-4 space-y-3">
            {[1,2,3].map(i => <Skeleton key={i} className="h-12 w-full" />)}
          </div>
        ) : clients.length === 0 ? (
          <EmptyState title="No clients found" description="Start by adding a new client to your database." />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 dark:bg-slate-800/50 border-b border-slate-200 dark:border-slate-700">
                <tr>
                  <th className="text-left py-3 px-4 font-medium text-slate-500 dark:text-slate-400">Client</th>
                  <th className="text-left py-3 px-4 font-medium text-slate-500 dark:text-slate-400 hidden md:table-cell">Company</th>
                  <th className="text-left py-3 px-4 font-medium text-slate-500 dark:text-slate-400 hidden lg:table-cell">Contact</th>
                  <th className="text-left py-3 px-4 font-medium text-slate-500 dark:text-slate-400">Status</th>
                  <th className="text-left py-3 px-4 font-medium text-slate-500 dark:text-slate-400 hidden lg:table-cell">Created</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
                {clients.map((client) => (
                  <Link href={`/clients/${client.id}`} key={client.id} className="contents">
                    <tr className="hover:bg-slate-50 dark:hover:bg-slate-800/30 cursor-pointer transition-colors">
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-3">
                          <Avatar name={client.name} />
                          <div>
                            <p className="font-medium text-slate-900 dark:text-white">{client.name}</p>
                            <p className="text-xs text-slate-500 md:hidden">{client.company_name}</p>
                          </div>
                        </div>
                      </td>
                      <td className="py-3 px-4 hidden md:table-cell text-slate-600 dark:text-slate-300">
                        {client.company_name || '-'}
                      </td>
                      <td className="py-3 px-4 hidden lg:table-cell">
                        <div className="flex flex-col">
                          <span className="text-slate-900 dark:text-white text-xs flex items-center gap-1">
                            <Mail className="w-3 h-3" /> {client.email}
                          </span>
                          <span className="text-slate-500 text-xs flex items-center gap-1 mt-0.5">
                            <Phone className="w-3 h-3" /> {client.phone || 'N/A'}
                          </span>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <Badge variant={statusColors[client.status]}>{client.status}</Badge>
                      </td>
                      <td className="py-3 px-4 text-slate-500 dark:text-slate-400 hidden lg:table-cell">
                        {new Date(client.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  </Link>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}