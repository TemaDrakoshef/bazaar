"use client"

import { useState } from "react"
import { Plus } from "lucide-react"

import {
  CreateProductModal,
  ProductTable,
  useSellerStore,
} from "@modules/sellers"

import { Button } from "@shared/ui/button"

export default function SellerInventoryPage() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const merchants = useSellerStore((state) => state.merchants)
  const selectedMerchantId = useSellerStore(
    (state) => state.selectedMerchantId,
  )
  const selected = merchants.find(
    (merchant) => merchant.id === selectedMerchantId,
  )

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">
            Товары и остатки
          </h1>
          <p className="text-sm text-muted-foreground">
            {selected
              ? `Организация: ${selected.name}`
              : "Организация не выбрана"}
          </p>
        </div>
        <Button onClick={() => setIsModalOpen(true)}>
          <Plus className="size-4" />
          Добавить товар
        </Button>
      </div>

      <ProductTable />

      <CreateProductModal open={isModalOpen} onOpenChange={setIsModalOpen} />
    </div>
  )
}