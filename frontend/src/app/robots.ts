import type { MetadataRoute } from "next"

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      allow: ["/", "/catalog/", "/product/"],
      disallow: ["/cart/", "/login/", "/register/", "/api/"],
    },
    sitemap: "https://example.com/sitemap.xml",
  }
}