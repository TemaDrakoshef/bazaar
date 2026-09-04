import axios from "axios"

import { API_PREFIX } from "./endpoints"

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

export const AUTH_TOKEN_KEY = "bazaar_access_token"


export const apiClient = axios.create({
  baseURL: `${API_BASE_URL}${API_PREFIX}`,
  timeout: 15_000,
  headers: { "Content-Type": "application/json" },
})

apiClient.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = window.localStorage.getItem(AUTH_TOKEN_KEY)
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401 && typeof window !== "undefined") {
      window.localStorage.removeItem(AUTH_TOKEN_KEY)
    }
    return Promise.reject(error)
  },
)