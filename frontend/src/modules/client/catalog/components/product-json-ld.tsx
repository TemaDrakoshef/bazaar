import { toProductSlug } from "@shared/lib/utils"

import type { Product } from "../types"

interface ProductJsonLdProps {
  product: Product
  siteUrl?: string
}


export function ProductJsonLd({
  product,
  siteUrl = "https://example.com",
}: ProductJsonLdProps) {
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "Product",
    name: product.title,
    description: product.description ?? undefined,
    sku: String(product.id),
    url: `${siteUrl}/product/${toProductSlug(product.id, product.title)}`,
    offers: {
      "@type": "Offer",
      priceCurrency: "RUB",
      price: product.price,
      availability:
        product.is_active && product.stock > 0
          ? "https://schema.org/InStock"
          : "https://schema.org/OutOfStock",
    },
  }

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
    />
  )
}