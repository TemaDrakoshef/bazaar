import { apiClient } from "@shared/api/client"
import { API_ENDPOINTS } from "@shared/api/endpoints"

import type {
  Category,
  Product,
  ProductListParams,
  ProductListResult,
} from "../types"

export const catalogService = {
  async getCategories(limit = 100, offset = 0): Promise<Category[]> {
    const { data } = await apiClient.get<Category[]>(
      API_ENDPOINTS.catalog.categories,
      { params: { limit, offset } },
    )
    return data.filter((category) => category.is_active)
  },

  async getCategory(id: number | string): Promise<Category> {
    const { data } = await apiClient.get<Category>(
      API_ENDPOINTS.catalog.category(id),
    )
    return data
  },

  async getProducts(
    params: ProductListParams = {},
  ): Promise<ProductListResult> {
    const { data } = await apiClient.get<ProductListResult>(
      API_ENDPOINTS.catalog.products,
      {
        params: {
          limit: params.limit ?? 20,
          offset: params.offset ?? 0,
        },
      },
    )
    return data
  },

  async getProduct(id: number | string): Promise<Product> {
    const { data } = await apiClient.get<Product>(
      API_ENDPOINTS.catalog.product(id),
    )
    return data
  },
}