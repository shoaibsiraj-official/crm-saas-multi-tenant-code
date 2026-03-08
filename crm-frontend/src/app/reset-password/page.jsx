'use client';

export const dynamic = "force-dynamic";

import { useState } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';

import AuthCard from '../components/ui/AuthCard';
import InputField from '../components/ui/InputField';
import Button from '../components/ui/Button';

import { resetPassword } from '../../lib/auth';

import toast from 'react-hot-toast';
import { Lock, CheckCircle } from 'lucide-react';

export default function ResetPasswordPage() {
  const searchParams = useSearchParams();

  const uid = searchParams?.get('uid');
  const token = searchParams?.get('token');

  const [loading, setLoading] = useState(false);
  const [reset, setReset] = useState(false);

  const [formData, setFormData] = useState({
    password: '',
    confirmPassword: '',
  });

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (formData.password !== formData.confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }

    setLoading(true);

    try {
      await resetPassword(uid, token, formData.password);
      setReset(true);
      toast.success('Password reset successfully!');
    } catch (error) {
      toast.error(error?.response?.data?.message || 'Failed to reset password');
    } finally {
      setLoading(false);
    }
  };

  if (reset) {
    return (
      <AuthCard>
        <div className="text-center">
          <div className="mx-auto w-12 h-12 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mb-4">
            <CheckCircle className="h-6 w-6 text-green-600" />
          </div>

          <h1 className="text-xl font-bold">Password Reset</h1>

          <p className="text-slate-500 dark:text-slate-400 mt-2 text-sm">
            Your password has been successfully reset. You can now log in with
            your new password.
          </p>

          <Link href="/login" className="block mt-6">
            <Button className="w-full">Continue to Login</Button>
          </Link>
        </div>
      </AuthCard>
    );
  }

  return (
    <AuthCard>
      <div className="mb-8 text-center">
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
          Set new password
        </h1>

        <p className="text-slate-500 dark:text-slate-400 mt-2 text-sm">
          Your new password must be different from previously used passwords.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <InputField
          label="New Password"
          type="password"
          icon={Lock}
          value={formData.password}
          onChange={(e) =>
            setFormData({ ...formData, password: e.target.value })
          }
          required
        />

        <InputField
          label="Confirm Password"
          type="password"
          icon={Lock}
          value={formData.confirmPassword}
          onChange={(e) =>
            setFormData({ ...formData, confirmPassword: e.target.value })
          }
          required
        />

        <Button type="submit" className="w-full mt-6" isLoading={loading}>
          Reset Password
        </Button>
      </form>
    </AuthCard>
  );
}