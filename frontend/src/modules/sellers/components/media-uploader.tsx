"use client"

import { ImagePlus, Loader2, Video } from "lucide-react"
import { useRef, useState } from "react"

import { sellerService } from "../api/seller.service"
import type { ProductMedia, ProductMediaType } from "../types"
import { validateImage, validateVideo } from "../utils/media-validation"

const IMAGE_ACCEPT = "image/jpeg,image/png,image/bmp"
const VIDEO_ACCEPT = "video/mp4,video/quicktime"

interface MediaUploaderProps {
  productId: number
  hasVideo: boolean
  onUploaded: (media: ProductMedia) => void
}

function extractErrorDetail(error: unknown): string {
  const detail = (
    error as { response?: { data?: { detail?: unknown } } } | null
  )?.response?.data?.detail
  if (typeof detail === "string") {
    return detail
  }
  if (error instanceof Error) {
    return error.message
  }
  return "Не удалось загрузить файл"
}

export function MediaUploader({
  productId,
  hasVideo,
  onUploaded,
}: MediaUploaderProps) {
  const [mode, setMode] = useState<ProductMediaType>("IMAGE")
  const [dragging, setDragging] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const videoDisabled = mode === "VIDEO" && hasVideo

  const handleFile = async (file: File) => {
    setError(null)

    const validationResult =
      mode === "IMAGE" ? await validateImage(file) : await validateVideo(file)
    if (!validationResult.ok) {
      setError(validationResult.error)
      return
    }

    setIsUploading(true)
    setProgress(0)
    try {
      const ticket = await sellerService.getMediaUploadUrl(productId, {
        media_type: mode,
        content_type: file.type,
        file_size: file.size,
      })
      await sellerService.uploadFileToStorage(
        ticket.upload_url,
        file,
        setProgress,
      )
      const media = await sellerService.confirmMediaUpload(productId, {
        media_type: mode,
        storage_key: ticket.storage_key,
        public_url: ticket.public_url,
        file_size: file.size,
        ...(mode === "IMAGE" && validationResult.meta.width
          ? { width: validationResult.meta.width }
          : {}),
        ...(mode === "IMAGE" && validationResult.meta.height
          ? { height: validationResult.meta.height }
          : {}),
        ...(mode === "VIDEO" && validationResult.meta.durationSeconds !== undefined
          ? { duration_seconds: validationResult.meta.durationSeconds }
          : {}),
      })
      onUploaded(media)
    } catch (uploadError) {
      setError(extractErrorDetail(uploadError))
    } finally {
      setIsUploading(false)
      setProgress(0)
    }
  }

  const openPicker = () => {
    if (!isUploading && !videoDisabled) {
      inputRef.current?.click()
    }
  }

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    setDragging(false)
    if (isUploading || videoDisabled) {
      return
    }
    const file = event.dataTransfer.files[0]
    if (file) {
      void handleFile(file)
    }
  }

  return (
    <div className="space-y-2">
      <div className="flex gap-1 rounded-lg border p-1">
        <button
          type="button"
          className={`flex flex-1 items-center justify-center gap-1.5 rounded-md px-2 py-1.5 text-sm transition-colors ${
            mode === "IMAGE"
              ? "bg-primary text-primary-foreground"
              : "text-muted-foreground hover:bg-muted"
          }`}
          onClick={() => setMode("IMAGE")}
        >
          <ImagePlus className="size-4" />
          Фото
        </button>
        <button
          type="button"
          className={`flex flex-1 items-center justify-center gap-1.5 rounded-md px-2 py-1.5 text-sm transition-colors ${
            mode === "VIDEO"
              ? "bg-primary text-primary-foreground"
              : "text-muted-foreground hover:bg-muted"
          }`}
          onClick={() => setMode("VIDEO")}
          disabled={hasVideo}
          title={hasVideo ? "У товара уже есть видео" : undefined}
        >
          <Video className="size-4" />
          Видео
        </button>
      </div>

      <div
        role="button"
        tabIndex={0}
        aria-disabled={videoDisabled || isUploading}
        className={`flex flex-col items-center justify-center gap-1 rounded-lg border border-dashed p-6 text-center transition-colors ${
          dragging ? "border-primary bg-primary/5" : ""
        } ${
          videoDisabled
            ? "cursor-not-allowed opacity-60"
            : "cursor-pointer hover:border-primary/60"
        }`}
        onClick={openPicker}
        onKeyDown={(event) => {
          if (event.key === "Enter" || event.key === " ") {
            openPicker()
          }
        }}
        onDragOver={(event) => {
          event.preventDefault()
          if (!videoDisabled && !isUploading) {
            setDragging(true)
          }
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
      >
        <input
          ref={inputRef}
          type="file"
          accept={mode === "IMAGE" ? IMAGE_ACCEPT : VIDEO_ACCEPT}
          className="hidden"
          onChange={(event) => {
            const file = event.target.files?.[0]
            event.target.value = ""
            if (file) {
              void handleFile(file)
            }
          }}
        />
        {isUploading ? (
          <>
            <Loader2 className="size-6 animate-spin text-muted-foreground" />
            <p className="text-sm text-muted-foreground">
              Загрузка... {progress}%
            </p>
            <div className="h-1.5 w-40 overflow-hidden rounded-full bg-muted">
              <div
                className="h-full bg-primary transition-all"
                style={{ width: `${progress}%` }}
              />
            </div>
          </>
        ) : videoDisabled ? (
          <p className="text-sm text-muted-foreground">
            Видео уже загружено — можно добавить только одно
          </p>
        ) : (
          <>
            <p className="text-sm font-medium">
              {mode === "IMAGE"
                ? "Перетащите фото или нажмите для выбора"
                : "Перетащите видео или нажмите для выбора"}
            </p>
            <p className="text-xs text-muted-foreground">
              {mode === "IMAGE"
                ? "JPEG, PNG или BMP · до 10 МБ · от 900×1200, пропорции 3:4"
                : "MP4 или MOV · до 50 МБ · не длиннее 3 минут"}
            </p>
          </>
        )}
      </div>

      {error && <p className="text-sm text-destructive">{error}</p>}
    </div>
  )
}
