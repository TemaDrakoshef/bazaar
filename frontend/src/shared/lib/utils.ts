import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs))
}

export function slugify(value: string): string {
  return value
    .toLowerCase()
    .trim()
    .replace(/\s+/g, "-")
    .replace(/[^a-z0-9\u0400-\u04ff-]/g, "")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "")
}

export function toProductSlug(id: number, title: string): string {
  return `${slugify(title)}-${id}`
}

export function productIdFromSlug(slug: string): number | null {
  const match = slug.match(/(\d+)$/)
  return match ? Number(match[1]) : null
}

export function formatPrice(value: number): string {
  return new Intl.NumberFormat("ru-RU", {
    style: "currency",
    currency: "RUB",
    maximumFractionDigits: 0,
  }).format(value)
}