import { Footer } from "./components/footer"
import { SiteHeader } from "./components/site-header"


export default function ClientLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <div className="flex min-h-dvh flex-col">
      <SiteHeader />
      <div className="flex-1">{children}</div>
      <Footer />
    </div>
  )
}
