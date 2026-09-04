import type { MetadataRoute } from "next"

const SITE_URL = "https://example.com"

export default function sitemap(): MetadataRoute.Sitemap {
  const lastModified = new Date()

  return [
    {
      url: `${SITE_URL}/`,
      lastModified,
      changeFrequency: "daily",
      priority: 1,
    },
    {
      url: `${SITE_URL}/catalog`,
      lastModified,
      changeFrequency: "daily",
      priority: 0.9,
    },
  ]
}