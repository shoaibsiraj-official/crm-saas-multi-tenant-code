'use client';
import { useState, useEffect } from 'react';
import { getProjectMembers, assignMember } from '@/lib/project';
import { getMembers } from '@/lib/organization';
import Avatar from '@/app/components/ui/Avatar';
import Button from '@/app/components/ui/Button';
import Card from '@/app/components/ui/Card';
import Badge from '@/app/components/ui/Badge';
import Modal from '@/app/components/ui/Modal';
import toast from 'react-hot-toast';
import { UserPlus } from 'lucide-react';

export default function ProjectMembersPage({ params }) {
  const { id } = params;
  const [members, setMembers] = useState([]);
  const [orgMembers, setOrgMembers] = useState([]);
  const [isModalOpen, setModalOpen] = useState(false);
  const [selectedMember, setSelectedMember] = useState('');
  const [role, setRole] = useState('contributor');

  useEffect(() => {
    fetchMembers();
    getMembers().then(setOrgMembers);
  }, [id]);

  const fetchMembers = async () => {
    const res = await getProjectMembers(id);
    setMembers(res);
  };

  const handleAssign = async () => {
    try {
      await assignMember(id, { user_id: selectedMember, role });
      toast.success('Member assigned');
      setModalOpen(false);
      fetchMembers();
    } catch (e) {
      toast.error('Error assigning member');
    }
  };

  const roleColors = { owner: 'primary', contributor: 'success', viewer: 'default' };

  return (
    <div className="space-y-6">
      <div className="flex justify-end">
        <Button onClick={() => setModalOpen(true)}><UserPlus className="w-4 h-4 mr-2" /> Assign Member</Button>
      </div>

      <Card className="divide-y divide-slate-100 dark:divide-slate-700">
        {members.map(m => (
          <div key={m.id} className="flex items-center justify-between p-4 hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors">
            <div className="flex items-center gap-3">
              <Avatar name={m.name} />
              <div>
                <p className="font-medium text-slate-900 dark:text-white">{m.name}</p>
                <p className="text-xs text-slate-500">{m.email}</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <Badge variant={roleColors[m.role]}>{m.role}</Badge>
              {m.role !== 'owner' && (
                <button className="text-xs text-red-500 hover:underline">Remove</button>
              )}
            </div>
          </div>
        ))}
      </Card>

      <Modal isOpen={isModalOpen} onClose={() => setModalOpen(false)} title="Assign Team Member">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Select Member</label>
            <select value={selectedMember} onChange={e => setSelectedMember(e.target.value)}
              className="w-full px-3 py-2 rounded-lg border dark:bg-slate-700 dark:border-slate-600">
              <option value="">Choose...</option>
              {orgMembers.filter(om => !members.find(m => m.id === om.id)).map(m => (
                <option key={m.id} value={m.id}>{m.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Role</label>
            <select value={role} onChange={e => setRole(e.target.value)}
              className="w-full px-3 py-2 rounded-lg border dark:bg-slate-700 dark:border-slate-600">
              <option value="contributor">Contributor</option>
              <option value="viewer">Viewer</option>
            </select>
          </div>
          <div className="pt-4">
            <Button onClick={handleAssign} className="w-full">Assign</Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}