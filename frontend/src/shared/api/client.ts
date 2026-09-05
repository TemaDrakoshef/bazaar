import axios from "axios"

import { useAuthStore } from "@modules/auth/store/use-auth-store"
import { useSellerStore } from "@modules/sellers/store/use-seller-store"

import { API_PREFIX } from "./endpoints"

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

export const SELLER_MERCHANT_HEADER = "X-Merchant-ID"


export const apiClient = axios.create({
  baseURL: `${API_BASE_URL}${API_PREFIX}`,
  timeout: 15_000,
  headers: { "Content-Type": "application/json" },
})

apiClient.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = useAuthStore.getState().accessToken
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    const url = config.url ?? ""
    if (url.startsWith("/v1/seller")) {
      const merchantId = useSellerStore.getState().selectedMerchantId
      if (!merchantId) {
        return Promise.reject(
          new Error(
            "Запрос прерван: магазин не выбран (X-Merchant-ID не определен)",
          ),
        )
      }
      config.headers[SELLER_MERCHANT_HEADER] = String(merchantId)
    }
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401 && typeof window !== "undefined") {
      useAuthStore.getState().clearSession()
    }
    return Promise.reject(error)
  },
)