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

export { MediaGallery } from "./components/media-gallery"
export { MediaUploader } from "./components/media-uploader"

export type {
  ConfirmMediaUploadPayload,
  CreateMerchantPayload,
  CreateProductPayload,
  MediaUploadTicket,
  Merchant,
  MerchantStatus,
  ProductMedia,
  ProductMediaType,
  ReorderMediaItem,
  SellerProduct,
  SellerProductListParams,
  SellerProductListResult,
  UpdateProductPayload,
} from "./types"