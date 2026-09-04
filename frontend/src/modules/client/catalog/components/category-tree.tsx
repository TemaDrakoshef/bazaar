"use client"

import { useQuery } from "@tanstack/react-query"
import { FolderOpen } from "lucide-react"
import Link from "next/link"

import { cn, slugify } from "@shared/lib/utils"
import { Skeleton } from "@shared/ui/skeleton"

import { catalogService } from "../api/catalog.service"
import type { Category } from "../types"

type CategoryNode = Category & { children: CategoryNode[] }

function buildTree(categories: Category[]): CategoryNode[] {
  const map = new Map<number, CategoryNode>()
  for (const category of categories) {
    map.set(category.id, { ...category, children: [] })
  }

  const roots: CategoryNode[] = []
  for (const node of map.values()) {
    const parent =
      node.parent_id !== null ? map.get(node.parent_id) : undefined
    if (parent) {
      parent.children.push(node)
    } else {
      roots.push(node)
    }
  }
  return roots
}

function CategoryBranch({
  node,
  activeSlugs,
}: {
  node: CategoryNode
  activeSlugs?: string[]
}) {
  const isActive =
    activeSlugs !== undefined &&
    activeSlugs[activeSlugs.length - 1] === slugify(node.name)

  const href =
    node.path !== "" ? `/catalog/${node.path.replace(/\./g, "/")}` : `/catalog`

  return (
    <li>
      <Link
        href={href}
        className={cn(
          "flex items-center gap-2 rounded-md px-2 py-1.5 text-sm transition-colors hover:bg-accent hover:text-accent-foreground",
          isActive && "bg-accent font-medium text-accent-foreground",
        )}
      >
        <FolderOpen className="h-4 w-4 shrink-0 text-muted-foreground" />
        {node.name}
      </Link>

      {node.children.length > 0 && (
        <ul className="ml-3 mt-1 space-y-1 border-l pl-2">
          {node.children.map((child) => (
            <CategoryBranch
              key={child.id}
              node={child}
              activeSlugs={activeSlugs}
            />
          ))}
        </ul>
      )}
    </li>
  )
}

interface CategoryTreeProps {
  currentPath?: string[]
  className?: string
}

export function CategoryTree({
  currentPath,
  className,
}: CategoryTreeProps) {
  const { data, isPending, isError } = useQuery({
    queryKey: ["catalog", "categories"],
    queryFn: () => catalogService.getCategories(),
  })

  if (isPending) {
    return (
      <nav className={cn("space-y-2", className)} aria-label="Категории">
        {[0, 1, 2, 3].map((item) => (
          <Skeleton key={item} className="h-8 w-full" />
        ))}
      </nav>
    )
  }

  if (isError || !data) {
    return (
      <p className="text-sm text-muted-foreground">
        Не удалось загрузить категории
      </p>
    )
  }

  const roots = buildTree(data)

  return (
    <nav className={cn("space-y-1", className)} aria-label="Категории товаров">
      <Link
        href="/catalog"
        className="flex items-center gap-2 rounded-md px-2 py-1.5 text-sm font-medium hover:bg-accent hover:text-accent-foreground"
      >
        Все товары
      </Link>
      <ul className="space-y-1">
        {roots.map((root) => (
          <CategoryBranch
            key={root.id}
            node={root}
            activeSlugs={currentPath}
          />
        ))}
      </ul>
    </nav>
  )
}