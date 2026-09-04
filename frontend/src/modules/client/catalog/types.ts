export interface Category {
  id: number
  name: string
  parent_id: number | null
  path: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Product {
  id: number
  category_id: number
  title: string
  description: string | null
  price: number
  stock: number
  is_active: boolean
  created_at: string
  updated_at: string
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