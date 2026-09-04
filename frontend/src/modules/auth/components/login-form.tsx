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

const loginSchema = z.object({
  email: z.string().email("Введите корректный email"),
  password: z.string().min(8, "Пароль должен содержать минимум 8 символов"),
});

type LoginValues = z.infer<typeof loginSchema>;

export function LoginForm() {
  const router = useRouter();
  const setSession = useAuthStore((state) => state.setSession);
  const [serverError, setServerError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: "", password: "" },
  });

  const loginMutation = useMutation({
    mutationFn: authService.login,
    onMutate: () => setServerError(null),
    onSuccess: (tokens, values) => {
      setSession(tokens, values.email);
      router.push("/");
      router.refresh();
    },
    onError: () =>
      setServerError("Не удалось войти. Проверьте email и пароль."),
  });

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle className="text-2xl">Вход</CardTitle>
        <CardDescription>
          Войдите в аккаунт, чтобы оформлять заказы на Bazaar
        </CardDescription>
      </CardHeader>

      <form
        noValidate
        onSubmit={handleSubmit((values) => loginMutation.mutate(values))}
      >
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label
              htmlFor="login-email"
              className="text-sm font-medium leading-none"
            >
              Email
            </label>
            <Input
              id="login-email"
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
              htmlFor="login-password"
              className="text-sm font-medium leading-none"
            >
              Пароль
            </label>
            <Input
              id="login-password"
              type="password"
              autoComplete="current-password"
              placeholder="••••••••"
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
            disabled={isSubmitting || loginMutation.isPending}
          >
            {loginMutation.isPending ? "Входим..." : "Войти"}
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
}