"use client"

import { ImageIcon, Play } from "lucide-react"
import { useState } from "react"

import type { ProductMedia } from "../types"

interface ProductGalleryProps {
  media: ProductMedia[]
}

export function ProductGallery({ media }: ProductGalleryProps) {
  const items = [...media].sort((a, b) => a.position - b.position)
  const [activeId, setActiveId] = useState<number | null>(items[0]?.id ?? null)
  const active = items.find((item) => item.id === activeId) ?? items[0] ?? null

  if (!active) {
    return (
      <div className="flex aspect-square items-center justify-center rounded-lg border bg-muted">
        <ImageIcon className="h-16 w-16 text-muted-foreground/50" />
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <div className="flex aspect-square items-center justify-center overflow-hidden rounded-lg border bg-muted">
        {active.media_type === "VIDEO" ? (
          <video
            key={active.id}
            src={active.url}
            controls
            className="h-full w-full object-contain"
          />
        ) : (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            key={active.id}
            src={active.url}
            alt="Фото товара"
            className="h-full w-full object-contain"
          />
        )}
      </div>

      {items.length > 1 && (
        <div className="grid grid-cols-5 gap-2">
          {items.map((item) => (
            <button
              key={item.id}
              type="button"
              aria-label={
                item.media_type === "VIDEO"
                  ? "Показать видео"
                  : `Показать фото ${item.position + 1}`
              }
              className={`relative aspect-3/4 overflow-hidden rounded-md border transition-opacity hover:opacity-90 ${
                item.id === active.id ? "ring-2 ring-primary" : ""
              }`}
              onClick={() => setActiveId(item.id)}
            >
              {item.media_type === "VIDEO" ? (
                <>
                  <video
                    src={item.url}
                    preload="metadata"
                    muted
                    className="h-full w-full object-cover"
                  />
                  <Play className="absolute left-1/2 top-1/2 size-5 -translate-x-1/2 -translate-y-1/2 text-white drop-shadow" />
                </>
              ) : (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={item.url}
                  alt={`Фото ${item.position + 1}`}
                  className="h-full w-full object-cover"
                />
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
