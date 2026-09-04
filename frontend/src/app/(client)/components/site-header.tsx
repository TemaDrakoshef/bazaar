"use client"

import { LogOut, Search, Store } from "lucide-react"
import Link from "next/link"

import { CartSheet } from "@modules/client/cart"

import { useAuthHydrated, useAuthStore } from "@modules/auth"

import { Button } from "@shared/ui/button"
import { Input } from "@shared/ui/input"
import { ThemeToggle } from "@shared/ui/theme-toggle"

export function SiteHeader() {
  const status = useAuthStore((state) => state.status)
  const email = useAuthStore((state) => state.email)
  const logout = useAuthStore((state) => state.logout)
  const hydrated = useAuthHydrated()

  return (
    <header className="sticky top-0 z-40 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="mx-auto flex h-16 max-w-7xl items-center gap-4 px-4 sm:px-6 lg:px-8">
        <Link
          href="/"
          className="flex items-center gap-2"
          aria-label="На главную"
        >
          <Store className="h-6 w-6" />
          <span className="text-xl font-bold tracking-tight">Bazaar</span>
        </Link>

        <form action="/catalog" className="flex flex-1 justify-center">
          <div className="relative w-full max-w-xl">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              type="search"
              name="q"
              placeholder="Поиск товаров..."
              className="pl-9"
              aria-label="Поиск товаров"
            />
          </div>
        </form>

        <nav className="flex items-center gap-1" aria-label="Учётная запись">
          <ThemeToggle />
          {!hydrated ? null : status === "loading" ? (
            <Button variant="ghost" size="sm" disabled>
              Входим...
            </Button>
          ) : status === "authenticated" ? (
            <div className="flex items-center gap-1">
              {email && (
                <span className="hidden items-center gap-2 sm:inline-flex">
                  <span
                    className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-sm font-semibold text-primary-foreground"
                    aria-hidden="true"
                  >
                    {email.charAt(0).toUpperCase()}
                  </span>
                  <span className="max-w-40 truncate text-sm font-medium">
                    {email}
                  </span>
                </span>
              )}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => void logout()}
              >
                <LogOut className="h-4 w-4" />
                <span className="hidden sm:inline">Выйти</span>
              </Button>
            </div>
          ) : (
            <Button variant="ghost" size="sm" asChild>
              <Link href="/login">Войти</Link>
            </Button>
          )}
          <CartSheet />
        </nav>
      </div>
    </header>
  )
}