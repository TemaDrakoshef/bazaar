import { ShoppingCart, Store } from "lucide-react"
import type { Metadata } from "next"
import Link from "next/link"
import { notFound } from "next/navigation"

import {
  catalogService,
  ProductGallery,
  ProductJsonLd,
  type Product,
} from "@modules/client/catalog"

import { formatPrice, productIdFromSlug } from "@shared/lib/utils"
import { Badge } from "@shared/ui/badge"
import { Button } from "@shared/ui/button"
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@shared/ui/card"

export const dynamic = "force-dynamic"

interface ProductPageProps {
  params: Promise<{ slug: string }>
}


export async function generateMetadata({
  params,
}: ProductPageProps): Promise<Metadata> {
  const { slug } = await params
  const id = productIdFromSlug(slug)
  const title = id ? `Товар #${id}` : "Товар"

  return {
    title,
    description: `Купить ${title} в маркетплейсе Bazaar. Описание, цена и наличие.`,
    openGraph: {
      title,
      description: `Купить ${title} в маркетплейсе Bazaar.`,
      type: "website",
    },
  }
}

export default async function ProductPage({ params }: ProductPageProps) {
  const { slug } = await params
  const id = productIdFromSlug(slug)
  console.log("ProductPage slug:", slug, "id:", id)

  if (id === null) {
    notFound()
  }

  const product: Product = await catalogService.getProduct(id)

  return (
    <main className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
      <ProductJsonLd product={product} />

      <div className="grid gap-10 lg:grid-cols-2">
        <ProductGallery media={product.media} />

        <div className="space-y-6">
          <Badge variant={product.stock > 0 ? "secondary" : "destructive"}>
            {product.stock > 0 ? "В наличии" : "Нет в наличии"}
          </Badge>

          <h1 className="text-3xl font-bold tracking-tight">{product.title}</h1>
          <p className="text-muted-foreground">{product.description}</p>

          <p className="text-3xl font-extrabold">
            {formatPrice(product.price)}
          </p>

          <div className="flex flex-wrap gap-3">
            <Button asChild size="lg">
              <Link href="/cart">
                <ShoppingCart className="h-5 w-5" />
                Продолжить с покупкой
              </Link>
            </Button>
            <Button asChild size="lg" variant="outline">
              <Link href="/catalog">В каталог</Link>
            </Button>
          </div>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Продавец</CardTitle>
            </CardHeader>
            <CardContent className="flex items-center gap-2 text-sm text-muted-foreground">
              <Store className="size-4" />
              <span>
                {product.merchant_name ??
                  `Магазин №${product.merchant_id}`}
              </span>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Характеристики</CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-muted-foreground">
              Характеристики и EAV-атрибуты будут загружены из каталога.
            </CardContent>
          </Card>
        </div>
      </div>
    </main>
  )
}