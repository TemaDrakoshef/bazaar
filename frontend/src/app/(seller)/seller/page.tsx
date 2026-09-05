"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"

import { useSellerStore } from "@modules/sellers"

export default function SellerIndexPage() {
  const router = useRouter()
  const merchants = useSellerStore((state) => state.merchants)
  const hasFetched = useSellerStore((state) => state.hasFetched)

  useEffect(() => {
    if (!hasFetched) {
      return
    }
    router.replace(
      merchants.length > 0 ? "/seller/inventory" : "/seller/onboarding",
    )
  }, [hasFetched, merchants.length, router])

  return null
}