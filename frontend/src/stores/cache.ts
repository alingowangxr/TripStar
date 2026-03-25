import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useCacheStore = defineStore('cache', () => {
  const attractionPhotos = ref<Record<string, string>>({})

  async function loadAttractionPhotos(attractions: { name: string }[]) {
    const pending = attractions.filter(a => !attractionPhotos.value[a.name])
    await Promise.allSettled(
      pending.map(async (a) => {
        try {
          const res = await fetch(`/api/poi/photo?query=${encodeURIComponent(a.name)}`)
          if (res.ok) {
            const data = await res.json()
            if (data.url) attractionPhotos.value[a.name] = data.url
          }
        } catch {}
      })
    )
  }

  return { attractionPhotos, loadAttractionPhotos }
})
