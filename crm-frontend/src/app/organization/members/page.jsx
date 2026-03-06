'use client';

import { useState, useEffect } from 'react';
import {
  getMembers,
  inviteMember,
  updateMemberRole,
  removeMember,
} from '@/lib/organization';
import MembersTable from '@/app/components/organization/MembersTable';
import InviteModal from '@/app/components/organization/InviteModal';
import Button from '@/app/components/ui/Button';
import toast from 'react-hot-toast';
import { UserPlus } from 'lucide-react';
import { useAuth } from '@/app/components/providers/AuthProvider';

export default function MembersPage() {
  const { user } = useAuth();

  // ✅ Get organizationId safely from user
  const organizationId = user?.organization?.id;

  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [inviteOpen, setInviteOpen] = useState(false);

  console.log("Auth user object:", user);

  // ✅ Fetch members ONLY when organizationId exists
  useEffect(() => {
    if (!organizationId) return;

    fetchMembers();
  }, [organizationId]);

  // ✅ WebSocket connection (safe + no crash)
  useEffect(() => {
    if (!organizationId) return;

    const socket = new WebSocket(
      `ws://localhost:8000/ws/org/${organizationId}/`
    );

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === "member_joined") {
        fetchMembers();
      }
    };

    socket.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    return () => {
      socket.close();
    };
  }, [organizationId]);

  const fetchMembers = async () => {
    try {
      setLoading(true);
      const res = await getMembers();
      console.log("Members API Response:", res);
      setMembers(res);
    } catch (e) {
      toast.error('Failed to load members');
    } finally {
      setLoading(false);
    }
  };

  const handleInvite = async (email, role) => {
    try {
      await inviteMember(email, role);
      toast.success("Invite sent");
      setInviteOpen(false);
      fetchMembers();
    } catch (error) {
      console.log("Invite Error:", error.response?.data);
      toast.error(error.response?.data?.message || "Invite failed");
    }
  };

  const handleRoleChange = async (userId, role) => {
    try {
      await updateMemberRole(userId, role);
      toast.success("Role updated");
      fetchMembers();
    } catch (error) {
      toast.error("Failed to update role");
      console.log("=== ROLE UPDATE ERROR ===");
      console.log("Status:", error.response?.status);
      console.log("Data:", error.response?.data);
      console.log("Full Error:", error);
    }
  };

  const handleRemove = async (userId) => {
    try {
      await removeMember(userId);
      toast.success("Member removed successfully");
      fetchMembers();
    } catch (error) {
      console.log("Remove Error:", error.response?.data);
      toast.error(
        error.response?.data?.message || "Failed to remove member"
      );
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
            Team Members
          </h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1">
            Manage your team and roles.
          </p>
        </div>

        <Button onClick={() => setInviteOpen(true)}>
          <UserPlus className="w-4 h-4 mr-2" />
          Invite Member
        </Button>
      </div>

      <MembersTable
        data={members}
        loading={loading}
        onRoleChange={handleRoleChange}
        onRemove={handleRemove}
        currentUserId={user?.id}
      />

      <InviteModal
        isOpen={inviteOpen}
        onClose={() => setInviteOpen(false)}
        onSubmit={handleInvite}
      />
    </div>
  );
}