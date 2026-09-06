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
  media: ProductMedia[]
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

export interface MediaUploadTicket {
  upload_url: string
  storage_key: string
  public_url: string
}

export interface ConfirmMediaUploadPayload {
  media_type: ProductMediaType
  storage_key: string
  public_url: string
  file_size: number
  width?: number
  height?: number
  duration_seconds?: number
}

export interface ReorderMediaItem {
  media_id: number
  position: number
}
