"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { authService } from "../api/auth.service";
import { useAuthStore } from "../store/use-auth-store";

import { Button } from "@shared/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@shared/ui/card";
import { Input } from "@shared/ui/input";

const registerSchema = z.object({
  email: z.string().email("Введите корректный email"),
  phone: z
    .string()
    .regex(/^\+[1-9][0-9]{6,14}$/, "Телефон в формате +79991234567")
    .or(z.literal(""))
    .optional(),
  password: z.string().min(8, "Пароль должен содержать минимум 8 символов"),
});

type RegisterValues = z.infer<typeof registerSchema>;

export function RegisterForm() {
  const router = useRouter();
  const setSession = useAuthStore((state) => state.setSession);
  const [serverError, setServerError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: { email: "", phone: "", password: "" },
  });

  const signupMutation = useMutation({
    mutationFn: authService.signup,
    onMutate: () => setServerError(null),
    onSuccess: (tokens, values) => {
      setSession(tokens, values.email);
      router.push("/");
      router.refresh();
    },
    onError: () =>
      setServerError("Не удалось зарегистрироваться. Попробуйте ещё раз."),
  });

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle className="text-2xl">Регистрация</CardTitle>
        <CardDescription>
          Создайте аккаунт, чтобы покупать на Bazaar
        </CardDescription>
      </CardHeader>

      <form
        noValidate
        onSubmit={handleSubmit((values) =>
          signupMutation.mutate({
            email: values.email,
            password: values.password,
            ...(values.phone && values.phone.length > 0
              ? { phone: values.phone }
              : {}),
          }),
        )}
      >
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label
              htmlFor="register-email"
              className="text-sm font-medium leading-none"
            >
              Email
            </label>
            <Input
              id="register-email"
              type="email"
              autoComplete="email"
              placeholder="you@example.com"
              aria-invalid={Boolean(errors.email)}
              {...register("email")}
            />
            {errors.email && (
              <p className="text-sm text-destructive">{errors.email.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <label
              htmlFor="register-phone"
              className="text-sm font-medium leading-none"
            >
              Телефон (необязательно)
            </label>
            <Input
              id="register-phone"
              type="tel"
              autoComplete="tel"
              placeholder="+79991234567"
              aria-invalid={Boolean(errors.phone)}
              {...register("phone")}
            />
            {errors.phone && (
              <p className="text-sm text-destructive">{errors.phone.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <label
              htmlFor="register-password"
              className="text-sm font-medium leading-none"
            >
              Пароль
            </label>
            <Input
              id="register-password"
              type="password"
              autoComplete="new-password"
              placeholder="Минимум 8 символов"
              aria-invalid={Boolean(errors.password)}
              {...register("password")}
            />
            {errors.password && (
              <p className="text-sm text-destructive">
                {errors.password.message}
              </p>
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
            disabled={isSubmitting || signupMutation.isPending}
          >
            {signupMutation.isPending ? "Создаём аккаунт..." : "Зарегистрироваться"}
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
}