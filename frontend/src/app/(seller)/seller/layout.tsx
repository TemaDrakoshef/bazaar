"use client"

import { useEffect, type ReactNode } from "react"
import { usePathname, useRouter } from "next/navigation"

import { useAuthHydrated, useAuthStore } from "@modules/auth"
import { SellerSidebar, useSellerStore } from "@modules/sellers"

import { Skeleton } from "@shared/ui/skeleton"

export default function SellerLayout({ children }: { children: ReactNode }) {
  const router = useRouter()
  const pathname = usePathname()
  const status = useAuthStore((state) => state.status)
  const hydrated = useAuthHydrated()
  const merchants = useSellerStore((state) => state.merchants)
  const isLoading = useSellerStore((state) => state.isLoading)
  const hasFetched = useSellerStore((state) => state.hasFetched)
  const fetchMyMerchants = useSellerStore((state) => state.fetchMyMerchants)

  useEffect(() => {
    if (hydrated && status === "anonymous") {
      router.replace("/login")
    }
  }, [hydrated, status, router])

  useEffect(() => {
    if (hydrated && status === "authenticated" && !hasFetched) {
      void fetchMyMerchants()
    }
  }, [hydrated, status, hasFetched, fetchMyMerchants])

  useEffect(() => {
    if (
      status === "authenticated" &&
      hasFetched &&
      !isLoading &&
      merchants.length === 0 &&
      pathname !== "/seller/onboarding"
    ) {
      router.replace("/seller/onboarding")
    }
  }, [status, hasFetched, isLoading, merchants.length, pathname, router])

  if (!hydrated || status !== "authenticated") {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Skeleton className="h-10 w-40" />
      </div>
    )
  }

  return (
    <div className="flex min-h-screen flex-col md:flex-row">
      <SellerSidebar />
      <main className="flex-1 p-6 lg:p-10">{children}</main>
    </div>
  )
}