import type { Metadata, Viewport } from "next"
import { Inter } from "next/font/google"

import "./globals.css"

import { Providers } from "./providers"

const inter = Inter({
  subsets: ["latin", "cyrillic"],
  variable: "--font-inter",
  display: "swap",
})

export const metadata: Metadata = {
  title: {
    default: "Bazaar — открытый маркетплейс",
    template: "%s | Bazaar",
  },
  description:
    "Bazaar — открытый маркетплейс. Покупайте товары из проверенных категорий: электроника, одежда и многое другое.",
  keywords: ["маркетплейс", "интернет-магазин", "покупки", "bazaar"],
  metadataBase: new URL("https://example.com"),
  openGraph: {
    type: "website",
    siteName: "Bazaar",
    locale: "ru_RU",
    title: "Bazaar — открытый маркетплейс",
    description:
      "Покупайте товары из проверенных категорий на открытом маркетплейсе Bazaar.",
  },
}

export const viewport: Viewport = {
  themeColor: "#09090b",
  width: "device-width",
  initialScale: 1,
}


const themeInitScript = `(function () {
  try {
    var stored = localStorage.getItem("bazaar-theme");
    var isDark =
      stored === "dark" ||
      (!stored && window.matchMedia("(prefers-color-scheme: dark)").matches);
    var root = document.documentElement;
    root.classList.toggle("dark", isDark);
    root.style.colorScheme = isDark ? "dark" : "light";
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) {
      meta.setAttribute("content", isDark ? "#09090b" : "#ffffff");
    }
  } catch (err) {}
})();`

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ru" suppressHydrationWarning>
      <body className={`${inter.variable} font-sans antialiased`}>
        <script dangerouslySetInnerHTML={{ __html: themeInitScript }} />
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}