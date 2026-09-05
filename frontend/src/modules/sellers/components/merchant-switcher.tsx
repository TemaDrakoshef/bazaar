"use client"

import { Plus, Store } from "lucide-react"
import Link from "next/link"

import { useSellerStore } from "../store/use-seller-store"

import { Button } from "@shared/ui/button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@shared/ui/select"

export function MerchantSwitcher() {
  const merchants = useSellerStore((state) => state.merchants)
  const selectedMerchantId = useSellerStore(
    (state) => state.selectedMerchantId,
  )
  const setSelectedMerchantId = useSellerStore(
    (state) => state.setSelectedMerchantId,
  )

  if (merchants.length === 0) {
    return (
      <Button asChild size="sm" variant="outline">
        <Link href="/seller/onboarding">
          <Plus className="size-4" />
          Создать магазин
        </Link>
      </Button>
    )
  }

  const selected =
    merchants.find((merchant) => merchant.id === selectedMerchantId) ??
    merchants[0]

  return (
    <div className="flex items-center gap-1">
      <Select
        value={selected ? String(selected.id) : undefined}
        onValueChange={(value) => setSelectedMerchantId(Number(value))}
      >
        <SelectTrigger className="w-56" aria-label="Активная организация">
          <span className="flex min-w-0 items-center gap-2">
            <Store className="size-4 shrink-0 text-muted-foreground" />
            <SelectValue placeholder="Выберите магазин" />
          </span>
        </SelectTrigger>
        <SelectContent>
          {merchants.map((merchant) => (
            <SelectItem key={merchant.id} value={String(merchant.id)}>
              {merchant.name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      <Button
        asChild
        size="icon-sm"
        variant="ghost"
        aria-label="Добавить организацию"
      >
        <Link href="/seller/onboarding">
          <Plus className="size-4" />
        </Link>
      </Button>
    </div>
  )
}