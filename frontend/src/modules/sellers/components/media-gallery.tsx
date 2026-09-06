"use client"

import { GripVertical, Loader2, Play, Trash2 } from "lucide-react"
import { useState } from "react"

import { Button } from "@shared/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@shared/ui/dialog"

import { sellerService } from "../api/seller.service"
import type { ProductMedia } from "../types"

interface MediaGalleryProps {
  productId: number
  media: ProductMedia[]
  onChange: (media: ProductMedia[]) => void
}

function sortedMedia(media: ProductMedia[]): ProductMedia[] {
  return [...media].sort((a, b) => a.position - b.position)
}

export function MediaGallery({ productId, media, onChange }: MediaGalleryProps) {
  const [deletingId, setDeletingId] = useState<number | null>(null)
  const [pendingDeleteId, setPendingDeleteId] = useState<number | null>(null)
  const [draggingId, setDraggingId] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)

  const items = sortedMedia(media)

  const handleDelete = async (item: ProductMedia) => {
    setPendingDeleteId(item.id)
    setError(null)
    try {
      await sellerService.deleteMedia(productId, item.id)
      onChange(items.filter((entry) => entry.id !== item.id))
      setDeletingId(null)
    } catch {
      setError("Не удалось удалить файл")
    } finally {
      setPendingDeleteId(null)
    }
  }

  const handleDropOn = async (target: ProductMedia) => {
    const sourceId = draggingId
    setDraggingId(null)
    if (sourceId === null || sourceId === target.id) {
      return
    }

    const current = sortedMedia(media)
    const fromIndex = current.findIndex((entry) => entry.id === sourceId)
    const toIndex = current.findIndex((entry) => entry.id === target.id)
    if (fromIndex === -1 || toIndex === -1) {
      return
    }

    const reordered = [...current]
    const [moved] = reordered.splice(fromIndex, 1)
    reordered.splice(toIndex, 0, moved)

    const withPositions = reordered.map((entry, index) => ({
      ...entry,
      position: index,
    }))
    onChange(withPositions)
    setError(null)
    try {
      await sellerService.reorderMedia(
        productId,
        withPositions.map((entry) => ({
          media_id: entry.id,
          position: entry.position,
        })),
      )
    } catch {
      onChange(current)
      setError("Не удалось изменить порядок")
    }
  }

  if (items.length === 0) {
    return (
      <p className="rounded-md border border-dashed p-4 text-center text-sm text-muted-foreground">
        Медиафайлов пока нет — загрузите первое фото или видео.
      </p>
    )
  }

  return (
    <div className="space-y-2">
      <div className="grid grid-cols-3 gap-2">
        {items.map((item) => (
          <div
            key={item.id}
            draggable
            onDragStart={() => setDraggingId(item.id)}
            onDragEnd={() => setDraggingId(null)}
            onDragOver={(event) => event.preventDefault()}
            onDrop={(event) => {
              event.preventDefault()
              void handleDropOn(item)
            }}
            className={`group relative aspect-3/4 cursor-grab overflow-hidden rounded-md border bg-muted active:cursor-grabbing ${
              draggingId === item.id ? "opacity-50" : ""
            }`}
          >
            {item.media_type === "VIDEO" ? (
              <>
                <video
                  src={item.url}
                  className="h-full w-full object-cover"
                  preload="metadata"
                  muted
                />
                <Play className="absolute left-1/2 top-1/2 size-6 -translate-x-1/2 -translate-y-1/2 text-white drop-shadow" />
              </>
            ) : (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={item.url}
                alt={`Медиа ${item.position + 1}`}
                className="h-full w-full object-cover"
              />
            )}

            {item.position === 0 && item.media_type === "IMAGE" && (
              <span className="absolute left-1 top-1 rounded bg-primary px-1.5 py-0.5 text-[10px] font-medium text-primary-foreground">
                Главное фото
              </span>
            )}

            <div className="absolute inset-x-0 bottom-0 flex items-center justify-between bg-black/45 px-1 py-0.5 opacity-0 transition-opacity group-hover:opacity-100">
              <GripVertical className="size-3.5 text-white" />
              <button
                type="button"
                aria-label="Удалить медиафайл"
                className="rounded p-0.5 text-white hover:bg-black/40"
                disabled={pendingDeleteId !== null}
                onClick={() => setDeletingId(item.id)}
              >
                {pendingDeleteId === item.id ? (
                  <Loader2 className="size-3.5 animate-spin" />
                ) : (
                  <Trash2 className="size-3.5" />
                )}
              </button>
            </div>
          </div>
        ))}
      </div>

      {error && <p className="text-sm text-destructive">{error}</p>}

      <Dialog
        open={deletingId !== null}
        onOpenChange={(open) => !open && setDeletingId(null)}
      >
        <DialogContent className="sm:max-w-sm">
          <DialogHeader>
            <DialogTitle>Удалить медиафайл?</DialogTitle>
            <DialogDescription>
              Файл будет удален из хранилища и пропадет со страницы товара.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setDeletingId(null)}
              disabled={pendingDeleteId !== null}
            >
              Отмена
            </Button>
            <Button
              variant="destructive"
              onClick={() => {
                const item = items.find((entry) => entry.id === deletingId)
                if (item) {
                  void handleDelete(item)
                }
              }}
              disabled={pendingDeleteId !== null}
            >
              {pendingDeleteId !== null ? "Удаляем..." : "Удалить"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

