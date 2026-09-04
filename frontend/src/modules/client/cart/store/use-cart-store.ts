import { create } from "zustand"
import { createJSONStorage, persist } from "zustand/middleware"
import { useShallow } from "zustand/react/shallow"

import type { CartItem, CartProduct } from "../types"

interface CartState {
  items: CartItem[]
  hasHydrated: boolean

  addItem: (product: CartProduct, quantity?: number) => void
  updateQuantity: (productId: number, quantity: number) => void
  removeItem: (productId: number) => void
  clearCart: () => void
}

const storage =
  typeof window === "undefined"
    ? undefined
    : createJSONStorage(() => window.localStorage)

export const useCartStore = create<CartState>()(
  persist(
    (set) => ({
      items: [],
      hasHydrated: false,

      addItem: (product, quantity = 1) =>
        set((state) => {
          const existing = state.items.find(
            (item) => item.product.id === product.id,
          )
          if (existing) {
            return {
              items: state.items.map((item) =>
                item.product.id === product.id
                  ? { ...item, quantity: item.quantity + quantity }
                  : item,
              ),
            }
          }
          return { items: [...state.items, { product, quantity }] }
        }),

      updateQuantity: (productId, quantity) =>
        set((state) => ({
          items:
            quantity <= 0
              ? state.items.filter((item) => item.product.id !== productId)
              : state.items.map((item) =>
                item.product.id === productId ? { ...item, quantity } : item,
              ),
        })),

      removeItem: (productId) =>
        set((state) => ({
          items: state.items.filter((item) => item.product.id !== productId),
        })),

      clearCart: () => set({ items: [] }),
    }),
    {
      name: "bazaar-cart",
      storage,
      onRehydrateStorage: () => (state) => {
        if (state) {
          state.hasHydrated = true
        }
      },
    },
  ),
)

export function useCartTotal(): { totalCount: number; totalPrice: number } {
  return useCartStore(
    useShallow((state) => ({
      totalCount: state.items.reduce((sum, item) => sum + item.quantity, 0),
      totalPrice: state.items.reduce(
        (sum, item) => sum + item.product.price * item.quantity,
        0,
      ),
    })),
  )
}

export function useCartHydrated(): boolean {
  return useCartStore((state) => state.hasHydrated)
}