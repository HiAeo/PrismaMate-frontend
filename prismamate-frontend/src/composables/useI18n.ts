import { ref, computed } from 'vue'
import zh from '@/locales/zh'
import en from '@/locales/en'

export type Locale = 'zh' | 'en'

const messages: Record<Locale, Record<string, any>> = { zh, en }

const currentLocale = ref<Locale>((localStorage.getItem('prismamate-locale') as Locale) || 'zh')

export function useI18n() {
  const locale = computed(() => currentLocale.value)

  function t(key: string): string {
    const keys = key.split('.')
    let value: any = messages[currentLocale.value]
    for (const k of keys) {
      if (value === undefined || value === null) return key
      value = value[k]
    }
    return typeof value === 'string' ? value : key
  }

  function setLocale(l: Locale) {
    currentLocale.value = l
    localStorage.setItem('prismamate-locale', l)
    document.documentElement.lang = l === 'zh' ? 'zh-CN' : 'en'
  }

  function toggleLocale() {
    setLocale(currentLocale.value === 'zh' ? 'en' : 'zh')
  }

  return { locale, t, setLocale, toggleLocale }
}

// 全局可用
export { currentLocale }
