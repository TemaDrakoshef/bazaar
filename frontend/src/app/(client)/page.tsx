import Link from "next/link"

import { CategoryTree, ProductList } from "@modules/client/catalog"

import { Button } from "@shared/ui/button"

export const dynamic = "force-dynamic"

export default function HomePage() {
  return (
    <main>
      <section className="mx-auto max-w-7xl px-4 py-20 text-center sm:px-6 lg:px-8">
        <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl">
          Открытый маркетплейс Bazaar
        </h1>
        <p className="mx-auto mt-4 max-w-2xl text-lg text-muted-foreground">
          Покупайте товары из каталогов с понятной иерархией категорий,
          управляйте корзиной и оформляйте заказы в один клик.
        </p>
        <Button asChild size="lg" className="mt-8">
          <Link href="/catalog">Смотреть каталог</Link>
        </Button>
      </section>

      <section className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid gap-10 lg:grid-cols-[280px_1fr]">
          <aside>
            <h2 className="mb-4 text-2xl font-bold">Категории</h2>
            <CategoryTree />
          </aside>
          <div>
            <h2 className="mb-4 text-2xl font-bold">Новые товары</h2>
            <ProductList limit={8} />
          </div>
        </div>
      </section>
    </main>
  )
}