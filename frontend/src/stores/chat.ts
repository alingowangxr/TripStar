import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export const useChatStore = defineStore('chat', () => {
  const history = ref<ChatMessage[]>([])
  const isOpen = ref(false)
  const isLoading = ref(false)

  async function sendMessage(message: string, tripPlan: any, language = 'zh-CN') {
    history.value.push({ role: 'user', content: message })
    isLoading.value = true
    try {
      const res = await fetch('/api/chat/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, trip_plan: tripPlan, history: history.value.slice(-10), language }),
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      history.value.push({ role: 'assistant', content: data.reply })
    } catch (e: any) {
      history.value.push({ role: 'assistant', content: `抱歉，发生错误：${e.message}` })
    } finally {
      isLoading.value = false
    }
  }

  function clear() { history.value = [] }

  return { history, isOpen, isLoading, sendMessage, clear }
})
