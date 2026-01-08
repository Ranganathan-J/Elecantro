import api from '../api/axios';

/**
 * User management service for admin operations
 */

export const userService = {
  // Get all users (admin only)
  getAllUsers: async () => {
    const response = await api.get('/api/users/list/');
    return response.data;
  },

  // Get user by ID
  getUserById: async (userId) => {
    const response = await api.get(`/api/users/${userId}/`);
    return response.data;
  },

  // Promote user to a role (admin only)
  promoteUser: async (userId, role) => {
    const response = await api.post('/api/users/promote/', {
      user_id: userId,
      role: role
    });
    return response.data;
  },

  // Demote user from admin (admin only)
  demoteUser: async (userId, role) => {
    const response = await api.post('/api/users/demote/', {
      user_id: userId,
      role: role
    });
    return response.data;
  },

  // Delete user (admin only)
  deleteUser: async (userId) => {
    const response = await api.delete(`/api/users/${userId}/`);
    return response.data;
  }
};
