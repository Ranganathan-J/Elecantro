import axios from "axios"

// Use Vite env var when available, otherwise use relative paths so
// the dev server (and its proxy) can route requests to the backend.
const API_BASE_URL = import.meta.env.VITE_API_URL || ""

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
})

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token")
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export async function login(email, password) {
  try {
    const response = await api.post("/auth/login", { email, password })
    return response.data
  } catch (error) {
    throw error
  }
}

export async function signup(email, password, name) {
  try {
    const response = await api.post("/auth/signup", { email, password, name })
    return response.data
  } catch (error) {
    throw error
  }
}

export async function validateToken(token) {
  try {
    const response = await api.get("/auth/me", {
      headers: { Authorization: `Bearer ${token}` },
    })
    return response.data
  } catch (error) {
    throw error
  }
}

export async function updateProfile(profileData) {
  try {
    const response = await api.put("/auth/profile", profileData)
    return response.data
  } catch (error) {
    throw error
  }
}

export default api
