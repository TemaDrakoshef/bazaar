export const API_PREFIX = "/api"

export const API_ENDPOINTS = {
  auth: {
    signup: "/v1/auth/signup",
    login: "/v1/auth/login",
    logout: "/v1/auth/logout",
    refresh: "/v1/auth/refresh",
    validate: "/v1/auth/validate",
  },
  catalog: {
    categories: "/v1/catalog/category",
    category: (id: number | string) => `/v1/catalog/category/${id}`,
    categoryMove: (id: number | string) => `/v1/catalog/category/${id}/move`,
    products: "/v1/catalog/product",
    product: (id: number | string) => `/v1/catalog/product/${id}`,
  },
  sellers: {
    create: "/v1/merchants",
    my: "/v1/merchants/my",
  },
  seller: {
    products: "/v1/seller/products",
    product: (id: number | string) => `/v1/seller/products/${id}`,
  },
} as const