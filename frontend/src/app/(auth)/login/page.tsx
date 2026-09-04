import type { Metadata } from "next";
import Link from "next/link";

import { LoginForm } from "@modules/auth";

export const metadata: Metadata = {
  title: "Вход",
  description: "Войдите в аккаунт на маркетплейсе Bazaar",
  robots: { index: false, follow: false },
};

export default function LoginPage() {
  return (
    <main className="flex min-h-dvh items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        <LoginForm />
        <p className="mt-6 text-center text-sm text-muted-foreground">
          Нет аккаунта?{" "}
          <Link
            href="/register"
            className="font-medium text-foreground underline underline-offset-4 hover:text-primary"
          >
            Зарегистрироваться
          </Link>
        </p>
      </div>
    </main>
  );
}