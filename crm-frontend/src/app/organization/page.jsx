'use client';
import { useState, useEffect } from 'react';
import { getOrganization, updateOrganization } from '@/lib/organization';
import OrganizationCard from '../components/organization/OrganizationCard';
import Modal from '../components/ui/Modal';
import Button from '../components/ui/Button';
import InputField from '../components/ui/InputField';
import toast from 'react-hot-toast';

export default function OrganizationPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editOpen, setEditOpen] = useState(false);
  const [editLoading, setEditLoading] = useState(false);
  const [name, setName] = useState('');

  useEffect(() => {
    fetchOrg();
  }, []);

  const fetchOrg = async () => {
    try {
      const res = await getOrganization();
      setData(res);
      setName(res.name);
    } catch (e) {
      toast.error('Failed to load organization');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdate = async () => {
    setEditLoading(true);
    try {
      const updated = await updateOrganization({ name });
      setData(updated);
      toast.success('Organization updated');
      setEditOpen(false);
    } catch (e) {
      toast.error(e.response?.data?.message || 'Update failed');
    } finally {
      setEditLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Organization Settings</h1>
        <p className="text-slate-500 dark:text-slate-400 mt-1">Manage your workspace details.</p>
      </div>

      <OrganizationCard 
        data={data} 
        loading={loading} 
        onEdit={() => setEditOpen(true)} 
      />

      <Modal isOpen={editOpen} onClose={() => setEditOpen(false)} title="Edit Organization">
        <div className="space-y-5">
          <InputField 
            label="Organization Name" 
            value={name} 
            onChange={(e) => setName(e.target.value)} 
          />
          <div className="flex justify-end gap-3 pt-4">
            <Button variant="secondary" onClick={() => setEditOpen(false)}>Cancel</Button>
            <Button onClick={handleUpdate} isLoading={editLoading}>Save Changes</Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}