import Link from "next/link";

export function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="border-t py-8">
      <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 px-4 sm:flex-row sm:px-6 lg:px-8">
        <p className="text-sm text-muted-foreground">
          © {year} Bazaar — открытый маркетплейс
        </p>
        <nav className="flex items-center gap-6 text-sm" aria-label="Полезные ссылки">
          <Link
            href="/catalog"
            className="text-muted-foreground transition-colors hover:text-foreground"
          >
            Каталог
          </Link>
          <Link
            href="/cart"
            className="text-muted-foreground transition-colors hover:text-foreground"
          >
            Корзина
          </Link>
          <Link
            href="/login"
            className="text-muted-foreground transition-colors hover:text-foreground"
          >
            Войти
          </Link>
        </nav>
      </div>
    </footer>
  );
}