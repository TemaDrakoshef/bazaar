"use client"

import { ShoppingCart, Trash2 } from "lucide-react"
import Link from "next/link"

import { formatPrice } from "@shared/lib/utils"
import { Button } from "@shared/ui/button"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@shared/ui/sheet"

import {
  useCartHydrated,
  useCartStore,
  useCartTotal,
} from "../store/use-cart-store"

import { CartItemView } from "./cart-item"

export function CartSheet() {
  const items = useCartStore((state) => state.items)
  const clearCart = useCartStore((state) => state.clearCart)
  const hydrated = useCartHydrated()
  const { totalCount, totalPrice } = useCartTotal()

  return (
    <Sheet>
      <SheetTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          className="relative"
          aria-label={`Корзина: ${totalCount} товаров`}
        >
          <ShoppingCart className="h-5 w-5" />
          {hydrated && totalCount > 0 && (
            <span className="absolute -right-1 -top-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-primary px-1 text-[10px] font-bold text-primary-foreground">
              {totalCount}
            </span>
          )}
        </Button>
      </SheetTrigger>

      <SheetContent side="right" className="flex w-full flex-col sm:max-w-md">
        <SheetHeader>
          <SheetTitle>Корзина</SheetTitle>
          <SheetDescription>
            {items.length > 0
              ? `${totalCount} товаров на сумму ${formatPrice(totalPrice)}`
              : "В корзине пока пусто"}
          </SheetDescription>
        </SheetHeader>

        <div className="flex-1 space-y-1 overflow-y-auto pr-1">
          {items.map((item) => (
            <CartItemView key={item.product.id} item={item} />
          ))}
          {items.length === 0 && (
            <div className="py-16 text-center text-sm text-muted-foreground">
              Добавьте товары из каталога, чтобы увидеть их здесь
            </div>
          )}
        </div>

        {items.length > 0 && (
          <SheetFooter className="gap-3 border-t pt-4 sm:flex-col sm:gap-3 sm:space-x-0">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Итого</span>
              <span className="text-lg font-bold">{formatPrice(totalPrice)}</span>
            </div>
            <Button asChild className="w-full">
              <Link href="/cart">Перейти в корзину</Link>
            </Button>
            <Button
              variant="ghost"
              className="w-full text-destructive hover:text-destructive"
              onClick={clearCart}
            >
              <Trash2 className="h-4 w-4" />
              Очистить корзину
            </Button>
          </SheetFooter>
        )}
      </SheetContent>
    </Sheet>
  )
}