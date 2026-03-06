'use client';
import { useState } from 'react';
import Link from 'next/link';
import AuthCard from '../components/ui/AuthCard';
import InputField from '../components/ui/InputField';
import Button from '../components/ui/Button';
import { forgotPassword } from '../../lib/auth';
import toast from 'react-hot-toast';
import { Mail, ArrowLeft } from 'lucide-react';

export default function ForgotPasswordPage() {
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await forgotPassword(email);
      setSubmitted(true);
      toast.success('Reset link sent!');
    } catch (error) {
      toast.error(error.response?.data?.message || 'Error sending reset link');
    } finally {
      setLoading(false);
    }
  };

  if (submitted) {
    return (
      <AuthCard>
        <div className="text-center">
          <div className="mx-auto w-12 h-12 bg-primary-100 dark:bg-primary-900/30 rounded-full flex items-center justify-center mb-4">
            <Mail className="h-6 w-6 text-primary-600" />
          </div>
          <h1 className="text-xl font-bold">Check your email</h1>
          <p className="text-slate-500 dark:text-slate-400 mt-2 text-sm">
            We sent a password reset link to <span className="font-medium">{email}</span>
          </p>
          <Link href="/login" className="block mt-6">
            <Button variant="outline" className="w-full">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Login
            </Button>
          </Link>
        </div>
      </AuthCard>
    );
  }

  return (
    <AuthCard>
      <div className="mb-8 text-center">
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Forgot password?</h1>
        <p className="text-slate-500 dark:text-slate-400 mt-2 text-sm">
          No worries, we'll send you reset instructions.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        <InputField 
          label="Email" 
          type="email" 
          icon={Mail}
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required 
        />
        <Button type="submit" className="w-full" isLoading={loading}>
          Reset Password
        </Button>
      </form>

      <Link href="/login" className="flex items-center justify-center mt-6 text-sm text-slate-600 hover:text-slate-900 dark:text-slate-400">
        <ArrowLeft className="h-4 w-4 mr-2" />
        Back to login
      </Link>
    </AuthCard>
  );
}