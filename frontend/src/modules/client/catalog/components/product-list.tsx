"use client";

import { useQuery } from "@tanstack/react-query";
import { Loader2 } from "lucide-react";

import { Button } from "@shared/ui/button";

import { catalogService } from "../api/catalog.service";
import type { ProductListParams } from "../types";

import { ProductCard } from "./product-card";

interface ProductListProps {
  categoryPath?: string[];
  search?: string;
  limit?: number;
}

export function ProductList({
  categoryPath,
  search,
  limit = 12,
}: ProductListProps) {
  const params: ProductListParams = { limit, categoryPath, search };

  const { data, isPending, isError, refetch } = useQuery({
    queryKey: ["catalog", "products", params],
    queryFn: () => catalogService.getProducts(params),
  });

  if (isPending) {
    return (
      <div className="flex items-center justify-center py-16">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex flex-col items-center gap-3 py-16 text-center">
        <p className="text-muted-foreground">
          Не удалось загрузить товары. Проверьте, что API-шлюз запущен.
        </p>
        <Button variant="outline" onClick={() => refetch()}>
          Повторить
        </Button>
      </div>
    );
  }

  if (!data || data.products.length === 0) {
    return (
      <p className="py-16 text-center text-muted-foreground">
        Товары не найдены
      </p>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {data.products.map((product) => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  );
}