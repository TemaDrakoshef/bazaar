"use client"

import { useQuery } from "@tanstack/react-query"

import {
  sellerService,
  SELLER_PRODUCTS_KEY,
  useSellerStore,
} from "@modules/sellers"

import { formatPrice } from "@shared/lib/utils"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@shared/ui/card"

export default function SellerDashboardPage() {
  const selectedMerchantId = useSellerStore(
    (state) => state.selectedMerchantId,
  )

  const productsQuery = useQuery({
    queryKey: [SELLER_PRODUCTS_KEY, selectedMerchantId, "dashboard"],
    queryFn: () => sellerService.getSellerProducts({ limit: 100, offset: 0 }),
    enabled: selectedMerchantId !== null,
  })

  const products = productsQuery.data?.products ?? []
  const totalStock = products.reduce((sum, product) => sum + product.stock, 0)
  const totalValue = products.reduce(
    (sum, product) => sum + product.price * product.stock,
    0,
  )

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Сводка</h1>
        <p className="text-sm text-muted-foreground">
          Метрики по выбранной организации
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <Card>
          <CardHeader>
            <CardDescription>Товаров</CardDescription>
            <CardTitle className="text-3xl">
              {productsQuery.isLoading ? "…" : products.length}
            </CardTitle>
          </CardHeader>
          <CardContent />
        </Card>
        <Card>
          <CardHeader>
            <CardDescription>Единиц на складе</CardDescription>
            <CardTitle className="text-3xl">
              {productsQuery.isLoading ? "…" : totalStock}
            </CardTitle>
          </CardHeader>
          <CardContent />
        </Card>
        <Card>
          <CardHeader>
            <CardDescription>Стоимость остатков</CardDescription>
            <CardTitle className="text-3xl">
              {productsQuery.isLoading ? "…" : formatPrice(totalValue)}
            </CardTitle>
          </CardHeader>
          <CardContent />
        </Card>
      </div>
    </div>
  )
}