import type { Metadata } from "next";
import Link from "next/link";

import { RegisterForm } from "@modules/auth";

export const metadata: Metadata = {
  title: "Регистрация",
  description: "Создайте аккаунт на маркетплейсе Bazaar",
  robots: { index: false, follow: false },
};

export default function RegisterPage() {
  return (
    <main className="flex min-h-dvh items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        <RegisterForm />
        <p className="mt-6 text-center text-sm text-muted-foreground">
          Уже есть аккаунт?{" "}
          <Link
            href="/login"
            className="font-medium text-foreground underline underline-offset-4 hover:text-primary"
          >
            Войти
          </Link>
        </p>
      </div>
    </main>
  );
}