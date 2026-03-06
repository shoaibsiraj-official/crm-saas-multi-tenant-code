'use client';
import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import AuthCard from '../components/ui/AuthCard';
import InputField from '../components/ui/InputField';
import Button from '../components/ui/Button';
import { login } from '../../lib/auth';
import toast from 'react-hot-toast';
import { Mail, Lock } from 'lucide-react';

export default function LoginPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [errors, setErrors] = useState({});

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await login(formData.email, formData.password);

      toast.success("Login successful 🚀");

      // 🔥 Invite Flow Check
      const searchParams = new URLSearchParams(window.location.search);
      const inviteToken = searchParams.get("invite");

      if (inviteToken) {
        router.push(`/accept-invite/${inviteToken}`);
      } else {
        router.push("/dashboard");
      }

    } catch (err) {
      toast.error("Login failed ❌");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthCard>
      <div className="mb-8 text-center">
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
          Welcome back
        </h1>
        <p className="text-slate-500 dark:text-slate-400 mt-2">
          Sign in to your account
        </p>
      </div>

      {/* ✅ FIXED HERE */}
      <form onSubmit={handleLogin} className="space-y-5">

        <InputField 
          label="Email" 
          type="email" 
          icon={Mail}
          value={formData.email}
          onChange={(e) => 
            setFormData({ ...formData, email: e.target.value })
          }
          error={errors.email}
          required 
        />

        <InputField 
          label="Password" 
          type="password" 
          icon={Lock}
          value={formData.password}
          onChange={(e) => 
            setFormData({ ...formData, password: e.target.value })
          }
          error={errors.password}
          required 
        />

        <div className="flex items-center justify-end">
          <Link 
            href="/forgot-password" 
            className="text-sm text-primary-600 hover:text-primary-700 dark:text-primary-400"
          >
            Forgot password?
          </Link>
        </div>

        <Button type="submit" className="w-full" isLoading={loading}>
          Sign In
        </Button>
      </form>

      <div className="mt-6 text-center text-sm text-slate-600 dark:text-slate-400">
        Don't have an account?{' '}
        <Link 
          href="/register" 
          className="font-medium text-primary-600 hover:text-primary-500"
        >
          Sign up
        </Link>
      </div>
    </AuthCard>
  );
}