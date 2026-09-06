export interface Category {
  id: number
  name: string
  parent_id: number | null
  path: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export type ProductMediaType = "IMAGE" | "VIDEO"

export interface ProductMedia {
  id: number
  product_id: number
  media_type: ProductMediaType
  url: string
  position: number
  width: number | null
  height: number | null
  duration_seconds: number | null
  file_size: number
}

export interface Product {
  id: number
  merchant_id: number
  merchant_name?: string
  category_id: number
  title: string
  description: string | null
  price: number
  stock: number
  is_active: boolean
  created_at: string
  updated_at: string
  media: ProductMedia[]
}

export interface ProductListParams {
  limit?: number
  offset?: number
  categoryPath?: string[]
  search?: string
}

export interface ProductListResult {
  products: Product[]
  count: number
}