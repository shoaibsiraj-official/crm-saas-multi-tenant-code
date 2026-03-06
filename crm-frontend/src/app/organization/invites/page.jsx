'use client';

import { useEffect, useState } from 'react';
import { getInvites, revokeInvite, getOrganizationDetail } from '@/lib/organization';
import toast from 'react-hot-toast';
import Button from '@/app/components/ui/Button';

export default function InvitePage() {
  const [invites, setInvites] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("PENDING");
  const [org, setOrg] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    filterInvites();
  }, [activeTab, invites]);

  const fetchData = async () => {
    try {
      const inviteData = await getInvites();
      const orgData = await getOrganizationDetail();

      setInvites(inviteData);
      setOrg(orgData);
    } catch {
      toast.error("Failed to load data");
    } finally {
      setLoading(false);
    }
  };

  const filterInvites = () => {
    const data = invites.filter(inv => inv.status === activeTab);
    setFiltered(data);
  };

  const handleRevoke = async (id) => {
    try {
      await revokeInvite(id);
      toast.success("Invite revoked");
      fetchData();
    } catch {
      toast.error("Failed to revoke");
    }
  };

  const badgeColors = {
    PENDING: "bg-yellow-100 text-yellow-700",
    ACCEPTED: "bg-green-100 text-green-700",
    EXPIRED: "bg-red-100 text-red-700",
  };

  if (loading) return <p className="p-8">Loading...</p>;

  return (
    <div className="max-w-6xl mx-auto space-y-6">

      {/* 🔥 Seat Counter */}
      {org && (
        <div className="p-4 rounded-xl bg-slate-100 dark:bg-slate-800 flex justify-between items-center">
          <div>
            <h2 className="font-semibold">Seat Usage</h2>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              {org.member_count} / {org.seat_limit === -1 ? "Unlimited" : org.seat_limit}
            </p>
          </div>
          <div className="text-sm">
            Remaining: <span className="font-semibold">{org.seats_remaining}</span>
          </div>
        </div>
      )}

      <h1 className="text-2xl font-bold">Invite Tracking</h1>

      {/* 🔥 Tabs */}
      <div className="flex gap-4">
        {["PENDING", "ACCEPTED", "EXPIRED"].map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 rounded-lg text-sm font-medium ${
              activeTab === tab
                ? "bg-primary-600 text-white"
                : "bg-slate-200 dark:bg-slate-700"
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* 🔥 Table */}
      <div className="bg-white dark:bg-slate-800 rounded-xl shadow">
        <table className="w-full text-sm">
          <thead className="border-b">
            <tr>
              <th className="text-left p-4">Email</th>
              <th className="text-left p-4">Role</th>
              <th className="text-left p-4">Status</th>
              <th className="text-left p-4">Action</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((invite) => (
              <tr key={invite.id} className="border-b">
                <td className="p-4">{invite.email}</td>
                <td className="p-4">{invite.role}</td>
                <td className="p-4">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${badgeColors[invite.status]}`}>
                    {invite.status}
                  </span>
                </td>
                <td className="p-4">
                  {invite.status === "PENDING" && (
                    <Button
                      variant="destructive"
                      onClick={() => handleRevoke(invite.id)}
                    >
                      Revoke
                    </Button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {filtered.length === 0 && (
          <p className="p-6 text-center text-slate-500">
            No {activeTab.toLowerCase()} invites
          </p>
        )}
      </div>
    </div>
  );
}