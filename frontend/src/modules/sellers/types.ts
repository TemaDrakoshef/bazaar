export type MerchantStatus = "PENDING_VERIFICATION" | "ACTIVE" | "BLOCKED"

export interface Merchant {
  id: number
  name: string
  inn: string
  owner_user_id: string
  status: MerchantStatus
  created_at: string
}

export interface CreateMerchantPayload {
  name: string
  inn: string
}

export interface SellerProduct {
  id: number
  merchant_id: number
  category_id: number
  title: string
  description: string | null
  price: number
  stock: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface CreateProductPayload {
  title: string
  description?: string
  price: number
  stock: number
  category_id: number
}

export interface UpdateProductPayload {
  title?: string
  description?: string
  price?: number
  stock?: number
  category_id?: number
  is_active?: boolean
}

export interface SellerProductListParams {
  limit?: number
  offset?: number
}

export interface SellerProductListResult {
  products: SellerProduct[]
  count: number
}