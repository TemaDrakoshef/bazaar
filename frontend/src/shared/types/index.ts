export interface BaseEntity {
  id: number
  created_at: string
  updated_at: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  limit: number
  offset: number
  hasMore: boolean
}

export interface PaginationParams {
  limit?: number
  offset?: number
}