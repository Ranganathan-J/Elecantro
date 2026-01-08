import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card';
import { Button } from '../ui/Button';
import { motion } from 'framer-motion';
import {
  Plus,
  Trash2,
  Settings,
  UserCheck,
  Shield,
  Eye,
  Calendar,
  Mail,
  Building,
  AlertTriangle
} from 'lucide-react';

const CONDITION_TYPES = {
  role: { label: 'User Role', icon: Shield, options: ['admin', 'analyst', 'viewer'] },
  company: { label: 'Company', icon: Building, type: 'text' },
  email_domain: { label: 'Email Domain', icon: Mail, type: 'text' },
  account_age: { label: 'Account Age (days)', icon: Calendar, type: 'number' },
  last_login: { label: 'Last Login (days ago)', icon: Calendar, type: 'number' }
};

const ACTION_TYPES = {
  set_role: { label: 'Set Role', icon: Shield, options: ['admin', 'analyst', 'viewer'] },
  add_role: { label: 'Add Role', icon: UserCheck, options: ['admin', 'analyst', 'viewer'] },
  remove_role: { label: 'Remove Role', icon: Eye, options: ['admin', 'analyst', 'viewer'] },
  delete_user: { label: 'Delete User', icon: Trash2, destructive: true },
  notify_admin: { label: 'Notify Admin', icon: AlertTriangle }
};

const RuleBuilder = ({ rule, onChange, onTest }) => {
  const [conditions, setConditions] = useState(rule?.conditions || []);
  const [actions, setActions] = useState(rule?.actions || []);
  const [ruleName, setRuleName] = useState(rule?.name || '');
  const [ruleDescription, setRuleDescription] = useState(rule?.description || '');

  const addCondition = () => {
    const newCondition = {
      id: Date.now(),
      type: 'role',
      operator: 'equals',
      value: ''
    };
    setConditions([...conditions, newCondition]);
  };

  const updateCondition = (index, field, value) => {
    const updatedConditions = [...conditions];
    updatedConditions[index] = { ...updatedConditions[index], [field]: value };
    setConditions(updatedConditions);
    onChange({ ...rule, conditions: updatedConditions });
  };

  const removeCondition = (index) => {
    const updatedConditions = conditions.filter((_, i) => i !== index);
    setConditions(updatedConditions);
    onChange({ ...rule, conditions: updatedConditions });
  };

  const addAction = () => {
    const newAction = {
      id: Date.now(),
      type: 'set_role',
      value: ''
    };
    setActions([...actions, newAction]);
  };

  const updateAction = (index, field, value) => {
    const updatedActions = [...actions];
    updatedActions[index] = { ...updatedActions[index], [field]: value };
    setActions(updatedActions);
    onChange({ ...rule, actions: updatedActions });
  };

  const removeAction = (index) => {
    const updatedActions = actions.filter((_, i) => i !== index);
    setActions(updatedActions);
    onChange({ ...rule, actions: updatedActions });
  };

  const renderConditionInput = (condition, index) => {
    const conditionType = CONDITION_TYPES[condition.type];
    
    if (conditionType.options) {
      return (
        <select
          value={condition.value}
          onChange={(e) => updateCondition(index, 'value', e.target.value)}
          className="flex-1 px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
        >
          <option value="">Select value...</option>
          {conditionType.options.map(option => (
            <option key={option} value={option}>{option}</option>
          ))}
        </select>
      );
    }

    return (
      <input
        type={conditionType.type || 'text'}
        value={condition.value}
        onChange={(e) => updateCondition(index, 'value', e.target.value)}
        placeholder={`Enter ${conditionType.label.toLowerCase()}...`}
        className="flex-1 px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
      />
    );
  };

  const renderActionInput = (action, index) => {
    const actionType = ACTION_TYPES[action.type];
    
    if (actionType.options) {
      return (
        <select
          value={action.value}
          onChange={(e) => updateAction(index, 'value', e.target.value)}
          className="flex-1 px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
        >
          <option value="">Select value...</option>
          {actionType.options.map(option => (
            <option key={option} value={option}>{option}</option>
          ))}
        </select>
      );
    }

    return (
      <input
        type="text"
        value={action.value || ''}
        onChange={(e) => updateAction(index, 'value', e.target.value)}
        placeholder={action.type === 'notify_admin' ? 'Admin email...' : 'Enter value...'}
        className="flex-1 px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
      />
    );
  };

  return (
    <div className="space-y-6">
      {/* Rule Basic Info */}
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2">Rule Name</label>
          <input
            type="text"
            value={ruleName}
            onChange={(e) => {
              setRuleName(e.target.value);
              onChange({ ...rule, name: e.target.value });
            }}
            placeholder="Enter rule name..."
            className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-2">Description</label>
          <textarea
            value={ruleDescription}
            onChange={(e) => {
              setRuleDescription(e.target.value);
              onChange({ ...rule, description: e.target.value });
            }}
            placeholder="Describe what this rule does..."
            rows={3}
            className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary resize-none"
          />
        </div>
      </div>

      {/* Conditions */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <Settings size={20} />
            Conditions
          </h3>
          <Button onClick={addCondition} size="sm" variant="outline">
            <Plus size={16} className="mr-2" />
            Add Condition
          </Button>
        </div>

        <div className="space-y-3">
          {conditions.map((condition, index) => {
            const ConditionIcon = CONDITION_TYPES[condition.type]?.icon || Settings;
            return (
              <motion.div
                key={condition.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center gap-3 p-3 bg-secondary/30 rounded-lg"
              >
                <ConditionIcon size={18} className="text-muted-foreground" />
                
                <select
                  value={condition.type}
                  onChange={(e) => updateCondition(index, 'type', e.target.value)}
                  className="px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                >
                  {Object.entries(CONDITION_TYPES).map(([key, type]) => (
                    <option key={key} value={key}>{type.label}</option>
                  ))}
                </select>

                <select
                  value={condition.operator}
                  onChange={(e) => updateCondition(index, 'operator', e.target.value)}
                  className="px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                >
                  <option value="equals">Equals</option>
                  <option value="not_equals">Not Equals</option>
                  <option value="contains">Contains</option>
                  <option value="greater_than">Greater Than</option>
                  <option value="less_than">Less Than</option>
                </select>

                {renderConditionInput(condition, index)}

                <Button
                  onClick={() => removeCondition(index)}
                  size="sm"
                  variant="ghost"
                  className="text-destructive hover:text-destructive"
                >
                  <Trash2 size={16} />
                </Button>
              </motion.div>
            );
          })}
          
          {conditions.length === 0 && (
            <div className="text-center py-8 text-muted-foreground border-2 border-dashed border-border rounded-lg">
              No conditions added. Click "Add Condition" to get started.
            </div>
          )}
        </div>
      </div>

      {/* Actions */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <Settings size={20} />
            Actions
          </h3>
          <Button onClick={addAction} size="sm" variant="outline">
            <Plus size={16} className="mr-2" />
            Add Action
          </Button>
        </div>

        <div className="space-y-3">
          {actions.map((action, index) => {
            const ActionIcon = ACTION_TYPES[action.type]?.icon || Settings;
            const isDestructive = ACTION_TYPES[action.type]?.destructive;
            
            return (
              <motion.div
                key={action.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex items-center gap-3 p-3 rounded-lg ${
                  isDestructive ? 'bg-destructive/10 border border-destructive/20' : 'bg-secondary/30'
                }`}
              >
                <ActionIcon size={18} className={isDestructive ? 'text-destructive' : 'text-muted-foreground'} />
                
                <select
                  value={action.type}
                  onChange={(e) => updateAction(index, 'type', e.target.value)}
                  className="px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                >
                  {Object.entries(ACTION_TYPES).map(([key, type]) => (
                    <option key={key} value={key}>{type.label}</option>
                  ))}
                </select>

                {renderActionInput(action, index)}

                <Button
                  onClick={() => removeAction(index)}
                  size="sm"
                  variant="ghost"
                  className="text-destructive hover:text-destructive"
                >
                  <Trash2 size={16} />
                </Button>
              </motion.div>
            );
          })}
          
          {actions.length === 0 && (
            <div className="text-center py-8 text-muted-foreground border-2 border-dashed border-border rounded-lg">
              No actions added. Click "Add Action" to get started.
            </div>
          )}
        </div>
      </div>

      {/* Test Rule Button */}
      {onTest && (
        <div className="pt-4 border-t border-border">
          <Button onClick={() => onTest(rule)} variant="outline" className="w-full">
            Test Rule
          </Button>
        </div>
      )}
    </div>
  );
};

export default RuleBuilder;
