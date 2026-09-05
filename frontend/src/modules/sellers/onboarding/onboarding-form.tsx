"use client"

import { zodResolver } from "@hookform/resolvers/zod"
import axios from "axios"
import { useMutation } from "@tanstack/react-query"
import { useRouter } from "next/navigation"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { sellerService } from "../api/seller.service"
import { useSellerStore } from "../store/use-seller-store"

import { Button } from "@shared/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@shared/ui/card"
import { Input } from "@shared/ui/input"

const onboardingSchema = z.object({
  name: z
    .string()
    .min(3, "Название должно содержать минимум 3 символа")
    .max(100, "Название должно содержать максимум 100 символов"),
  inn: z
    .string()
    .regex(/^\d{10}$|^\d{12}$/, "ИНН должен содержать 10 или 12 цифр"),
})

type OnboardingValues = z.infer<typeof onboardingSchema>

export function OnboardingForm() {
  const router = useRouter()
  const addMerchant = useSellerStore((state) => state.addMerchant)
  const [serverError, setServerError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<OnboardingValues>({
    resolver: zodResolver(onboardingSchema),
    defaultValues: { name: "", inn: "" },
  })

  const createMerchantMutation = useMutation({
    mutationFn: sellerService.createMerchant,
    onMutate: () => setServerError(null),
    onSuccess: (merchant) => {
      addMerchant(merchant)
      router.push("/seller/inventory")
      router.refresh()
    },
    onError: (error) => {
      if (axios.isAxiosError(error) && error.response?.status === 401) {
        setServerError("Сессия истекла. Войдите в аккаунт заново.")
        return
      }
      setServerError(
        "Не удалось создать магазин. Проверьте данные и попробуйте снова.",
      )
    },
  })

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle className="text-2xl">Новый магазин</CardTitle>
        <CardDescription>
          Зарегистрируйте организацию, чтобы продавать на Bazaar
        </CardDescription>
      </CardHeader>

      <form
        noValidate
        onSubmit={handleSubmit((values) => createMerchantMutation.mutate(values))}
      >
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label
              htmlFor="onboarding-name"
              className="text-sm font-medium leading-none"
            >
              Название
            </label>
            <Input
              id="onboarding-name"
              autoComplete="organization"
              placeholder="ООО «Ромашка»"
              aria-invalid={Boolean(errors.name)}
              {...register("name")}
            />
            {errors.name && (
              <p className="text-sm text-destructive">{errors.name.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <label
              htmlFor="onboarding-inn"
              className="text-sm font-medium leading-none"
            >
              ИНН
            </label>
            <Input
              id="onboarding-inn"
              inputMode="numeric"
              placeholder="7707083893"
              aria-invalid={Boolean(errors.inn)}
              {...register("inn")}
            />
            {errors.inn && (
              <p className="text-sm text-destructive">{errors.inn.message}</p>
            )}
          </div>

          {serverError && (
            <p className="text-sm text-destructive">{serverError}</p>
          )}
        </CardContent>

        <CardFooter>
          <Button
            type="submit"
            className="w-full"
            disabled={isSubmitting || createMerchantMutation.isPending}
          >
            {createMerchantMutation.isPending
              ? "Создаем магазин..."
              : "Создать магазин"}
          </Button>
        </CardFooter>
      </form>
    </Card>
  )
}