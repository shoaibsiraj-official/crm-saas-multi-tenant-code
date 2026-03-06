'use client';

import { useState } from 'react';
import Modal from '../ui/Modal';
import Button from '../ui/Button';
import InputField from '../ui/InputField';

export default function InviteModal({ isOpen, onClose, onSubmit }) {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    role: 'MEMBER',   // ✅ match backend format
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // ✅ Pass email + role separately
      await onSubmit(formData.email, formData.role);

      setFormData({ email: '', role: 'MEMBER' });
    } catch (error) {
      // error handled in parent via toast
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Invite Team Member">
      <form onSubmit={handleSubmit} className="space-y-5">
        
        <InputField
          label="Email Address"
          type="email"
          required
          value={formData.email}
          onChange={(e) =>
            setFormData({ ...formData, email: e.target.value })
          }
          placeholder="colleague@company.com"
        />

        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
            Role
          </label>

          <select
            value={formData.role}
            onChange={(e) =>
              setFormData({ ...formData, role: e.target.value })
            }
            className="w-full px-3 py-2.5 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 focus:ring-2 focus:ring-brand-500 outline-none text-sm"
          >
            {/* ✅ Use backend-valid roles */}
            <option value="MEMBER">Member</option>
            <option value="ORG_ADMIN">Admin</option>
          </select>
        </div>

        <div className="pt-4 flex justify-end gap-3">
          <Button
            variant="secondary"
            onClick={onClose}
            type="button"
          >
            Cancel
          </Button>

          <Button type="submit" isLoading={loading}>
            Send Invite
          </Button>
        </div>
      </form>
    </Modal>
  );
}