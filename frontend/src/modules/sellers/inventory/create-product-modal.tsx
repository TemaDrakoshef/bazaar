"use client"

import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQuery } from "@tanstack/react-query"
import { useState } from "react"
import { Controller, useForm, type SubmitHandler } from "react-hook-form"
import { z } from "zod"

import { catalogService } from "@modules/client/catalog"

import { queryClient } from "@shared/api/query-client"
import { Button } from "@shared/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@shared/ui/dialog"
import { Input } from "@shared/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@shared/ui/select"

import { sellerService } from "../api/seller.service"
import { SELLER_PRODUCTS_KEY } from "../store/use-seller-store"

const productSchema = z.object({
  title: z
    .string()
    .min(1, "Укажите название")
    .max(255, "Название должно содержать максимум 255 символов"),
  description: z.string().max(2000, "Описание до 2000 символов").optional(),
  price: z
    .number({ message: "Введите цену" })
    .int("Цена — целое число")
    .min(0, "Цена не может быть отрицательной"),
  stock: z
    .number({ message: "Введите остаток" })
    .int("Остаток — целое число")
    .min(0, "Остаток не может быть отрицательным"),
  category_id: z
    .number({ message: "Выберите категорию" })
    .int()
    .positive("Выберите категорию"),
})

type ProductValues = z.infer<typeof productSchema>

interface CreateProductModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function CreateProductModal({
  open,
  onOpenChange,
}: CreateProductModalProps) {
  const [serverError, setServerError] = useState<string | null>(null)

  const {
    register,
    control,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<ProductValues>({
    resolver: zodResolver(productSchema),
    defaultValues: {
      title: "",
      description: "",
      price: 0,
      stock: 0,
      category_id: 0,
    },
  })

  const categoriesQuery = useQuery({
    queryKey: ["catalog-categories"],
    queryFn: () => catalogService.getCategories(),
    enabled: open,
  })

  const createProductMutation = useMutation({
    mutationFn: sellerService.createSellerProduct,
    onMutate: () => setServerError(null),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: [SELLER_PRODUCTS_KEY],
      })
      reset()
      onOpenChange(false)
    },
    onError: () =>
      setServerError("Не удалось создать товар. Попробуйте еще раз."),
  })

  const onSubmit: SubmitHandler<ProductValues> = (values) => {
    createProductMutation.mutate({
      ...values,
      description: values.description?.trim() || undefined,
    })
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Добавить товар</DialogTitle>
          <DialogDescription>
            Товар будет опубликован в выбранной организации
          </DialogDescription>
        </DialogHeader>

        <form
          noValidate
          className="space-y-4"
          onSubmit={handleSubmit(onSubmit)}
        >
          <div className="space-y-2">
            <label
              htmlFor="create-product-title"
              className="text-sm font-medium leading-none"
            >
              Название
            </label>
            <Input
              id="create-product-title"
              placeholder="Футболка оверсайз"
              aria-invalid={Boolean(errors.title)}
              {...register("title")}
            />
            {errors.title && (
              <p className="text-sm text-destructive">{errors.title.message}</p>
            )}
          </div>
          <div className="space-y-2">
            <label
              htmlFor="create-product-description"
              className="text-sm font-medium leading-none"
            >
              Описание
            </label>
            <textarea
              id="create-product-description"
              rows={3}
              placeholder="Хлопок 100%, размерный ряд S–XL"
              className="flex min-h-16 w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs outline-none transition-[color,box-shadow] placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50 aria-invalid:border-destructive aria-invalid:ring-destructive/20"
              aria-invalid={Boolean(errors.description)}
              {...register("description")}
            />
            {errors.description && (
              <p className="text-sm text-destructive">
                {errors.description.message}
              </p>
            )}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label
                htmlFor="create-product-price"
                className="text-sm font-medium leading-none"
              >
                Цена, ₽
              </label>
              <Input
                id="create-product-price"
                type="number"
                min={0}
                step={1}
                aria-invalid={Boolean(errors.price)}
                {...register("price", { valueAsNumber: true })}
              />
              {errors.price && (
                <p className="text-sm text-destructive">
                  {errors.price.message}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <label
                htmlFor="create-product-stock"
                className="text-sm font-medium leading-none"
              >
                Остаток, шт
              </label>
              <Input
                id="create-product-stock"
                type="number"
                min={0}
                step={1}
                aria-invalid={Boolean(errors.stock)}
                {...register("stock", { valueAsNumber: true })}
              />
              {errors.stock && (
                <p className="text-sm text-destructive">
                  {errors.stock.message}
                </p>
              )}
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium leading-none">Категория</label>
            <Controller
              control={control}
              name="category_id"
              render={({ field }) => (
                <Select
                  value={field.value ? String(field.value) : undefined}
                  onValueChange={(value) => field.onChange(Number(value))}
                >
                  <SelectTrigger className="w-full" aria-label="Категория">
                    <SelectValue placeholder="Выберите категорию" />
                  </SelectTrigger>
                  <SelectContent>
                    {(categoriesQuery.data ?? []).map((category) => (
                      <SelectItem key={category.id} value={String(category.id)}>
                        {category.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}
            />
            {errors.category_id && (
              <p className="text-sm text-destructive">
                {errors.category_id.message}
              </p>
            )}
          </div>

          {serverError && (
            <p className="text-sm text-destructive">{serverError}</p>
          )}

          <DialogFooter>
            <Button
              type="submit"
              disabled={
                isSubmitting ||
                createProductMutation.isPending ||
                categoriesQuery.isLoading
              }
            >
              {createProductMutation.isPending
                ? "Создаем товар..."
                : "Создать товар"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}