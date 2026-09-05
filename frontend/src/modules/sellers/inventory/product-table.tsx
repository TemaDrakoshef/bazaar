"use client"

import { useMutation, useQuery } from "@tanstack/react-query"
import { Trash2 } from "lucide-react"
import { useState } from "react"

import { catalogService } from "@modules/client/catalog"

import { queryClient } from "@shared/api/query-client"
import { formatPrice } from "@shared/lib/utils"
import { Badge } from "@shared/ui/badge"
import { Button } from "@shared/ui/button"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@shared/ui/table"

import { sellerService } from "../api/seller.service"
import { SELLER_PRODUCTS_KEY, useSellerStore } from "../store/use-seller-store"
import type { SellerProduct } from "../types"

const PAGE_SIZE = 10

function StockBadge({ stock }: { stock: number }) {
  if (stock <= 0) {
    return <Badge variant="destructive">Нет на складе</Badge>
  }
  if (stock < 5) {
    return (
      <Badge
        variant="outline"
        className="border-transparent bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-400"
      >
        Мало: {stock}
      </Badge>
    )
  }

  return (
    <Badge
      variant="outline"
      className="border-transparent bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-400"
    >
      В наличии: {stock}
    </Badge>
  )
}

export function ProductTable() {
  const selectedMerchantId = useSellerStore(
    (state) => state.selectedMerchantId,
  )
  const [pagination, setPagination] = useState({
    merchantId: selectedMerchantId,
    page: 0,
  })
  if (pagination.merchantId !== selectedMerchantId) {
    setPagination({ merchantId: selectedMerchantId, page: 0 })
  }
  const page = pagination.page
  const offset = page * PAGE_SIZE

  const productsQuery = useQuery({
    queryKey: [SELLER_PRODUCTS_KEY, selectedMerchantId, page],
    queryFn: () => sellerService.getSellerProducts({ limit: PAGE_SIZE, offset }),
    enabled: selectedMerchantId !== null,
  })

  const categoriesQuery = useQuery({
    queryKey: ["catalog-categories"],
    queryFn: () => catalogService.getCategories(),
  })

  const deleteProductMutation = useMutation({
    mutationFn: (productId: number) =>
      sellerService.deleteSellerProduct(productId),
    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey: [SELLER_PRODUCTS_KEY],
      })
    },
  })

  if (selectedMerchantId === null) {
    return (
      <p className="rounded-md border border-dashed p-8 text-center text-sm text-muted-foreground">
        Выберите организацию, чтобы увидеть ее товары.
      </p>
    )
  }

  const products = productsQuery.data?.products ?? []
  const count = productsQuery.data?.count ?? 0
  const categoryNames = new Map(
    (categoriesQuery.data ?? []).map((category) => [category.id, category.name]),
  )
  const totalPages = Math.max(1, Math.ceil(count / PAGE_SIZE))

  const handleDelete = (product: SellerProduct) => {
    if (window.confirm(`Удалить товар «${product.title}»?`)) {
      deleteProductMutation.mutate(product.id)
    }
  }

  return (
    <div className="space-y-4">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-14">ID</TableHead>
            <TableHead>Название</TableHead>
            <TableHead>Категория</TableHead>
            <TableHead>Цена</TableHead>
            <TableHead>Остаток</TableHead>
            <TableHead>Статус</TableHead>
            <TableHead className="w-20 text-right">Действия</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {products.length === 0 ? (
            <TableRow>
              <TableCell
                colSpan={7}
                className="h-24 text-center text-muted-foreground"
              >
                {productsQuery.isLoading
                  ? "Загружаем товары..."
                  : "Товаров пока нет. Добавьте первый товар."}
              </TableCell>
            </TableRow>
          ) : (
            products.map((product) => (
              <TableRow key={product.id}>
                <TableCell className="text-muted-foreground">
                  {product.id}
                </TableCell>
                <TableCell className="max-w-64 truncate font-medium">
                  {product.title}
                </TableCell>
                <TableCell className="text-muted-foreground">
                  {categoryNames.get(product.category_id) ??
                    `#${product.category_id}`}
                </TableCell>
                <TableCell>{formatPrice(product.price)}</TableCell>
                <TableCell>
                  <StockBadge stock={product.stock} />
                </TableCell>
                <TableCell>
                  <Badge variant={product.is_active ? "secondary" : "outline"}>
                    {product.is_active ? "Активен" : "Скрыт"}
                  </Badge>
                </TableCell>
                <TableCell className="text-right">
                  <Button
                    size="icon-xs"
                    variant="ghost"
                    aria-label={`Удалить товар ${product.title}`}
                    disabled={deleteProductMutation.isPending}
                    onClick={() => handleDelete(product)}
                  >
                    <Trash2 className="size-4 text-destructive" />
                  </Button>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>

      {totalPages > 1 && (
        <div className="flex items-center justify-end gap-2">
          <span className="text-sm text-muted-foreground">
            Страница {page + 1} из {totalPages}
          </span>
          <Button
            size="sm"
            variant="outline"
            disabled={page === 0}
            onClick={() =>
              setPagination((current) => ({
                ...current,
                page: current.page - 1,
              }))
            }
          >
            Назад
          </Button>
          <Button
            size="sm"
            variant="outline"
            disabled={page + 1 >= totalPages}
            onClick={() =>
              setPagination((current) => ({
                ...current,
                page: current.page + 1,
              }))
            }
          >
            Вперед
          </Button>
        </div>
      )}
    </div>
  )
}