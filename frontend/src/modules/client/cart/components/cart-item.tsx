"use client";

import { ImageIcon, Minus, Plus, Trash2 } from "lucide-react";
import Link from "next/link";

import { Button } from "@shared/ui/button";
import { cn, formatPrice } from "@shared/lib/utils";

import { useCartStore } from "../store/use-cart-store";
import type { CartItem } from "../types";

interface CartItemViewProps {
  item: CartItem;
  className?: string;
}

export function CartItemView({ item, className }: CartItemViewProps) {
  const updateQuantity = useCartStore((state) => state.updateQuantity);
  const removeItem = useCartStore((state) => state.removeItem);

  return (
    <div
      className={cn(
        "flex items-start gap-4 border-b py-4 last:border-0",
        className,
      )}
    >
      <div className="flex h-20 w-20 flex-none items-center justify-center rounded-md bg-muted text-muted-foreground/60">
        <ImageIcon className="h-8 w-8" />
      </div>

      <div className="flex flex-1 flex-col gap-3">
        <div className="flex items-start justify-between gap-4">
          <div className="space-y-1">
            <Link
              href={`/product/${item.product.slug}`}
              className="line-clamp-2 font-medium hover:underline"
            >
              {item.product.title}
            </Link>
            <p className="text-sm text-muted-foreground">
              {formatPrice(item.product.price)} за шт.
            </p>
          </div>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 text-muted-foreground hover:text-destructive"
            onClick={() => removeItem(item.product.id)}
            aria-label="Удалить из корзины"
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>

        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-1">
            <Button
              variant="outline"
              size="icon"
              className="h-8 w-8"
              disabled={item.quantity <= 1}
              onClick={() => updateQuantity(item.product.id, item.quantity - 1)}
              aria-label="Уменьшить количество"
            >
              <Minus className="h-3.5 w-3.5" />
            </Button>
            <span className="w-10 text-center text-sm font-medium">
              {item.quantity}
            </span>
            <Button
              variant="outline"
              size="icon"
              className="h-8 w-8"
              onClick={() => updateQuantity(item.product.id, item.quantity + 1)}
              aria-label="Увеличить количество"
            >
              <Plus className="h-3.5 w-3.5" />
            </Button>
          </div>
          <span className="font-bold">
            {formatPrice(item.product.price * item.quantity)}
          </span>
        </div>
      </div>
    </div>
  );
}