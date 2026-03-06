'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Plus, Search } from 'lucide-react';
import Button from '@/app/components/ui/Button';
import InputField from '@/app/components/ui/InputField';
import Skeleton from '@/app/components/ui/Skeleton';
import toast from 'react-hot-toast';
import api from '@/lib/axios';

export default function ContactsPage() {
  const router = useRouter();

  const [contacts, setContacts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    fetchContacts();
  }, []);

  const fetchContacts = async () => {
    try {
      const res = await api.get('/contacts/');
      setContacts(res.data.data.contacts);
    } catch (err) {
      toast.error('Failed to load contacts');
    } finally {
      setLoading(false);
    }
  };

  const filteredContacts = contacts.filter((contact) =>
    contact.name?.toLowerCase().includes(search.toLowerCase()) ||
    contact.email?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="max-w-6xl mx-auto space-y-8">

      {/* HEADER */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
            Contacts
          </h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1">
            Manage your leads and clients.
          </p>
        </div>

        <Button onClick={() => router.push('/organization/contacts/new')}>
          <Plus className="w-4 h-4 mr-2" />
          Add Contact
        </Button>
      </div>

      {/* SEARCH */}
      <div className="max-w-sm">
        <InputField
          type="text"
          placeholder="Search contacts..."
          icon={Search}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {/* TABLE */}
      <div className="overflow-x-auto rounded-xl border border-slate-200 dark:border-slate-700">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 dark:bg-slate-800/50 border-b border-slate-200 dark:border-slate-700">
            <tr>
              <th className="text-left py-3 px-4 font-medium">Name</th>
              <th className="text-left py-3 px-4 font-medium">Email</th>
              <th className="text-left py-3 px-4 font-medium">Phone</th>
              <th className="text-left py-3 px-4 font-medium">Company</th>
              <th className="text-left py-3 px-4 font-medium">Created</th>
            </tr>
          </thead>

          <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
            {loading ? (
              [1,2,3].map((i) => (
                <tr key={i}>
                  <td colSpan="5">
                    <Skeleton className="h-12 w-full" />
                  </td>
                </tr>
              ))
            ) : filteredContacts.length === 0 ? (
              <tr>
                <td colSpan="5" className="py-6 text-center text-slate-500">
                  No contacts found.
                </td>
              </tr>
            ) : (
              filteredContacts.map((contact) => (
                <tr
                  key={contact.id}
                  className="hover:bg-slate-50 dark:hover:bg-slate-800/30 transition"
                >
                  <td className="py-3 px-4 font-medium text-slate-900 dark:text-white">
                    {contact.name}
                  </td>
                  <td className="py-3 px-4">{contact.email}</td>
                  <td className="py-3 px-4">{contact.phone || '-'}</td>
                  <td className="py-3 px-4">{contact.company || '-'}</td>
                  <td className="py-3 px-4 text-xs text-slate-500">
                    {new Date(contact.created_at).toLocaleDateString()}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}