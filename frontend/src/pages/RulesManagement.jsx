import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { rulesService } from '../services/rulesService';
import { useAuth } from '../context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Settings,
  Plus,
  Save,
  X,
  Users,
  History,
  AlertTriangle,
  CheckCircle,
  Loader2
} from 'lucide-react';
import RuleBuilder from '../components/rules/RuleBuilder';
import RulesList from '../components/rules/RulesList';

const RulesManagement = () => {
  const { user: currentUser } = useAuth();
  const queryClient = useQueryClient();
  const [isCreating, setIsCreating] = useState(false);
  const [editingRule, setEditingRule] = useState(null);
  const [currentRule, setCurrentRule] = useState({});

  // Check if current user is admin
  const userRole = currentUser?.role || currentUser?.user?.role;
  const isAdmin = userRole === 'admin';

  // Fetch all rules
  const { data: rules = [], isLoading, error } = useQuery({
    queryKey: ['rules'],
    queryFn: rulesService.getAllRules,
    enabled: isAdmin,
    refetchInterval: 30000
  });

  // Create rule mutation
  const createRuleMutation = useMutation({
    mutationFn: rulesService.createRule,
    onSuccess: () => {
      queryClient.invalidateQueries(['rules']);
      setIsCreating(false);
      setCurrentRule({});
    }
  });

  // Update rule mutation
  const updateRuleMutation = useMutation({
    mutationFn: ({ id, data }) => rulesService.updateRule(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['rules']);
      setEditingRule(null);
      setCurrentRule({});
    }
  });

  // Delete rule mutation
  const deleteRuleMutation = useMutation({
    mutationFn: rulesService.deleteRule,
    onSuccess: () => {
      queryClient.invalidateQueries(['rules']);
    }
  });

  // Apply rules mutation
  const applyRulesMutation = useMutation({
    mutationFn: rulesService.applyRules,
    onSuccess: () => {
      queryClient.invalidateQueries(['users']);
    }
  });

  const handleCreateRule = () => {
    setCurrentRule({
      name: '',
      description: '',
      conditions: [],
      actions: [],
      status: 'inactive'
    });
    setIsCreating(true);
    setEditingRule(null);
  };

  const handleEditRule = (rule) => {
    setCurrentRule({ ...rule });
    setEditingRule(rule);
    setIsCreating(false);
  };

  const handleSaveRule = () => {
    if (!currentRule.name || !currentRule.conditions?.length || !currentRule.actions?.length) {
      alert('Please fill in all required fields: name, at least one condition, and one action.');
      return;
    }

    if (editingRule) {
      updateRuleMutation.mutate({ id: editingRule.id, data: currentRule });
    } else {
      createRuleMutation.mutate(currentRule);
    }
  };

  const handleDeleteRule = (ruleId) => {
    if (window.confirm('Are you sure you want to delete this rule? This action cannot be undone.')) {
      deleteRuleMutation.mutate(ruleId);
    }
  };

  const handleToggleRule = (ruleId) => {
    const rule = rules.find(r => r.id === ruleId);
    if (rule) {
      const updatedRule = { ...rule, status: rule.status === 'active' ? 'inactive' : 'active' };
      updateRuleMutation.mutate({ id: ruleId, data: updatedRule });
    }
  };

  const handleApplyRule = (ruleId) => {
    if (window.confirm('Are you sure you want to apply this rule to all users? This action will modify user accounts based on the rule conditions.')) {
      applyRulesMutation.mutate([ruleId]);
    }
  };

  const handleDuplicateRule = (rule) => {
    const duplicatedRule = {
      ...rule,
      name: `${rule.name} (Copy)`,
      status: 'inactive'
    };
    delete duplicatedRule.id;
    setCurrentRule(duplicatedRule);
    setEditingRule(null);
    setIsCreating(true);
  };

  const handleCancel = () => {
    setIsCreating(false);
    setEditingRule(null);
    setCurrentRule({});
  };

  // Redirect if not admin
  if (!isAdmin) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Card className="max-w-md">
          <CardContent className="p-6 text-center">
            <AlertTriangle className="mx-auto mb-4 text-destructive" size={48} />
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
            <AlertTriangle className="mx-auto mb-4 text-destructive" size={48} />
            <h2 className="text-xl font-semibold mb-2">Error Loading Rules</h2>
            <p className="text-muted-foreground">
              {error.response?.data?.error || 'Failed to load rules'}
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
            <Settings className="text-primary" size={32} />
            Rules Management
          </h1>
          <p className="text-muted-foreground mt-1">
            Create and manage automated user management rules
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="text-sm text-muted-foreground">
            {rules.length} {rules.length === 1 ? 'rule' : 'rules'}
          </div>
          <Button onClick={handleCreateRule} disabled={isCreating || editingRule}>
            <Plus size={16} className="mr-2" />
            Create Rule
          </Button>
        </div>
      </div>

      {/* Create/Edit Rule Form */}
      <AnimatePresence>
        {(isCreating || editingRule) && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>
                    {editingRule ? 'Edit Rule' : 'Create New Rule'}
                  </CardTitle>
                  <Button variant="ghost" size="sm" onClick={handleCancel}>
                    <X size={16} />
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <RuleBuilder
                  rule={currentRule}
                  onChange={setCurrentRule}
                />
                <div className="flex gap-2 pt-4 border-t border-border">
                  <Button
                    onClick={handleSaveRule}
                    disabled={createRuleMutation.isPending || updateRuleMutation.isPending}
                  >
                    {(createRuleMutation.isPending || updateRuleMutation.isPending) ? (
                      <Loader2 className="mr-2 animate-spin" size={16} />
                    ) : (
                      <Save size={16} className="mr-2" />
                    )}
                    {editingRule ? 'Update Rule' : 'Create Rule'}
                  </Button>
                  <Button variant="outline" onClick={handleCancel}>
                    Cancel
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Rules List */}
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
      ) : (
        <RulesList
          rules={rules}
          onEdit={handleEditRule}
          onDelete={handleDeleteRule}
          onToggle={handleToggleRule}
          onApply={handleApplyRule}
          onDuplicate={handleDuplicateRule}
        />
      )}

      {/* Success Messages */}
      <AnimatePresence>
        {createRuleMutation.isSuccess && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <Card className="bg-green-500/10 border-green-500/20">
              <CardContent className="p-4 flex items-center gap-2">
                <CheckCircle className="text-green-500" size={20} />
                <span className="text-green-500">Rule created successfully!</span>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {updateRuleMutation.isSuccess && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <Card className="bg-green-500/10 border-green-500/20">
              <CardContent className="p-4 flex items-center gap-2">
                <CheckCircle className="text-green-500" size={20} />
                <span className="text-green-500">Rule updated successfully!</span>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {applyRulesMutation.isSuccess && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <Card className="bg-blue-500/10 border-blue-500/20">
              <CardContent className="p-4 flex items-center gap-2">
                <Users className="text-blue-500" size={20} />
                <span className="text-blue-500">Rule applied successfully!</span>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default RulesManagement;
