import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { userService } from '../services/userService';
import { rulesService } from '../services/rulesService';
import { useAuth } from '../context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Users,
  Shield,
  UserCheck,
  Eye,
  Trash2,
  ChevronDown,
  ChevronUp,
  Search,
  AlertCircle,
  CheckCircle,
  XCircle,
  Loader2,
  Settings,
  Play,
  AlertTriangle
} from 'lucide-react';
import { cn } from '../lib/utils';

const ROLE_COLORS = {
  admin: 'bg-red-500/10 text-red-500 border-red-500/20',
  analyst: 'bg-blue-500/10 text-blue-500 border-blue-500/20',
  viewer: 'bg-gray-500/10 text-gray-500 border-gray-500/20'
};

const ROLE_ICONS = {
  admin: Shield,
  analyst: UserCheck,
  viewer: Eye
};

const UserManagement = () => {
  const { user: currentUser } = useAuth();
  const queryClient = useQueryClient();
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedUser, setExpandedUser] = useState(null);
  const [selectedRole, setSelectedRole] = useState({});
  const [showRulesPanel, setShowRulesPanel] = useState(false);

  // Check if current user is admin - handle both direct and nested user objects
  const userRole = currentUser?.role || currentUser?.user?.role;
  const isAdmin = userRole === 'admin';
  
  // Fetch all users
  const { data: users = [], isLoading, error } = useQuery({
    queryKey: ['users'],
    queryFn: userService.getAllUsers,
    enabled: isAdmin, // Only fetch if admin
    refetchInterval: 30000 // Refetch every 30 seconds
  });

  // Fetch all rules
  const { data: rules = [] } = useQuery({
    queryKey: ['rules'],
    queryFn: rulesService.getAllRules,
    enabled: isAdmin,
    refetchInterval: 60000 // Refetch every minute
  });

  // Promote user mutation
  const promoteMutation = useMutation({
    mutationFn: ({ userId, role }) => userService.promoteUser(userId, role),
    onSuccess: () => {
      queryClient.invalidateQueries(['users']);
      setSelectedRole({});
    }
  });

  // Demote user mutation
  const demoteMutation = useMutation({
    mutationFn: ({ userId, role }) => userService.demoteUser(userId, role),
    onSuccess: () => {
      queryClient.invalidateQueries(['users']);
      setSelectedRole({});
    }
  });

  // Delete user mutation
  const deleteMutation = useMutation({
    mutationFn: (userId) => userService.deleteUser(userId),
    onSuccess: () => {
      queryClient.invalidateQueries(['users']);
    }
  });

  // Apply rules mutation
  const applyRulesMutation = useMutation({
    mutationFn: (ruleIds) => rulesService.applyRules(ruleIds),
    onSuccess: () => {
      queryClient.invalidateQueries(['users']);
      queryClient.invalidateQueries(['rules']);
    }
  });

  // Filter users by search term
  const filteredUsers = users.filter(u =>
    u.username?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    u.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    u.role?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handlePromote = (userId, role) => {
    if (window.confirm(`Are you sure you want to promote this user to ${role}?`)) {
      promoteMutation.mutate({ userId, role });
    }
  };

  const handleDemote = (userId, role) => {
    if (window.confirm(`Are you sure you want to demote this user to ${role}?`)) {
      demoteMutation.mutate({ userId, role });
    }
  };

  const handleDelete = (userId, username) => {
    if (window.confirm(`Are you sure you want to delete user "${username}"? This action cannot be undone.`)) {
      deleteMutation.mutate(userId);
    }
  };

  const handleApplyRules = (ruleIds) => {
    if (window.confirm('Are you sure you want to apply the selected rules? This will modify user accounts based on the rule conditions.')) {
      applyRulesMutation.mutate(ruleIds);
    }
  };

  // Redirect if not admin
  if (!isAdmin) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Card className="max-w-md">
          <CardContent className="p-6 text-center">
            <AlertCircle className="mx-auto mb-4 text-destructive" size={48} />
            <h2 className="text-xl font-semibold mb-2">Access Denied</h2>
            <p className="text-muted-foreground">
              You need admin privileges to access this page.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Card className="max-w-md">
          <CardContent className="p-6 text-center">
            <XCircle className="mx-auto mb-4 text-destructive" size={48} />
            <h2 className="text-xl font-semibold mb-2">Error Loading Users</h2>
            <p className="text-muted-foreground">
              {error.response?.data?.error || 'Failed to load users'}
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Users className="text-primary" size={32} />
            User Management
          </h1>
          <p className="text-muted-foreground mt-1">
            Manage users, roles, and permissions
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            onClick={() => setShowRulesPanel(!showRulesPanel)}
            className="flex items-center gap-2"
          >
            <Settings size={16} />
            Rules ({rules.length})
          </Button>
          <div className="text-sm text-muted-foreground">
            {filteredUsers.length} {filteredUsers.length === 1 ? 'user' : 'users'}
          </div>
        </div>
      </div>

      {/* Rules Panel */}
      <AnimatePresence>
        {showRulesPanel && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings size={20} />
                  Active Rules
                </CardTitle>
              </CardHeader>
              <CardContent>
                {rules.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    No rules configured. <a href="/rules" className="text-primary hover:underline">Create rules</a> to automate user management.
                  </div>
                ) : (
                  <div className="space-y-3">
                    {rules.filter(rule => rule.status === 'active').map(rule => (
                      <div key={rule.id} className="flex items-center justify-between p-3 bg-secondary/30 rounded-lg">
                        <div className="flex-1">
                          <h4 className="font-medium">{rule.name}</h4>
                          <p className="text-sm text-muted-foreground">{rule.description}</p>
                        </div>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleApplyRules([rule.id])}
                          disabled={applyRulesMutation.isPending}
                        >
                          {applyRulesMutation.isPending ? (
                            <Loader2 className="animate-spin" size={16} />
                          ) : (
                            <Play size={16} />
                          )}
                        </Button>
                      </div>
                    ))}
                    <div className="pt-3 border-t border-border">
                      <Button
                        variant="outline"
                        className="w-full"
                        onClick={() => window.location.href = '/rules'}
                      >
                        <Settings size={16} className="mr-2" />
                        Manage All Rules
                      </Button>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Search Bar */}
      <Card>
        <CardContent className="p-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground" size={20} />
            <input
              type="text"
              placeholder="Search users by name, email, or role..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
        </CardContent>
      </Card>

      {/* Users List */}
      {isLoading ? (
        <div className="grid gap-4">
          {[1, 2, 3].map(i => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-6">
                <div className="h-20 bg-secondary rounded" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : filteredUsers.length === 0 ? (
        <Card>
          <CardContent className="p-12 text-center">
            <Users className="mx-auto mb-4 text-muted-foreground" size={48} />
            <h3 className="text-lg font-semibold mb-2">No users found</h3>
            <p className="text-muted-foreground">
              {searchTerm ? 'Try adjusting your search terms' : 'No users in the system'}
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          <AnimatePresence>
            {filteredUsers.map((user) => {
              const RoleIcon = ROLE_ICONS[user.role] || Eye;
              const isExpanded = expandedUser === user.id;
              const isCurrentUser = user.id === currentUser?.id;

              return (
                <motion.div
                  key={user.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                >
                  <Card className="group hover:border-primary/30 transition-all">
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        {/* User Info */}
                        <div className="flex items-center gap-4 flex-1">
                          <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
                            <Users className="text-primary" size={24} />
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                              <h3 className="font-semibold text-lg truncate">
                                {user.username}
                                {isCurrentUser && (
                                  <span className="ml-2 text-xs text-muted-foreground">(You)</span>
                                )}
                                {user.id === currentUser?.id && (
                                  <span className="ml-2 text-xs text-muted-foreground">(You)</span>
                                )}
                              </h3>
                            </div>
                            <p className="text-sm text-muted-foreground truncate">{user.email}</p>
                            <div className="flex items-center gap-2 mt-2">
                              <span className={cn(
                                "text-xs px-2 py-0.5 rounded-full capitalize border flex items-center gap-1",
                                ROLE_COLORS[user.role] || ROLE_COLORS.viewer
                              )}>
                                <RoleIcon size={12} />
                                {user.role}
                              </span>
                              {user.company && (
                                <span className="text-xs text-muted-foreground">
                                  • {user.company}
                                </span>
                              )}
                            </div>
                          </div>
                        </div>

                        {/* Actions */}
                        <div className="flex items-center gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setExpandedUser(isExpanded ? null : user.id)}
                          >
                            {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                          </Button>
                        </div>
                      </div>

                      {/* Expanded Actions */}
                      <AnimatePresence>
                        {isExpanded && (
                          <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: 'auto', opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            className="mt-4 pt-4 border-t border-border"
                          >
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                              {/* Promote to Admin */}
                              {user.role !== 'admin' && (
                                <div>
                                  <label className="text-sm font-medium mb-2 block">Promote to Admin</label>
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    className="w-full"
                                    onClick={() => handlePromote(user.id, 'admin')}
                                    disabled={promoteMutation.isPending || isCurrentUser}
                                  >
                                    {promoteMutation.isPending && selectedRole[user.id] === 'admin' ? (
                                      <Loader2 className="mr-2 animate-spin" size={16} />
                                    ) : (
                                      <Shield className="mr-2" size={16} />
                                    )}
                                    Make Admin
                                  </Button>
                                </div>
                              )}

                              {/* Promote to Analyst */}
                              {user.role === 'viewer' && (
                                <div>
                                  <label className="text-sm font-medium mb-2 block">Promote to Analyst</label>
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    className="w-full"
                                    onClick={() => handlePromote(user.id, 'analyst')}
                                    disabled={promoteMutation.isPending}
                                  >
                                    {promoteMutation.isPending && selectedRole[user.id] === 'analyst' ? (
                                      <Loader2 className="mr-2 animate-spin" size={16} />
                                    ) : (
                                      <UserCheck className="mr-2" size={16} />
                                    )}
                                    Make Analyst
                                  </Button>
                                </div>
                              )}

                              {/* Demote from Admin */}
                              {user.role === 'admin' && !isCurrentUser && (
                                <>
                                  <div>
                                    <label className="text-sm font-medium mb-2 block">Demote to Analyst</label>
                                    <Button
                                      variant="outline"
                                      size="sm"
                                      className="w-full"
                                      onClick={() => handleDemote(user.id, 'analyst')}
                                      disabled={demoteMutation.isPending}
                                    >
                                      {demoteMutation.isPending && selectedRole[user.id] === 'analyst' ? (
                                        <Loader2 className="mr-2 animate-spin" size={16} />
                                      ) : (
                                        <UserCheck className="mr-2" size={16} />
                                      )}
                                      Demote to Analyst
                                    </Button>
                                  </div>
                                  <div>
                                    <label className="text-sm font-medium mb-2 block">Demote to Viewer</label>
                                    <Button
                                      variant="outline"
                                      size="sm"
                                      className="w-full"
                                      onClick={() => handleDemote(user.id, 'viewer')}
                                      disabled={demoteMutation.isPending}
                                    >
                                      {demoteMutation.isPending && selectedRole[user.id] === 'viewer' ? (
                                        <Loader2 className="mr-2 animate-spin" size={16} />
                                      ) : (
                                        <Eye className="mr-2" size={16} />
                                      )}
                                      Demote to Viewer
                                    </Button>
                                  </div>
                                </>
                              )}

                              {/* Delete User */}
                              {!isCurrentUser && (
                                <div className={cn(
                                  "md:col-span-2",
                                  user.role === 'admin' ? "md:col-span-1" : ""
                                )}>
                                  <label className="text-sm font-medium mb-2 block text-destructive">Danger Zone</label>
                                  <Button
                                    variant="destructive"
                                    size="sm"
                                    className="w-full"
                                    onClick={() => handleDelete(user.id, user.username)}
                                    disabled={deleteMutation.isPending}
                                  >
                                    {deleteMutation.isPending ? (
                                      <Loader2 className="mr-2 animate-spin" size={16} />
                                    ) : (
                                      <Trash2 className="mr-2" size={16} />
                                    )}
                                    Delete User
                                  </Button>
                                </div>
                              )}
                            </div>

                            {/* User Details */}
                            <div className="mt-4 pt-4 border-t border-border text-sm text-muted-foreground">
                              <div className="grid grid-cols-2 gap-2">
                                <div>
                                  <span className="font-medium">Joined:</span>{' '}
                                  {user.date_joined ? new Date(user.date_joined).toLocaleDateString() : 'N/A'}
                                </div>
                                <div>
                                  <span className="font-medium">Last Login:</span>{' '}
                                  {user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}
                                </div>
                                {user.first_name && (
                                  <div>
                                    <span className="font-medium">Name:</span>{' '}
                                    {user.first_name} {user.last_name || ''}
                                  </div>
                                )}
                                {user.phone && (
                                  <div>
                                    <span className="font-medium">Phone:</span> {user.phone}
                                  </div>
                                )}
                              </div>
                            </div>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </CardContent>
                  </Card>
                </motion.div>
              );
            })}
          </AnimatePresence>
        </div>
      )}
    </div>
  );
};

export default UserManagement;
