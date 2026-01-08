import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card';
import { Button } from '../ui/Button';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Settings,
  Play,
  Pause,
  Trash2,
  Edit,
  Copy,
  ChevronDown,
  ChevronUp,
  CheckCircle,
  XCircle,
  Clock,
  Users,
  AlertTriangle
} from 'lucide-react';

const RulesList = ({ rules, onEdit, onDelete, onToggle, onApply, onDuplicate }) => {
  const [expandedRule, setExpandedRule] = useState(null);

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="text-green-500" size={16} />;
      case 'inactive':
        return <Pause className="text-gray-500" size={16} />;
      case 'error':
        return <XCircle className="text-red-500" size={16} />;
      default:
        return <Clock className="text-yellow-500" size={16} />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'bg-green-500/10 text-green-500 border-green-500/20';
      case 'inactive':
        return 'bg-gray-500/10 text-gray-500 border-gray-500/20';
      case 'error':
        return 'bg-red-500/10 text-red-500 border-red-500/20';
      default:
        return 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20';
    }
  };

  const formatCondition = (condition) => {
    const operatorMap = {
      equals: '=',
      not_equals: '≠',
      contains: 'contains',
      greater_than: '>',
      less_than: '<'
    };
    
    return `${condition.type} ${operatorMap[condition.operator]} ${condition.value}`;
  };

  const formatAction = (action) => {
    return `${action.type}: ${action.value || 'N/A'}`;
  };

  return (
    <div className="space-y-4">
      {rules.length === 0 ? (
        <Card>
          <CardContent className="p-12 text-center">
            <Settings className="mx-auto mb-4 text-muted-foreground" size={48} />
            <h3 className="text-lg font-semibold mb-2">No Rules Found</h3>
            <p className="text-muted-foreground">
              Create your first rule to automate user management
            </p>
          </CardContent>
        </Card>
      ) : (
        <AnimatePresence>
          {rules.map((rule) => {
            const isExpanded = expandedRule === rule.id;
            const hasDestructiveActions = rule.actions?.some(action => 
              action.type === 'delete_user'
            );

            return (
              <motion.div
                key={rule.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
              >
                <Card className={`group hover:border-primary/30 transition-all ${
                  hasDestructiveActions ? 'border-destructive/30' : ''
                }`}>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      {/* Rule Info */}
                      <div className="flex items-center gap-4 flex-1">
                        <div className={`h-12 w-12 rounded-full flex items-center justify-center ${
                          hasDestructiveActions ? 'bg-destructive/10' : 'bg-primary/10'
                        }`}>
                          <Settings className={hasDestructiveActions ? 'text-destructive' : 'text-primary'} size={24} />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="font-semibold text-lg truncate">
                              {rule.name}
                            </h3>
                            <span className={`text-xs px-2 py-0.5 rounded-full border flex items-center gap-1 ${getStatusColor(rule.status)}`}>
                              {getStatusIcon(rule.status)}
                              {rule.status}
                            </span>
                            {hasDestructiveActions && (
                              <span className="text-xs px-2 py-0.5 rounded-full bg-destructive/10 text-destructive border border-destructive/20 flex items-center gap-1">
                                <AlertTriangle size={12} />
                                Destructive
                              </span>
                            )}
                          </div>
                          <p className="text-sm text-muted-foreground mb-2 line-clamp-2">
                            {rule.description}
                          </p>
                          <div className="flex items-center gap-4 text-xs text-muted-foreground">
                            <span className="flex items-center gap-1">
                              <Users size={12} />
                              {rule.conditions?.length || 0} conditions
                            </span>
                            <span className="flex items-center gap-1">
                              <Settings size={12} />
                              {rule.actions?.length || 0} actions
                            </span>
                            {rule.last_applied && (
                              <span className="flex items-center gap-1">
                                <Clock size={12} />
                                Applied {new Date(rule.last_applied).toLocaleDateString()}
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
                          onClick={() => setExpandedRule(isExpanded ? null : rule.id)}
                        >
                          {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                        </Button>
                      </div>
                    </div>

                    {/* Expanded Details */}
                    <AnimatePresence>
                      {isExpanded && (
                        <motion.div
                          initial={{ height: 0, opacity: 0 }}
                          animate={{ height: 'auto', opacity: 1 }}
                          exit={{ height: 0, opacity: 0 }}
                          className="mt-4 pt-4 border-t border-border"
                        >
                          {/* Conditions */}
                          {rule.conditions && rule.conditions.length > 0 && (
                            <div className="mb-4">
                              <h4 className="text-sm font-medium mb-2 text-muted-foreground">Conditions</h4>
                              <div className="space-y-1">
                                {rule.conditions.map((condition, index) => (
                                  <div key={index} className="text-sm bg-secondary/30 px-3 py-2 rounded">
                                    {formatCondition(condition)}
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Actions */}
                          {rule.actions && rule.actions.length > 0 && (
                            <div className="mb-4">
                              <h4 className="text-sm font-medium mb-2 text-muted-foreground">Actions</h4>
                              <div className="space-y-1">
                                {rule.actions.map((action, index) => (
                                  <div key={index} className={`text-sm px-3 py-2 rounded ${
                                    action.type === 'delete_user' 
                                      ? 'bg-destructive/10 text-destructive' 
                                      : 'bg-secondary/30'
                                  }`}>
                                    {formatAction(action)}
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Action Buttons */}
                          <div className="flex flex-wrap gap-2 pt-4 border-t border-border">
                            <Button
                              onClick={() => onEdit(rule)}
                              size="sm"
                              variant="outline"
                            >
                              <Edit size={16} className="mr-2" />
                              Edit
                            </Button>
                            
                            <Button
                              onClick={() => onDuplicate(rule)}
                              size="sm"
                              variant="outline"
                            >
                              <Copy size={16} className="mr-2" />
                              Duplicate
                            </Button>

                            <Button
                              onClick={() => onToggle(rule.id)}
                              size="sm"
                              variant={rule.status === 'active' ? 'secondary' : 'outline'}
                            >
                              {rule.status === 'active' ? (
                                <>
                                  <Pause size={16} className="mr-2" />
                                  Deactivate
                                </>
                              ) : (
                                <>
                                  <Play size={16} className="mr-2" />
                                  Activate
                                </>
                              )}
                            </Button>

                            <Button
                              onClick={() => onApply(rule.id)}
                              size="sm"
                              variant="outline"
                              disabled={rule.status !== 'active'}
                            >
                              <Users size={16} className="mr-2" />
                              Apply Now
                            </Button>

                            <Button
                              onClick={() => onDelete(rule.id)}
                              size="sm"
                              variant="destructive"
                            >
                              <Trash2 size={16} className="mr-2" />
                              Delete
                            </Button>
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
      )}
    </div>
  );
};

export default RulesList;
