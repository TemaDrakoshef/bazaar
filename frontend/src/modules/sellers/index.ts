export { sellerService } from "./api/seller.service"
export { CreateProductModal } from "./inventory/create-product-modal"
export { ProductTable } from "./inventory/product-table"
export { MerchantSwitcher } from "./components/merchant-switcher"
export { SellerSidebar } from "./components/seller-sidebar"
export { OnboardingForm } from "./onboarding/onboarding-form"
export {
  SELLER_PRODUCTS_KEY,
  useSellerHydrated,
  useSellerStore,
} from "./store/use-seller-store"

export type {
  CreateMerchantPayload,
  CreateProductPayload,
  Merchant,
  MerchantStatus,
  SellerProduct,
  SellerProductListParams,
  SellerProductListResult,
  UpdateProductPayload,
} from "./types"