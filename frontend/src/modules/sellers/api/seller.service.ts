import axios from "axios"

import { apiClient } from "@shared/api/client"
import { API_ENDPOINTS } from "@shared/api/endpoints"

import type {
  ConfirmMediaUploadPayload,
  CreateMerchantPayload,
  CreateProductPayload,
  MediaUploadTicket,
  Merchant,
  ProductMedia,
  ReorderMediaItem,
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

  async getSellerProduct(id: number | string): Promise<SellerProduct> {
    const { data } = await apiClient.get<SellerProduct>(
      API_ENDPOINTS.seller.product(id),
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

  async getMediaUploadUrl(
    productId: number | string,
    payload: {
      media_type: "IMAGE" | "VIDEO"
      content_type: string
      file_size: number
    },
  ): Promise<MediaUploadTicket> {
    const { data } = await apiClient.post<MediaUploadTicket>(
      API_ENDPOINTS.seller.media.uploadUrl(productId),
      payload,
    )
    return data
  },


  async uploadFileToStorage(
    uploadUrl: string,
    file: File,
    onProgress?: (percent: number) => void,
  ): Promise<void> {
    await axios.put(uploadUrl, file, {
      headers: { "Content-Type": file.type },
      onUploadProgress: (event) => {
        if (!onProgress) {
          return
        }
        const total = event.total ?? file.size
        onProgress(Math.min(100, Math.round((event.loaded / total) * 100)))
      },
    })
  },

  async confirmMediaUpload(
    productId: number | string,
    payload: ConfirmMediaUploadPayload,
  ): Promise<ProductMedia> {
    const { data } = await apiClient.post<ProductMedia>(
      API_ENDPOINTS.seller.media.confirm(productId),
      payload,
    )
    return data
  },

  async deleteMedia(
    productId: number | string,
    mediaId: number | string,
  ): Promise<void> {
    await apiClient.delete(API_ENDPOINTS.seller.media.item(productId, mediaId))
  },

  async reorderMedia(
    productId: number | string,
    items: ReorderMediaItem[],
  ): Promise<void> {
    await apiClient.patch(API_ENDPOINTS.seller.media.reorder(productId), {
      items,
    })
  },
}