export const MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024
export const MAX_VIDEO_SIZE_BYTES = 50 * 1024 * 1024
export const MAX_VIDEO_DURATION_SECONDS = 180

const ALLOWED_IMAGE_TYPES = new Set(["image/jpeg", "image/png", "image/bmp"])
const ALLOWED_VIDEO_TYPES = new Set(["video/mp4", "video/quicktime"])

const MIN_IMAGE_WIDTH = 900
const MIN_IMAGE_HEIGHT = 1200
const ASPECT_TOLERANCE = 0.02

export interface MediaFileMeta {
  width?: number
  height?: number
  durationSeconds?: number
}

function readImageSize(file: File): Promise<MediaFileMeta> {
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(file)
    const image = new window.Image()
    image.onload = () => {
      URL.revokeObjectURL(url)
      resolve({ width: image.naturalWidth, height: image.naturalHeight })
    }
    image.onerror = () => {
      URL.revokeObjectURL(url)
      reject(new Error("Не удалось прочитать изображение"))
    }
    image.src = url
  })
}

function readVideoDuration(file: File): Promise<MediaFileMeta> {
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(file)
    const video = document.createElement("video")
    video.preload = "metadata"
    video.onloadedmetadata = () => {
      URL.revokeObjectURL(url)
      resolve({ durationSeconds: Math.round(video.duration) })
    }
    video.onerror = () => {
      URL.revokeObjectURL(url)
      reject(new Error("Не удалось прочитать видео"))
    }
    video.src = url
  })
}

export async function validateImage(
  file: File,
): Promise<{ ok: true; meta: MediaFileMeta } | { ok: false; error: string }> {
  if (!ALLOWED_IMAGE_TYPES.has(file.type)) {
    return { ok: false, error: "Поддерживаются только JPEG, PNG и BMP" }
  }
  if (file.size > MAX_IMAGE_SIZE_BYTES) {
    return { ok: false, error: "Фото должно быть не больше 10 МБ" }
  }

  let meta: MediaFileMeta
  try {
    meta = await readImageSize(file)
  } catch {
    return { ok: false, error: "Не удалось прочитать изображение" }
  }

  const { width = 0, height = 0 } = meta
  if (width < MIN_IMAGE_WIDTH || height < MIN_IMAGE_HEIGHT) {
    return {
      ok: false,
      error: "Минимальный размер 900x1200 и пропорции 3:4",
    }
  }
  const aspect = width / height
  if (Math.abs(aspect - 3 / 4) / (3 / 4) > ASPECT_TOLERANCE) {
    return {
      ok: false,
      error: "Минимальный размер 900x1200 и пропорции 3:4",
    }
  }

  return { ok: true, meta }
}

export async function validateVideo(
  file: File,
): Promise<{ ok: true; meta: MediaFileMeta } | { ok: false; error: string }> {
  if (!ALLOWED_VIDEO_TYPES.has(file.type)) {
    return { ok: false, error: "Поддерживаются только MP4 и MOV" }
  }
  if (file.size > MAX_VIDEO_SIZE_BYTES) {
    return { ok: false, error: "Видео должно быть не больше 50 МБ" }
  }

  let meta: MediaFileMeta
  try {
    meta = await readVideoDuration(file)
  } catch {
    return { ok: false, error: "Не удалось прочитать видео" }
  }

  if ((meta.durationSeconds ?? 0) > MAX_VIDEO_DURATION_SECONDS) {
    return { ok: false, error: "Видео должно быть не длиннее 3 минут" }
  }

  return { ok: true, meta }
}
