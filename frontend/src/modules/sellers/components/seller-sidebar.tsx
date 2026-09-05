"use client"

import { LayoutDashboard, Package } from "lucide-react"
import Link from "next/link"
import { usePathname } from "next/navigation"

import { MerchantSwitcher } from "./merchant-switcher"

import { cn } from "@shared/lib/utils"

const NAV_ITEMS = [
  { href: "/seller/inventory", label: "Товары и остатки", icon: Package },
  { href: "/seller/dashboard", label: "Сводка", icon: LayoutDashboard },
]

export function SellerSidebar() {
  const pathname = usePathname()

  return (
    <aside className="flex w-full flex-col gap-6 border-b bg-background p-4 md:h-screen md:w-64 md:border-r md:border-b-0">
      <div>
        <p className="mb-2 text-xs font-medium tracking-wide text-muted-foreground uppercase">
          Организация
        </p>
        <MerchantSwitcher />
      </div>

      <nav className="flex flex-col gap-1" aria-label="Панель продавца">
        {NAV_ITEMS.map((item) => {
          const isActive =
            pathname === item.href || pathname.startsWith(`${item.href}/`)
          const Icon = item.icon

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground",
                isActive
                  ? "bg-accent text-accent-foreground"
                  : "text-muted-foreground",
              )}
            >
              <Icon className="size-4" />
              {item.label}
            </Link>
          )
        })}
      </nav>
    </aside>
  )
}