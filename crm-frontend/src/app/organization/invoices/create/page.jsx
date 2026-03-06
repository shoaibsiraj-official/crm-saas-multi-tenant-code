'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import axios from '@/lib/axios';
import Card from '@/app/components/ui/Card';
import Button from '@/app/components/ui/Button';
import InputField from '@/app/components/ui/InputField';
import toast from 'react-hot-toast';

export default function CreateInvoicePage() {

  const router = useRouter();

  const [clients, setClients] = useState([]);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(false);

  const [form, setForm] = useState({
    client: '',
    project: '',
    due_date: '',
    status: 'DRAFT',
    amount: ''
  });

  useEffect(() => {
    fetchClients();
    fetchProjects();
  }, []);

  // =========================
  // FETCH CLIENTS
  // =========================
  const fetchClients = async () => {
    try {

      const res = await axios.get('/clients/');
      const data = res.data;

      const list =
        data.results ||
        data.data?.results ||
        data.data ||
        [];

      setClients(Array.isArray(list) ? list : []);

    } catch (err) {

      console.log(err.response?.data);
      toast.error('Failed to load clients');

    }
  };

  // =========================
  // FETCH PROJECTS
  // =========================
  const fetchProjects = async () => {
    try {

      const res = await axios.get('/projects/');

      console.log("PROJECT API RESPONSE:", res.data);

      const projectList = res.data?.data?.projects || [];

      setProjects(Array.isArray(projectList) ? projectList : []);

    } catch (err) {

      console.log(err.response?.data);
      toast.error('Failed to load projects');

    }
  };

  // =========================
  // SUBMIT INVOICE
  // =========================
  const handleSubmit = async (e) => {

    e.preventDefault();

    if (!form.client) {
      toast.error('Select a client');
      return;
    }

    if (!form.amount) {
      toast.error('Enter invoice amount');
      return;
    }

    setLoading(true);

    try {

      // CREATE INVOICE
      const res = await axios.post('/invoices/', {
        client: form.client,
        project: form.project || null,
        due_date: form.due_date,
        status: form.status,
        amount: Number(form.amount),
        tax: 0
      });

      console.log("INVOICE RESPONSE:", res.data);

      const invoiceId = res.data?.id;

      if (!invoiceId) {
        toast.error("Invoice ID not found");
        return;
      }

      toast.success('Invoice created successfully!');

      // DOWNLOAD PDF
      const pdf = await axios.get(
        `/invoices/${invoiceId}/download/`,
        { responseType: "blob" }
      );

      const url = window.URL.createObjectURL(new Blob([pdf.data]));

      const link = document.createElement("a");
      link.href = url;
      link.download = `invoice-${invoiceId}.pdf`;

      document.body.appendChild(link);
      link.click();

      router.push('/organization/invoices');

    } catch (err) {

      console.log("FULL ERROR:", err.response?.data);

      toast.error(
        err.response?.data?.message || "Failed to create invoice"
      );

    } finally {

      setLoading(false);

    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">

      <h1 className="text-2xl font-bold">Create Invoice</h1>

      <Card className="p-6">

        <form onSubmit={handleSubmit} className="space-y-5">

          {/* CLIENT */}
          <div>
            <label className="block text-sm font-medium mb-1">
              Client
            </label>

            <select
              value={form.client}
              onChange={(e) =>
                setForm({ ...form, client: e.target.value })
              }
              className="w-full px-3 py-2 rounded-lg border"
            >

              <option value="">Select Client</option>

              {clients.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}

            </select>
          </div>

          {/* PROJECT */}
          <div>
            <label className="block text-sm font-medium mb-1">
              Project
            </label>

            <select
              value={form.project}
              onChange={(e) =>
                setForm({ ...form, project: e.target.value })
              }
              className="w-full px-3 py-2 border rounded-lg"
            >

              <option value="">Select Project</option>

              {projects.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}

            </select>
          </div>

          <InputField
            type="date"
            label="Due Date"
            value={form.due_date}
            onChange={(e) =>
              setForm({ ...form, due_date: e.target.value })
            }
          />

          {/* STATUS */}
          <div>
            <label className="block text-sm font-medium mb-1">
              Status
            </label>

            <select
              value={form.status}
              onChange={(e) =>
                setForm({ ...form, status: e.target.value })
              }
              className="w-full px-3 py-2 rounded-lg border"
            >

              <option value="DRAFT">Draft</option>
              <option value="SENT">Sent</option>
              <option value="PAID">Paid</option>
              <option value="OVERDUE">Overdue</option>

            </select>
          </div>

          {/* AMOUNT */}
          <InputField
            type="number"
            label="Amount"
            value={form.amount}
            onChange={(e) =>
              setForm({ ...form, amount: e.target.value })
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
              Create Invoice
            </Button>

          </div>

        </form>

      </Card>

    </div>
  );
}