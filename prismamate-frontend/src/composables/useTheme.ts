import { ref, computed } from 'vue'

// 强制使用深色主题，移除浅色主题支持
const currentTheme = ref<'dark'>('dark')

// 初始化主题 - 始终使用深色主题
document.documentElement.classList.add('dark')
document.documentElement.classList.remove('light')
localStorage.setItem('prismamate-theme', 'dark')

export function useTheme() {
  const theme = computed(() => currentTheme.value)
  const isDark = computed(() => true)
  const isLight = computed(() => false)

  function setTheme(t: 'dark') {
    currentTheme.value = t
    document.documentElement.classList.add('dark')
    document.documentElement.classList.remove('light')
    localStorage.setItem('prismamate-theme', t)
  }

  function toggleTheme() {
    // 保持深色主题，不做任何切换
  }

  return { theme, isDark, isLight, setTheme, toggleTheme }
}

export { currentTheme }
