"use client"

import { useState } from "react"

import { queryClient } from "@shared/api/query-client"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@shared/ui/sheet"

import { SELLER_PRODUCTS_KEY } from "../store/use-seller-store"
import type { ProductMedia, SellerProduct } from "../types"
import { MediaGallery } from "./media-gallery"
import { MediaUploader } from "./media-uploader"

interface ProductMediaSheetProps {
  product: SellerProduct | null
  onOpenChange: (open: boolean) => void
}

export function ProductMediaSheet({
  product,
  onOpenChange,
}: ProductMediaSheetProps) {
  const [media, setMedia] = useState<ProductMedia[]>(product?.media ?? [])

  const handleClose = (open: boolean) => {
    if (!open) {
      void queryClient.invalidateQueries({
        queryKey: [SELLER_PRODUCTS_KEY],
      })
    }
    onOpenChange(open)
  }

  return (
    <Sheet open={product !== null} onOpenChange={handleClose}>
      <SheetContent
        side="right"
        className="flex w-full flex-col gap-4 overflow-y-auto sm:max-w-md"
      >
        <SheetHeader>
          <SheetTitle>Медиа товара</SheetTitle>
          <SheetDescription className="truncate">
            {product?.title}
          </SheetDescription>
        </SheetHeader>
        {product && (
          <>
            <MediaGallery
              productId={product.id}
              media={media}
              onChange={setMedia}
            />
            <MediaUploader
              productId={product.id}
              hasVideo={media.some((item) => item.media_type === "VIDEO")}
              onUploaded={(item) => setMedia((current) => [...current, item])}
            />
          </>
        )}
      </SheetContent>
    </Sheet>
  )
}
