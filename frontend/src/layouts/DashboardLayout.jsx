import React from 'react';
import { Outlet, NavLink, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
    LayoutDashboard,
    UploadCloud,
    LineChart,
    Settings,
    LogOut,
    Menu,
    X,
    Bot,
    Users,
    Shield
} from 'lucide-react';
import { Button } from '../components/ui/Button';
import { cn } from '../lib/utils';
import { motion, AnimatePresence } from 'framer-motion';

const SidebarItem = ({ to, icon: Icon, label, onClick }) => {
    const location = useLocation();
    const isActive = location.pathname.startsWith(to);

    return (
        <NavLink
            to={to}
            className={({ isActive }) => cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group text-sm font-medium",
                isActive
                    ? "bg-primary text-primary-foreground shadow-md shadow-primary/20"
                    : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
            )}
            onClick={onClick}
        >
            <Icon size={18} />
            <span>{label}</span>
        </NavLink>
    )
}

const DashboardLayout = () => {
    const { user, logout } = useAuth();
    const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);

    // Check if current user is admin
    const userRole = user?.role || user?.user?.role;
    const isAdmin = userRole === 'admin';

    const navItems = [
        { to: '/dashboard', icon: LayoutDashboard, label: 'Overview' },
        { to: '/upload', icon: UploadCloud, label: 'Ingestion Hub' },
        { to: '/insights', icon: LineChart, label: 'Insights AI' },
        { to: '/settings', icon: Settings, label: 'Settings' },
    ];

    // Add admin-only items
    if (isAdmin) {
        navItems.push(
            { to: '/users', icon: Users, label: 'User Management' },
            { to: '/rules', icon: Shield, label: 'Rules Management' }
        );
    }

    return (
        <div className="min-h-screen bg-background flex text-foreground">

            {/* Mobile Overlay */}
            <AnimatePresence>
                {mobileMenuOpen && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 z-40 bg-black/50 lg:hidden backdrop-blur-sm"
                        onClick={() => setMobileMenuOpen(false)}
                    />
                )}
            </AnimatePresence>

            {/* Sidebar */}
            <motion.aside
                className={cn(
                    "fixed lg:static inset-y-0 left-0 z-50 w-64 bg-card border-r border-border flex flex-col transition-transform duration-300 transform lg:transform-none",
                    mobileMenuOpen ? "translate-x-0" : "-translate-x-full"
                )}
            >
                <div className="h-16 flex items-center px-6 border-b border-border">
                    <Bot className="text-primary mr-2" size={24} />
                    <span className="font-bold text-xl tracking-tight">Elecantro</span>
                </div>

                <nav className="flex-1 p-4 space-y-1">
                    <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2 px-2">Menu</div>
                    {navItems.map((item) => (
                        <SidebarItem key={item.to} {...item} onClick={() => setMobileMenuOpen(false)} />
                    ))}
                </nav>

                <div className="p-4 border-t border-border">
                    <div className="flex items-center gap-3 mb-4 px-2">
                        <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold">
                            {user?.username?.charAt(0).toUpperCase()}
                        </div>
                        <div className="flex-1 overflow-hidden">
                            <p className="text-sm font-medium truncate">{user?.username}</p>
                            <p className="text-xs text-muted-foreground truncate">{user?.email}</p>
                        </div>
                    </div>
                    <Button variant="outline" className="w-full justify-start text-muted-foreground" size="sm" onClick={logout}>
                        <LogOut size={16} className="mr-2" />
                        Sign Out
                    </Button>
                </div>
            </motion.aside>

            {/* Main Content */}
            <main className="flex-1 flex flex-col min-h-screen overflow-hidden">
                {/* Mobile Header */}
                <header className="lg:hidden h-16 flex items-center px-4 border-b border-border bg-background/80 backdrop-blur-md sticky top-0 z-30">
                    <Button variant="ghost" size="icon" onClick={() => setMobileMenuOpen(true)}>
                        <Menu size={24} />
                    </Button>
                    <span className="ml-4 font-bold text-lg">Elecantro</span>
                </header>

                {/* Page Content */}
                <div className="flex-1 overflow-auto p-4 lg:p-8 relative">
                    <Outlet />
                </div>
            </main>

        </div>
    );
};

export default DashboardLayout;
