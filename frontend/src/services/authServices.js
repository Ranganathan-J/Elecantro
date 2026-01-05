import api from './api'

export async function login(username, password) {
  try {
    const response = await api.post('/api/users/login/', { username, password })
    // Backend returns: { user: {...}, tokens: { access, refresh } }
    return {
      user: response.data.user,
      access_token: response.data.tokens?.access,
      refresh_token: response.data.tokens?.refresh,
    }
  } catch (err) {
    throw err
  }
}

export async function validateToken(token) {
  try {
    const response = await api.get('/api/users/profile/', {
      headers: { Authorization: `Bearer ${token}` },
    })
    // profile endpoint returns { user: ... } or user object depending on backend
    // Here backend's UserProfileView returns { 'user': UserSerializer(...) } in some places,
    // but test_api uses GET /api/users/profile/ expecting user object. Normalize both.
    if (response.data && response.data.user) return response.data.user
    return response.data
  } catch (err) {
    throw err
  }
}

export async function signup(email, password, name) {
  // Minimal signup wrapper — adapt if backend differs
  try {
    const response = await api.post('/api/users/register/', { email, password, password_confirm: password, username: name })
    return response.data
  } catch (err) {
    throw err
  }
}

export async function updateProfile(profileData) {
  try {
    const response = await api.put('/api/users/profile/', profileData)
    return response.data
  } catch (err) {
    throw err
  }
}

export default { login, validateToken, signup, updateProfile }
