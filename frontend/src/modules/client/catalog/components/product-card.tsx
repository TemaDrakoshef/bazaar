"use client"

import { ImageIcon, ShoppingCart } from "lucide-react"
import Link from "next/link"

import { useCartStore } from "@modules/client/cart/store/use-cart-store"

import { cn, formatPrice, toProductSlug } from "@shared/lib/utils"
import { Badge } from "@shared/ui/badge"
import { Button } from "@shared/ui/button"
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
} from "@shared/ui/card"

import type { Product } from "../types"

interface ProductCardProps {
  product: Product
  className?: string
}

export function ProductCard({ product, className }: ProductCardProps) {
  const addItem = useCartStore((state) => state.addItem)
  const slug = toProductSlug(product.id, product.title)
  const isInStock = product.is_active && product.stock > 0

  return (
    <Card
      className={cn(
        "group flex flex-col overflow-hidden transition-shadow hover:shadow-md",
        className,
      )}
    >
      <Link href={`/product/${slug}`} className="block" aria-label={product.title}>
        <div className="flex aspect-square items-center justify-center bg-muted">
          <ImageIcon className="h-10 w-10 text-muted-foreground/50" />
        </div>
      </Link>

      <CardHeader className="flex-1 gap-1.5">
        <Link href={`/product/${slug}`}>
          <h3 className="line-clamp-2 font-semibold leading-snug hover:underline">
            {product.title}
          </h3>
        </Link>
        <Badge variant={isInStock ? "secondary" : "destructive"} className="w-fit">
          {isInStock ? "В наличии" : "Нет в наличии"}
        </Badge>
      </CardHeader>

      <CardContent>
        <p className="text-lg font-extrabold">{formatPrice(product.price)}</p>
      </CardContent>

      <CardFooter>
        <Button
          size="sm"
          className="w-full"
          disabled={!isInStock}
          onClick={() =>
            addItem(
              {
                id: product.id,
                slug,
                title: product.title,
                price: product.price,
              },
              1,
            )
          }
        >
          <ShoppingCart className="h-4 w-4" />
          В корзину
        </Button>
      </CardFooter>
    </Card>
  )
}