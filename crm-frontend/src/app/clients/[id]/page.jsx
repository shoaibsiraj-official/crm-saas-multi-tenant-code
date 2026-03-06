'use client';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useParams } from 'next/navigation';
import { getClient, deleteClient } from '@/lib/client';
import Card from '@/app/components/ui/Card';
import Badge from '@/app/components/ui/Badge';
import Button from '@/app/components/ui/Button';
import Avatar from '@/app/components/ui/Avatar';
import Modal from '@/app/components/ui/Modal';
import Skeleton from '@/app/components/ui/Skeleton';
import toast from 'react-hot-toast';
import { Edit, Trash2, Mail, Phone, MapPin, Calendar, User } from 'lucide-react';
import Link from 'next/link';

export default function ClientDetailPage() {
  const { id } = useParams();
  const router = useRouter();
  const [client, setClient] = useState(null);
  const [loading, setLoading] = useState(true);
  const [deleteModal, setDeleteModal] = useState(false);

  useEffect(() => {
    fetchClient();
  }, [id]);

  const fetchClient = async () => {
    try {
      const res = await getClient(id);
      setClient(res);
    } catch (err) {
      toast.error('Client not found');
      router.push('/clients');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    try {
      await deleteClient(id);
      toast.success('Client deleted');
      router.push('/clients');
    } catch (err) {
      toast.error('Failed to delete client');
    }
  };

  const statusColors = { active: 'success', lead: 'primary', inactive: 'warning' };

  if (loading) return <div className="p-8"><Skeleton className="h-32 w-full" /></div>;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <Avatar name={client?.name} className="w-16 h-16 text-xl" />
          <div>
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white">{client?.name}</h1>
            <div className="flex items-center gap-2 mt-1">
              <span className="text-slate-500 text-sm">{client?.company_name}</span>
              <Badge variant={statusColors[client?.status]}>{client?.status}</Badge>
            </div>
          </div>
        </div>
        <div className="flex gap-2">
          <Link href={`/clients/${id}/edit`}>
            <Button variant="secondary"><Edit className="w-4 h-4 mr-2" /> Edit</Button>
          </Link>
          <Button variant="danger" onClick={() => setDeleteModal(true)}>
            <Trash2 className="w-4 h-4" />
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Info */}
        <div className="lg:col-span-2 space-y-6">
          <Card className="p-6">
            <h3 className="text-sm font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-4">Contact Info</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-y-4 gap-x-8">
              <div className="flex items-center gap-3">
                <Mail className="w-5 h-5 text-slate-400" />
                <div>
                  <p className="text-xs text-slate-500">Email</p>
                  <a href={`mailto:${client?.email}`} className="text-sm font-medium text-indigo-600 dark:text-indigo-400 hover:underline">
                    {client?.email}
                  </a>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Phone className="w-5 h-5 text-slate-400" />
                <div>
                  <p className="text-xs text-slate-500">Phone</p>
                  <p className="text-sm font-medium text-slate-800 dark:text-slate-200">
                    {client?.phone || 'Not provided'}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3 md:col-span-2">
                <MapPin className="w-5 h-5 text-slate-400" />
                <div>
                  <p className="text-xs text-slate-500">Address</p>
                  <p className="text-sm font-medium text-slate-800 dark:text-slate-200">
                    {client?.address || 'Not provided'}
                  </p>
                </div>
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <h3 className="text-sm font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-4">Notes</h3>
            <p className="text-sm text-slate-600 dark:text-slate-300 whitespace-pre-wrap">
              {client?.notes || 'No notes added for this client.'}
            </p>
          </Card>
        </div>

        {/* Sidebar Info */}
        <div className="space-y-6">
          <Card className="p-6">
            <h3 className="text-sm font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-4">Metadata</h3>
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <User className="w-5 h-5 text-slate-400" />
                <div>
                  <p className="text-xs text-slate-500">Created By</p>
                  <p className="text-sm font-medium text-slate-800 dark:text-slate-200">
                    {client?.created_by_name || 'System'}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Calendar className="w-5 h-5 text-slate-400" />
                <div>
                  <p className="text-xs text-slate-500">Created At</p>
                  <p className="text-sm font-medium text-slate-800 dark:text-slate-200">
                    {new Date(client?.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>

      {/* Delete Modal */}
      <Modal isOpen={deleteModal} onClose={() => setDeleteModal(false)} title="Delete Client">
        <p className="text-slate-600 dark:text-slate-300 mb-6">
          Are you sure you want to delete <span className="font-semibold">{client?.name}</span>? This action cannot be undone.
        </p>
        <div className="flex justify-end gap-3">
          <Button variant="secondary" onClick={() => setDeleteModal(false)}>Cancel</Button>
          <Button onClick={handleDelete} className="bg-red-600 hover:bg-red-700">Delete</Button>
        </div>
      </Modal>
    </div>
  );
}