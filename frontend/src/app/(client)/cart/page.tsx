"use client"

import { ShoppingCart } from "lucide-react"
import Link from "next/link"

import { CartItemView, useCartHydrated, useCartStore, useCartTotal } from "@modules/client/cart"

import { formatPrice } from "@shared/lib/utils"
import { Button } from "@shared/ui/button"
import { Card, CardContent } from "@shared/ui/card"

export default function CartPage() {
  const items = useCartStore((state) => state.items)
  const hydrated = useCartHydrated()
  const { totalCount, totalPrice } = useCartTotal()

  if (!hydrated) {
    return null
  }

  return (
    <main className="mx-auto max-w-3xl px-4 py-10 sm:px-6">
      <h1 className="mb-8 text-3xl font-bold tracking-tight">Корзина</h1>

      {items.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center gap-4 py-16 text-center">
            <ShoppingCart className="h-12 w-12 text-muted-foreground/60" />
            <div>
              <p className="font-medium">В корзине пока пусто</p>
              <p className="text-sm text-muted-foreground">
                Загляните в каталог и добавьте что-нибудь интересное
              </p>
            </div>
            <Button asChild>
              <Link href="/catalog">Перейти в каталог</Link>
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-2">
          <div className="rounded-lg border px-4">
            {items.map((item) => (
              <CartItemView key={item.product.id} item={item} />
            ))}
          </div>

          <div className="flex flex-col gap-3 rounded-lg border p-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="text-sm text-muted-foreground">
              Итого {totalCount} товаров
            </div>
            <div className="flex items-center gap-4">
              <span className="text-2xl font-extrabold">
                {formatPrice(totalPrice)}
              </span>
              <Button size="lg">Оформить заказ</Button>
            </div>
          </div>
        </div>
      )}
    </main>
  )
}