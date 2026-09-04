export interface LoginInput {
  email: string
  password: string
}

export interface SignUpInput {
  email: string
  phone?: string
  password: string
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
}

export type AuthStatus = "anonymous" | "authenticated" | "loading"

export interface AuthUser {
  id: string
  email: string
}