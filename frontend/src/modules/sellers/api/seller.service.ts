import { apiClient } from "@shared/api/client"
import { API_ENDPOINTS } from "@shared/api/endpoints"

import type {
  CreateMerchantPayload,
  CreateProductPayload,
  Merchant,
  SellerProduct,
  SellerProductListParams,
  SellerProductListResult,
  UpdateProductPayload,
} from "../types"

export const sellerService = {
  async createMerchant(payload: CreateMerchantPayload): Promise<Merchant> {
    const { data } = await apiClient.post<Merchant>(
      API_ENDPOINTS.sellers.create,
      payload,
    )
    return data
  },

  async getMyMerchants(): Promise<Merchant[]> {
    const { data } = await apiClient.get<Merchant[]>(API_ENDPOINTS.sellers.my)
    return data
  },

  async getSellerProducts(
    params: SellerProductListParams = {},
  ): Promise<SellerProductListResult> {
    const { data } = await apiClient.get<SellerProductListResult>(
      API_ENDPOINTS.seller.products,
      {
        params: {
          limit: params.limit ?? 20,
          offset: params.offset ?? 0,
        },
      },
    )
    return data
  },

  async createSellerProduct(
    payload: CreateProductPayload,
  ): Promise<SellerProduct> {
    const { data } = await apiClient.post<SellerProduct>(
      API_ENDPOINTS.seller.products,
      {
        ...payload,
        ...(payload.description ? { description: payload.description } : {}),
      },
    )
    return data
  },

  async updateSellerProduct(
    id: number | string,
    payload: UpdateProductPayload,
  ): Promise<SellerProduct> {
    const { data } = await apiClient.patch<SellerProduct>(
      API_ENDPOINTS.seller.product(id),
      payload,
    )
    return data
  },

  async deleteSellerProduct(id: number | string): Promise<void> {
    await apiClient.delete(API_ENDPOINTS.seller.product(id))
  },
}