'use client';
import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import AuthCard from '../components/ui/AuthCard';
import InputField from '../components/ui/InputField';
import Button from '../components/ui/Button';
import { register } from '../../lib/auth';
import toast from 'react-hot-toast';
import { Mail, Lock, User } from 'lucide-react';

export default function RegisterPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({ name: '', email: '', password: '', confirmPassword: '' });
  const [errors, setErrors] = useState({});

const handleSubmit = async (e) => {
  e.preventDefault();

  if (formData.password !== formData.confirmPassword) {
    setErrors({ password_confirm: "Passwords do not match" });
    return;
  }

  setLoading(true);

  // Split full name into first + last
  const nameParts = formData.name.trim().split(" ");
  const first_name = nameParts[0] || "";
  const last_name = nameParts.slice(1).join(" ") || "";

  try {
    await register({
      email: formData.email,
      password: formData.password,
      password_confirm: formData.confirmPassword,
      first_name,
      last_name,
    });

    toast.success("Account created successfully!");
    router.push("/login");
  } catch (error) {
    const message = error.response?.data?.message || "Registration failed";
    const details = error.response?.data?.errors;

    if (details) setErrors(details);
    toast.error(message);
  } finally {
    setLoading(false);
  }
};
  return (
    <AuthCard>
      <div className="mb-8 text-center">
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Create an account</h1>
        <p className="text-slate-500 dark:text-slate-400 mt-2">Start your 30-day free trial</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <InputField 
          label="Full Name" 
          icon={User}
          value={formData.name}
          onChange={(e) => setFormData({...formData, name: e.target.value})}
          error={errors.name}
          required 
        />
        <InputField 
          label="Email" 
          type="email" 
          icon={Mail}
          value={formData.email}
          onChange={(e) => setFormData({...formData, email: e.target.value})}
          error={errors.email}
          required 
        />
        <InputField 
          label="Password" 
          type="password" 
          icon={Lock}
          value={formData.password}
          onChange={(e) => setFormData({...formData, password: e.target.value})}
          error={errors.password}
          required 
        />
        <InputField 
          label="Confirm Password" 
          type="password" 
          icon={Lock}
          value={formData.confirmPassword}
          onChange={(e) => setFormData({...formData, confirmPassword: e.target.value})}
          error={errors.confirmPassword} 
          required 
        />

        <Button type="submit" className="w-full mt-6" isLoading={loading}>
          Create Account
        </Button>
      </form>

      <p className="mt-6 text-center text-sm text-slate-600 dark:text-slate-400">
        Already have an account?{' '}
        <Link href="/login" className="font-medium text-primary-600 hover:text-primary-500">
          Sign in
        </Link>
      </p>
    </AuthCard>
  );
}