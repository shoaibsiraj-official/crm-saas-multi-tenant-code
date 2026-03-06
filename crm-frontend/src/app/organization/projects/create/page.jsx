'use client';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { createProject } from '@/lib/project';
import { getMembers } from '@/lib/organization';
import { getClients } from '@/lib/client';   // ✅ ADDED
import Card from '@/app/components/ui/Card';
import Button from '@/app/components/ui/Button';
import InputField from '@/app/components/ui/InputField';
import toast from 'react-hot-toast';

export default function CreateProjectPage() {
    const router = useRouter();
    const [loading, setLoading] = useState(false);
    const [members, setMembers] = useState([]);
    const [clients, setClients] = useState([]);   // ✅ ADDED

    const [form, setForm] = useState({
        name: '',
        description: '',
        start_date: '',
        deadline: '',
        status: 'ACTIVE',
        members: [],
        client: null,    // ✅ ADDED
    });

    useEffect(() => {
        // Load members
        getMembers()
            .then(setMembers)
            .catch(() => toast.error('Could not load members'));

        // Load clients
        getClients()
            .then(res => {
                console.log("Clients API:", res)
                setClients(res.results || res.data?.results || res || [])
            })
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!form.name) {
            return toast.error('Project name is required');
        }

        setLoading(true);

        try {
            const payload = {
                name: form.name,
                description: form.description,
                status: form.status.toUpperCase(),
                client: form.client,   // ✅ SEND CLIENT
            };

            const res = await createProject(payload);

            toast.success('Project created!');
            router.push(`/organization/projects/${res.id}`);
        } catch (err) {
            toast.error(
                err.response?.data?.message || 'Error creating project'
            );
        } finally {
            setLoading(false);
        }
    };

    const toggleMember = (id) => {
        setForm(prev => ({
            ...prev,
            members: prev.members.includes(id)
                ? prev.members.filter(m => m !== id)
                : [...prev.members, id]
        }));
    };

    return (
        <div className="max-w-2xl mx-auto">
            <Card className="p-8">
                <h1 className="text-2xl font-bold mb-6 text-slate-900 dark:text-white">
                    Create New Project
                </h1>

                <form onSubmit={handleSubmit} className="space-y-5">

                    {/* Project Name */}
                    <InputField
                        label="Project Name"
                        required
                        value={form.name}
                        onChange={e =>
                            setForm({ ...form, name: e.target.value })
                        }
                    />

                    {/* Description */}
                    <div>
                        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                            Description
                        </label>
                        <textarea
                            rows={3}
                            className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 focus:ring-2 focus:ring-indigo-500 outline-none"
                            value={form.description}
                            onChange={e =>
                                setForm({ ...form, description: e.target.value })
                            }
                        />
                    </div>

                    {/* Client Dropdown ✅ */}
                    <div>
                        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                            Client
                        </label>

                        <select
                            value={form.client || ""}
                            onChange={(e) =>
                                setForm({
                                    ...form,
                                    client: e.target.value || null,
                                })
                            }
                            className="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 focus:ring-2 focus:ring-indigo-500 outline-none"
                        >
                            <option value="">No Client</option>

                            {clients.map((c) => (
                                <option key={c.id} value={c.id}>
                                    {c.name}
                                </option>
                            ))}
                        </select>
                    </div>

                    {/* Dates */}
                    <div className="grid grid-cols-2 gap-4">
                        <InputField
                            type="date"
                            label="Start Date"
                            value={form.start_date}
                            onChange={e =>
                                setForm({ ...form, start_date: e.target.value })
                            }
                        />
                        <InputField
                            type="date"
                            label="Deadline"
                            value={form.deadline}
                            onChange={e =>
                                setForm({ ...form, deadline: e.target.value })
                            }
                        />
                    </div>

                    {/* Assign Members */}
                    <div>
                        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                            Assign Members
                        </label>

                        <div className="flex flex-wrap gap-2 p-3 border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 max-h-40 overflow-y-auto">
                            {members.map(m => (
                                <button
                                    type="button"
                                    key={m.id}
                                    onClick={() => toggleMember(m.id)}
                                    className={`px-3 py-1 text-xs rounded-full transition-colors ${form.members.includes(m.id)
                                        ? 'bg-indigo-600 text-white'
                                        : 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-600'
                                        }`}
                                >
                                    {m.full_name || m.email}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Buttons */}
                    <div className="pt-4 flex justify-end gap-3">
                        <Button
                            variant="secondary"
                            type="button"
                            onClick={() => router.back()}
                        >
                            Cancel
                        </Button>

                        <Button type="submit" isLoading={loading}>
                            Create Project
                        </Button>
                    </div>
                </form>
            </Card>
        </div>
    );
}