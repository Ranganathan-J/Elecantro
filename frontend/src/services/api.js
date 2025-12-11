import axios from "axios";

const api = axios.create({
  baseURL: "https://glowing-adventure-jj56v44646jrfqjwq-8000.app.github.dev",
  withCredentials: true,   // FIXED
  headers: {
    "Content-Type": "application/json",
    "Accept": "application/json",
  },
});

export default api;
