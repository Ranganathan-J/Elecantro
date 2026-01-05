import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Bot, LineChart, ShieldCheck } from 'lucide-react';
import { motion } from 'framer-motion';

const Login = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const { register, handleSubmit, formState: { errors } } = useForm();

  const onSubmit = async (data) => {
    setLoading(true);
    const result = await login(data.email, data.password);
    setLoading(false);

    if (result.success) {
      navigate('/dashboard');
    } else {
      alert(result.error); // TODO: Replace with nice toast
    }
  };

  return (
    <div className="min-h-screen grid lg:grid-cols-2 bg-background text-foreground overflow-hidden">
      {/* Left: Hero Section */}
      <div className="hidden lg:flex flex-col justify-center items-center bg-slate-900 border-r border-slate-800 p-12 relative overflow-hidden">
        {/* Background Gradients */}
        <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-primary/20 via-background to-background opacity-50" />
        <div className="absolute bottom-0 right-0 w-1/2 h-1/2 bg-[radial-gradient(ellipse_at_bottom_right,_var(--tw-gradient-stops))] from-accent/20 via-background to-background opacity-50" />

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="relative z-10 max-w-lg text-center"
        >
          <div className="flex justify-center mb-8">
            <div className="h-20 w-20 rounded-2xl bg-primary/20 flex items-center justify-center border border-primary/50 shadow-[0_0_30px_rgba(124,58,237,0.3)]">
              <Bot size={40} className="text-primary" />
            </div>
          </div>
          <h1 className="text-4xl font-bold tracking-tight mb-4">
            Analysis at <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-purple-400">Wrapspeed</span>
          </h1>
          <p className="text-lg text-muted-foreground mb-8">
            Ingest thousands of reviews in seconds. Let our AI uncover hidden insights while you sleep.
          </p>

          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 rounded-lg bg-white/5 border border-white/10 backdrop-blur-sm">
              <LineChart className="mb-2 text-blue-400" />
              <h3 className="font-semibold">Real-time Stats</h3>
              <p className="text-xs text-muted-foreground">Monitor trends instantly</p>
            </div>
            <div className="p-4 rounded-lg bg-white/5 border border-white/10 backdrop-blur-sm">
              <ShieldCheck className="mb-2 text-green-400" />
              <h3 className="font-semibold">Enterprise Grade</h3>
              <p className="text-xs text-muted-foreground">Secure & Scalable</p>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Right: Login Form */}
      <div className="flex items-center justify-center p-8">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="w-full max-w-md space-y-8"
        >
          <div className="text-center lg:text-left">
            <h2 className="text-3xl font-bold">Welcome back</h2>
            <p className="text-muted-foreground mt-2">Enter your credentials to access your workspace.</p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6 mt-8">
            <div className="space-y-2">
              <label className="text-sm font-medium">Email</label>
              <Input
                {...register("email", { required: "Email is required" })}
                placeholder="name@company.com"
                error={errors.email?.message}
              />
            </div>

            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <label className="text-sm font-medium">Password</label>
                <Link to="/forgot-password" className="text-xs text-primary hover:underline">Forgot password?</Link>
              </div>
              <Input
                type="password"
                {...register("password", { required: "Password is required" })}
                placeholder="••••••••"
                error={errors.password?.message}
              />
            </div>

            <Button type="submit" className="w-full" size="lg" loading={loading}>
              Sign In
            </Button>
          </form>

          <div className="text-center text-sm">
            Don't have an account?{' '}
            <Link to="/register" className="font-medium text-primary hover:underline transition-colors">
              Create an account
            </Link>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Login;
