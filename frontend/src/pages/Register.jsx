import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Bot, CheckCircle } from 'lucide-react';
import { motion } from 'framer-motion';

const Register = () => {
    const { register: registerUser } = useAuth();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);

    const { register, handleSubmit, watch, formState: { errors } } = useForm();

    const onSubmit = async (data) => {
        setLoading(true);

        const payload = {
            username: data.username,
            email: data.email,
            password: data.password,
            password_confirm: data.password_confirm,
            first_name: data.first_name,
            last_name: data.last_name,
            company: data.company,
            role: 'admin' // Defaulting to admin for this demo
        };

        const result = await registerUser(payload);
        setLoading(false);

        if (result.success) {
            navigate('/login');
        } else {
            // Display backend error (often an object like { username: [...] })
            const msg = typeof result.error === 'object'
                ? Object.values(result.error).flat().join(', ')
                : result.error;
            alert(msg);
        }
    };

    return (
        <div className="min-h-screen bg-background text-foreground flex items-center justify-center p-4 relative overflow-hidden">
            {/* Background Ambience */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-[-20%] right-[-10%] w-[600px] h-[600px] bg-primary/10 rounded-full blur-[100px]" />
                <div className="absolute bottom-[-20%] left-[-10%] w-[500px] h-[500px] bg-accent/10 rounded-full blur-[100px]" />
            </div>

            <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, type: "spring" }}
                className="w-full max-w-lg bg-card border border-border rounded-xl shadow-2xl overflow-hidden z-10"
            >
                <div className="p-8 md:p-12">
                    <div className="flex flex-col items-center mb-8">
                        <div className="h-12 w-12 rounded-xl bg-primary/20 flex items-center justify-center border border-primary/50 mb-4">
                            <Bot size={24} className="text-primary" />
                        </div>
                        <h2 className="text-3xl font-bold">Create Account</h2>
                        <p className="text-muted-foreground mt-2">Start your 14-day free trial</p>
                    </div>

                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <label className="text-sm font-medium">First Name</label>
                                <Input
                                    {...register("first_name", { required: "Required" })}
                                    placeholder="John"
                                    error={errors.first_name?.message}
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-medium">Last Name</label>
                                <Input
                                    {...register("last_name", { required: "Required" })}
                                    placeholder="Doe"
                                    error={errors.last_name?.message}
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-medium">Username</label>
                            <Input
                                {...register("username", { required: "Username is required", minLength: { value: 3, message: "Min 3 chars" } })}
                                placeholder="johndoe"
                                error={errors.username?.message}
                            />
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-medium">Work Email</label>
                            <Input
                                {...register("email", {
                                    required: "Email is required",
                                    pattern: { value: /\S+@\S+\.\S+/, message: "Invalid email" }
                                })}
                                placeholder="name@company.com"
                                error={errors.email?.message}
                            />
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-medium">Company Name</label>
                            <Input
                                {...register("company", { required: "Company is required" })}
                                placeholder="Acme Corp"
                                error={errors.company?.message}
                            />
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <label className="text-sm font-medium">Password</label>
                                <Input
                                    type="password"
                                    {...register("password", { required: "Password is required", minLength: { value: 6, message: "Min 6 chars" } })}
                                    placeholder="••••••••"
                                    error={errors.password?.message}
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-medium">Confirm</label>
                                <Input
                                    type="password"
                                    {...register("password_confirm", {
                                        required: "Confirm is required",
                                        validate: (val) => {
                                            if (watch('password') != val) {
                                                return "Passwords do not match";
                                            }
                                        }
                                    })}
                                    placeholder="••••••••"
                                    error={errors.password_confirm?.message}
                                />
                            </div>
                        </div>

                        <div className="pt-2">
                            <Button type="submit" className="w-full" size="lg" loading={loading}>
                                Get Started
                            </Button>
                        </div>
                    </form>

                    <div className="mt-6 text-center text-sm text-muted-foreground">
                        Already have an account? <Link to="/login" className="text-primary hover:underline">Sign in</Link>
                    </div>
                </div>

                {/* Footer features */}
                <div className="bg-muted/30 p-6 flex justify-around text-xs text-muted-foreground border-t border-border">
                    <div className="flex items-center gap-2"><CheckCircle size={14} className="text-green-500" /> No credit card</div>
                    <div className="flex items-center gap-2"><CheckCircle size={14} className="text-green-500" /> 14-day trial</div>
                    <div className="flex items-center gap-2"><CheckCircle size={14} className="text-green-500" /> Cancel anytime</div>
                </div>
            </motion.div>
        </div>
    );
};

export default Register;
