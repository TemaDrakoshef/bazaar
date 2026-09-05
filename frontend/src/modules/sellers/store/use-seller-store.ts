import { queryClient } from "@shared/api/query-client"
import { create } from "zustand"
import { createJSONStorage, persist } from "zustand/middleware"

import { sellerService } from "../api/seller.service"
import type { Merchant } from "../types"

const SELLER_PRODUCTS_QUERY_KEY = "seller-products"

interface SellerState {
  merchants: Merchant[]
  selectedMerchantId: number | null
  isLoading: boolean
  hasFetched: boolean
  hasHydrated: boolean

  fetchMyMerchants: () => Promise<void>
  setSelectedMerchantId: (id: number) => void
  addMerchant: (merchant: Merchant) => void
  reset: () => void
}

const storage =
  typeof window === "undefined"
    ? undefined
    : createJSONStorage(() => window.localStorage)

export const useSellerStore = create<SellerState>()(
  persist(
    (set, get) => ({
      merchants: [],
      selectedMerchantId: null,
      isLoading: false,
      hasFetched: false,
      hasHydrated: false,

      fetchMyMerchants: async () => {
        if (get().isLoading) {
          return
        }
        set({ isLoading: true })
        try {
          const merchants = await sellerService.getMyMerchants()
          set((state) => {
            const current = state.selectedMerchantId
            const stillAvailable =
              current !== null &&
              merchants.some((merchant) => merchant.id === current)
            return {
              merchants,
              hasFetched: true,
              selectedMerchantId: stillAvailable
                ? current
                : (merchants[0]?.id ?? null),
            }
          })
        } catch {
          set({ hasFetched: true })
        } finally {
          set({ isLoading: false })
        }
      },

      setSelectedMerchantId: (id) => {
        set({ selectedMerchantId: id })
        void queryClient.invalidateQueries({
          queryKey: [SELLER_PRODUCTS_QUERY_KEY],
        })
      },

      addMerchant: (merchant) =>
        set((state) => ({
          merchants: [...state.merchants, merchant],
          selectedMerchantId: merchant.id,
        })),

      reset: () =>
        set({
          merchants: [],
          selectedMerchantId: null,
          isLoading: false,
          hasFetched: false,
        }),
    }),
    {
      name: "bazaar-seller",
      storage,
      partialize: (state) => ({
        selectedMerchantId: state.selectedMerchantId,
      }),
      onRehydrateStorage: () => (state) => {
        if (state) {
          state.hasHydrated = true
        }
      },
    },
  ),
)

export function useSellerHydrated(): boolean {
  return useSellerStore((state) => state.hasHydrated)
}

export const SELLER_PRODUCTS_KEY = SELLER_PRODUCTS_QUERY_KEY