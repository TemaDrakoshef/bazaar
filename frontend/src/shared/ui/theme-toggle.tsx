"use client"

import { Moon, Sun } from "lucide-react"
import { useEffect } from "react"

import { initTheme, useThemeStore } from "@shared/lib/theme"

import { Button } from "@shared/ui/button"

export function ThemeToggle() {
  const theme = useThemeStore((state) => state.theme)
  const toggle = useThemeStore((state) => state.toggle)

  useEffect(() => {
    initTheme()
  }, [])

  const isDark = theme === "dark"

  return (
    <Button
      type="button"
      variant="ghost"
      size="icon"
      onClick={toggle}
      aria-label={isDark ? "Включить светлую тему" : "Включить тёмную тему"}
      title={isDark ? "Светлая тема" : "Тёмная тема"}
    >
      {isDark ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
    </Button>
  )
}