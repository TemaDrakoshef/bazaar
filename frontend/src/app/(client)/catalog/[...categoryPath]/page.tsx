import type { Metadata } from "next"

import { CategoryTree, ProductList } from "@modules/client/catalog"

export const dynamic = "force-dynamic"

interface CategoryPageProps {
  params: Promise<{ categoryPath: string[] }>
}

export async function generateMetadata({
  params,
}: CategoryPageProps): Promise<Metadata> {
  const { categoryPath } = await params
  const segment = categoryPath[categoryPath.length - 1] ?? "каталог"
  const title = segment.charAt(0).toUpperCase() + segment.slice(1)

  return {
    title: `Каталог: ${title}`,
    description: `Товары в категории «${title}» на маркетплейсе Bazaar`,
  }
}

export default async function CategoryPage({
  params,
}: CategoryPageProps) {
  const { categoryPath } = await params
  const segment =
    categoryPath[categoryPath.length - 1]
      ?.split("-")
      .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
      .join(" ") ?? "Категория"

  return (
    <main className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
      <h1 className="mb-8 text-3xl font-bold tracking-tight">{segment}</h1>
      <div className="grid gap-10 lg:grid-cols-[280px_1fr]">
        <aside>
          <CategoryTree currentPath={categoryPath} />
        </aside>
        <section>
          <ProductList categoryPath={categoryPath} />
        </section>
      </div>
    </main>
  )
}