import en from './locales/en.json'
import ja from './locales/ja.json'
import zh from './locales/zh.json'
import zhTW from './locales/zh-TW.json'

export const SUPPORTED_LOCALES = ['zh-CN', 'ja-JP', 'en-US', 'zh-TW'] as const

export type AppLocale = (typeof SUPPORTED_LOCALES)[number]

export const DEFAULT_LOCALE: AppLocale = 'zh-CN'

export const messages = {
  'zh-CN': zh,
  'ja-JP': ja,
  'en-US': en,
  'zh-TW': zhTW,
}
