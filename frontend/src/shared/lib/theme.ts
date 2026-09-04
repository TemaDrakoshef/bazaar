"use client"

import { create } from "zustand"

export type Theme = "light" | "dark"

const STORAGE_KEY = "bazaar-theme"

interface ThemeState {

  theme: Theme
  toggle: () => void
}

function getSystemTheme(): Theme {
  return window.matchMedia("(prefers-color-scheme: dark)").matches
    ? "dark"
    : "light"
}

function readStoredTheme(): Theme | null {
  try {
    const stored = window.localStorage.getItem(STORAGE_KEY)
    return stored === "dark" || stored === "light" ? stored : null
  } catch {
    return null
  }
}

function applyTheme(theme: Theme): void {
  const root = document.documentElement
  root.classList.toggle("dark", theme === "dark")
  root.style.colorScheme = theme

  const meta = document.querySelector('meta[name="theme-color"]')
  meta?.setAttribute("content", theme === "dark" ? "#09090b" : "#ffffff")
}

export const useThemeStore = create<ThemeState>()((set, get) => ({
  theme: "light",

  toggle: () => {
    const next: Theme = get().theme === "dark" ? "light" : "dark"
    applyTheme(next)
    try {
      window.localStorage.setItem(STORAGE_KEY, next)
    } catch {
    }
    set({ theme: next })
  },
}))


export function initTheme(): Theme {
  const theme = readStoredTheme() ?? getSystemTheme()
  applyTheme(theme)
  useThemeStore.setState({ theme })
  return theme
}