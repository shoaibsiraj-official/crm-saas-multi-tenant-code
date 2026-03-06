'use client';

import { useState } from "react";
import { useRouter } from 'next/navigation';
import { createClient } from '@/lib/client';
import Card from '@/app/components/ui/Card';
import Button from '@/app/components/ui/Button';
import InputField from '@/app/components/ui/InputField';
import toast from 'react-hot-toast';

export default function NewClientPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  const [form, setForm] = useState({
    name: '',
    email: '',
    phone: '',
    company_name: '',
    address: '',
    notes: '',
    status: 'ACTIVE'
  });

const handleSubmit = async (e) => {
  e.preventDefault();

  if (!form.name.trim() || !form.email.trim()) {
    return toast.error("Name and Email are required");
  }

  setLoading(true);

  try {
    // 🔥 createClient already returns client object
    const newClient = await createClient({
      name: form.name.trim(),
      email: form.email.trim().toLowerCase(),
      phone: form.phone || "",
      company_name: form.company_name || "",
      address: form.address || "",
      notes: form.notes || "",
      status: form.status,
    });

    // Safety check
    if (!newClient?.id) {
      throw new Error("Invalid server response");
    }

    toast.success("Client created successfully ✅");

    router.push(`/organization/clients/${newClient.id}`);

  } catch (error) {
    console.log("FULL ERROR:", error);

    const serverMessage =
      error?.response?.data?.message ||
      error?.response?.data?.errors ||
      error?.message ||
      "Something went wrong";

    toast.error(
      typeof serverMessage === "string"
        ? serverMessage
        : JSON.stringify(serverMessage)
    );
  } finally {
    setLoading(false);
  }
};

  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
          New Client
        </h1>
        <p className="text-slate-500 dark:text-slate-400 text-sm">
          Fill in the details to add a new client.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">

        {/* Contact Info */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4 border-b pb-2">
            Contact Information
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <InputField
              label="Client Name"
              required
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
            />

            <InputField
              label="Company Name"
              value={form.company_name}
              onChange={(e) => setForm({ ...form, company_name: e.target.value })}
            />

            <InputField
              label="Email"
              type="email"
              required
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
            />

            <InputField
              label="Phone"
              type="tel"
              value={form.phone}
              onChange={(e) => setForm({ ...form, phone: e.target.value })}
            />
          </div>
        </Card>

        {/* Additional Details */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4 border-b pb-2">
            Additional Details
          </h3>

          <div className="space-y-4">

            <div>
              <label className="block text-sm font-medium mb-1">
                Status
              </label>

              {/* 🔥 FIXED VALUES (Must match backend choices exactly) */}
              <select
                value={form.status}
                onChange={(e) =>
                  setForm({ ...form, status: e.target.value })
                }
                className="w-full px-3 py-2.5 rounded-lg border"
              >
                <option value="ACTIVE">Active</option>
                <option value="INACTIVE">Inactive</option>
              </select>
            </div>

            <InputField
              label="Address"
              value={form.address}
              onChange={(e) => setForm({ ...form, address: e.target.value })}
            />

            <div>
              <label className="block text-sm font-medium mb-1">
                Notes
              </label>
              <textarea
                rows={4}
                className="w-full px-3 py-2 rounded-lg border text-sm"
                value={form.notes}
                onChange={(e) => setForm({ ...form, notes: e.target.value })}
                placeholder="Add any specific notes about this client..."
              />
            </div>

          </div>
        </Card>

        {/* Buttons */}
        <div className="flex justify-end gap-3">
          <Button
            variant="secondary"
            type="button"
            onClick={() => router.back()}
          >
            Cancel
          </Button>

          <Button type="submit"
            disabled={loading}
            isLoading={loading}
          >
            Save Client
          </Button>
        </div>

      </form>
    </div>
  );
}