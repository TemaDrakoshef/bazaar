import type { Metadata } from "next";

import { CategoryTree, ProductList } from "@modules/client/catalog";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Каталог товаров",
  description: "Все товары маркетплейса Bazaar с иерархией категорий",
};

export default function CatalogPage() {
  return (
    <main className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
      <h1 className="mb-8 text-3xl font-bold tracking-tight">Каталог товаров</h1>
      <div className="grid gap-10 lg:grid-cols-[280px_1fr]">
        <aside>
          <CategoryTree />
        </aside>
        <section>
          <ProductList />
        </section>
      </div>
    </main>
  );
}