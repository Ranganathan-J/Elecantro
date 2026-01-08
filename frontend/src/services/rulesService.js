import api from '../api/axios';

/**
 * Rules management service for admin operations
 */

export const rulesService = {
  // Get all rules
  getAllRules: async () => {
    const response = await api.get('/api/rules/');
    return response.data;
  },

  // Create new rule
  createRule: async (ruleData) => {
    const response = await api.post('/api/rules/', ruleData);
    return response.data;
  },

  // Update rule
  updateRule: async (ruleId, ruleData) => {
    const response = await api.put(`/api/rules/${ruleId}/`, ruleData);
    return response.data;
  },

  // Delete rule
  deleteRule: async (ruleId) => {
    const response = await api.delete(`/api/rules/${ruleId}/`);
    return response.data;
  },

  // Apply rules to users
  applyRules: async (ruleIds) => {
    const response = await api.post('/api/rules/apply/', { rule_ids: ruleIds });
    return response.data;
  },

  // Get rule execution history
  getRuleHistory: async () => {
    const response = await api.get('/api/rules/history/');
    return response.data;
  },

  // Test rule on specific user
  testRule: async (ruleId, userId) => {
    const response = await api.post(`/api/rules/${ruleId}/test/`, { user_id: userId });
    return response.data;
  }
};
