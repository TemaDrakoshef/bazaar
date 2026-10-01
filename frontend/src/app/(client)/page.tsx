
import { CategoryTree, ProductList } from "@modules/client/catalog"


export const dynamic = "force-dynamic"

export default function HomePage() {
  return (
    <main>
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