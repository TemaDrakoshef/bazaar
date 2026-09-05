import { create } from "zustand"
import { createJSONStorage, persist } from "zustand/middleware"

import { useSellerStore } from "@modules/sellers/store/use-seller-store"

import { authService } from "../api/auth.service"
import type { AuthStatus, AuthTokens, LoginInput, SignUpInput } from "../types"

interface AuthState {
  status: AuthStatus
  email: string | null
  userId: string | null
  accessToken: string | null
  refreshToken: string | null
  hasHydrated: boolean

  login: (input: LoginInput) => Promise<void>
  signup: (input: SignUpInput) => Promise<void>
  logout: () => Promise<void>
  setSession: (tokens: AuthTokens, email: string) => void
  clearSession: () => void
}


const storage =
  typeof window === "undefined"
    ? undefined
    : createJSONStorage(() => window.localStorage)

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      status: "anonymous",
      email: null,
      userId: null,
      accessToken: null,
      refreshToken: null,
      hasHydrated: false,

      setSession: (tokens, email) =>
        set({
          status: "authenticated",
          email,
          accessToken: tokens.access_token,
          refreshToken: tokens.refresh_token,
        }),

      clearSession: () => {
        useSellerStore.getState().reset()
        set({
          status: "anonymous",
          email: null,
          userId: null,
          accessToken: null,
          refreshToken: null,
        })
      },

      login: async (input) => {
        set({ status: "loading", email: input.email })
        try {
          const tokens = await authService.login(input)
          get().setSession(tokens, input.email)
        } catch (error) {
          set({ status: "anonymous" })
          throw error
        }
      },

      signup: async (input) => {
        set({ status: "loading", email: input.email })
        try {
          const tokens = await authService.signup({
            email: input.email,
            password: input.password,
            ...(input.phone && input.phone.length > 0
              ? { phone: input.phone }
              : {}),
          })
          get().setSession(tokens, input.email)
        } catch (error) {
          set({ status: "anonymous" })
          throw error
        }
      },

      logout: async () => {
        const { refreshToken } = get()
        try {
          await authService.logout(refreshToken ?? undefined)
        } finally {
          get().clearSession()
        }
      },
    }),
    {
      name: "bazaar-auth",
      storage,
      onRehydrateStorage: () => (state) => {
        if (state) {
          state.status =
            state.accessToken && state.refreshToken
              ? "authenticated"
              : "anonymous"
          state.hasHydrated = true
        }
      },
    },
  ),
)

export function useAuthHydrated(): boolean {
  return useAuthStore((state) => state.hasHydrated)
}