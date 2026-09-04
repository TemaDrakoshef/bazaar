import { apiClient } from "@shared/api/client"
import { API_ENDPOINTS } from "@shared/api/endpoints"

import type { AuthTokens, LoginInput, SignUpInput } from "../types"

interface ValidateTokenResult {
  valid: boolean
  user_id?: string | null
  error_message?: string
}

export const authService = {
  async signup(input: SignUpInput): Promise<AuthTokens> {
    const { data } = await apiClient.post<AuthTokens>(
      API_ENDPOINTS.auth.signup,
      input,
    )
    return data
  },

  async login(input: LoginInput): Promise<AuthTokens> {
    const { data } = await apiClient.post<AuthTokens>(
      API_ENDPOINTS.auth.login,
      input,
    )
    return data
  },


  async logout(identifier?: string): Promise<void> {
    await apiClient.post(API_ENDPOINTS.auth.logout, {
      session_id: identifier ?? "",
    })
  },

  async refresh(refreshToken: string): Promise<AuthTokens> {
    const { data } = await apiClient.post<AuthTokens>(
      API_ENDPOINTS.auth.refresh,
      { refresh_token: refreshToken },
    )
    return data
  },

  async validate(accessToken: string): Promise<ValidateTokenResult> {
    const { data } = await apiClient.post<ValidateTokenResult>(
      API_ENDPOINTS.auth.validate,
      { access_token: accessToken },
    )
    return data
  },
}