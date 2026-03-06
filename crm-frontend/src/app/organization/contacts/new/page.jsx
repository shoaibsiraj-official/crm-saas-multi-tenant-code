'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Card from '@/app/components/ui/Card';
import InputField from '@/app/components/ui/InputField';
import Button from '@/app/components/ui/Button';
import toast from 'react-hot-toast';
import api from '@/lib/axios';

export default function NewContactPage() {

  const router = useRouter();
  const [loading, setLoading] = useState(false);

  const [form, setForm] = useState({
    name: '',
    email: '',
    phone: '',
    company: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!form.name) {
      return toast.error('Name is required');
    }

    try {

      setLoading(true);

      await api.post('/contacts/', form);

      toast.success('Contact created successfully');

      router.push('/organization/contacts');

    } catch (err) {

      toast.error(
        err.response?.data?.message || 'Failed to create contact'
      );

    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto">

      <Card className="p-8">

        <h1 className="text-2xl font-bold mb-6 text-slate-900 dark:text-white">
          Add Contact
        </h1>

        <form onSubmit={handleSubmit} className="space-y-5">

          <InputField
            label="Name"
            required
            value={form.name}
            onChange={(e) =>
              setForm({ ...form, name: e.target.value })
            }
          />

          <InputField
            label="Email"
            type="email"
            value={form.email}
            onChange={(e) =>
              setForm({ ...form, email: e.target.value })
            }
          />

          <InputField
            label="Phone"
            value={form.phone}
            onChange={(e) =>
              setForm({ ...form, phone: e.target.value })
            }
          />

          <InputField
            label="Company"
            value={form.company}
            onChange={(e) =>
              setForm({ ...form, company: e.target.value })
            }
          />

          <div className="flex justify-end gap-3 pt-4">

            <Button
              type="button"
              variant="secondary"
              onClick={() => router.back()}
            >
              Cancel
            </Button>

            <Button type="submit" isLoading={loading}>
              Create Contact
            </Button>

          </div>

        </form>

      </Card>

    </div>
  );
}