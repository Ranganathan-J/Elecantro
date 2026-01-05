import React from 'react';
import { useAuth } from '../context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { User, Mail, Building, Shield, LogOut } from 'lucide-react';

const Settings = () => {
    const { user, logout } = useAuth();

    if (!user) return null;

    return (
        <div className="space-y-6 max-w-4xl mx-auto">
            <div>
                <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
                <p className="text-muted-foreground mt-1">Manage your account and preferences.</p>
            </div>

            <div className="grid gap-6">
                {/* Profile Card */}
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <User size={20} />
                            Profile Information
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="space-y-1">
                                <label className="text-xs font-semibold text-muted-foreground uppercase">Username</label>
                                <div className="flex items-center gap-2 p-3 bg-secondary/30 rounded-lg border">
                                    <User size={16} className="text-muted-foreground" />
                                    <span className="font-medium">{user.username}</span>
                                </div>
                            </div>
                            <div className="space-y-1">
                                <label className="text-xs font-semibold text-muted-foreground uppercase">Email Address</label>
                                <div className="flex items-center gap-2 p-3 bg-secondary/30 rounded-lg border">
                                    <Mail size={16} className="text-muted-foreground" />
                                    <span className="font-medium">{user.email || 'N/A'}</span>
                                </div>
                            </div>
                            <div className="space-y-1">
                                <label className="text-xs font-semibold text-muted-foreground uppercase">Role</label>
                                <div className="flex items-center gap-2 p-3 bg-secondary/30 rounded-lg border">
                                    <Shield size={16} className="text-muted-foreground" />
                                    <span className="font-medium capitalize">{user.role || 'User'}</span>
                                </div>
                            </div>
                            <div className="space-y-1">
                                <label className="text-xs font-semibold text-muted-foreground uppercase">Company</label>
                                <div className="flex items-center gap-2 p-3 bg-secondary/30 rounded-lg border">
                                    <Building size={16} className="text-muted-foreground" />
                                    <span className="font-medium">{user.company || 'Not specified'}</span>
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* Account Actions */}
                <Card className="border-destructive/20">
                    <CardHeader>
                        <CardTitle className="text-destructive">Danger Zone</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p className="text-sm text-muted-foreground mb-4">
                            Log out of your account to end your current session.
                        </p>
                        <Button
                            variant="destructive"
                            className="gap-2"
                            onClick={logout}
                        >
                            <LogOut size={16} />
                            Sign Out
                        </Button>
                    </CardContent>
                </Card>
            </div>

            <div className="text-center text-xs text-muted-foreground py-8">
                Elecantro AI Analytics v1.0.0
            </div>
        </div>
    );
};

export default Settings;
