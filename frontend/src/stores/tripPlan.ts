import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { TripPlan, KnowledgeGraphData } from '@/types'

export const useTripPlanStore = defineStore('tripPlan', () => {
  const tripPlan = ref<TripPlan | null>(null)
  const originalPlan = ref<TripPlan | null>(null)
  const graphData = ref<KnowledgeGraphData | null>(null)

  function loadFromSession() {
    const raw = sessionStorage.getItem('tripPlan')
    const rawGraph = sessionStorage.getItem('graphData')
    if (raw) tripPlan.value = JSON.parse(raw)
    if (rawGraph) graphData.value = JSON.parse(rawGraph)
  }

  function saveToSession() {
    if (tripPlan.value) sessionStorage.setItem('tripPlan', JSON.stringify(tripPlan.value))
  }

  function beginEdit() {
    originalPlan.value = JSON.parse(JSON.stringify(tripPlan.value))
  }

  function cancelEdit() {
    if (originalPlan.value) tripPlan.value = JSON.parse(JSON.stringify(originalPlan.value))
    originalPlan.value = null
  }

  function commitEdit() {
    originalPlan.value = null
    saveToSession()
  }

  function deleteAttraction(dayIndex: number, attrIndex: number) {
    tripPlan.value?.days[dayIndex]?.attractions.splice(attrIndex, 1)
  }

  function moveAttraction(dayIndex: number, attrIndex: number, direction: 'up' | 'down') {
    const attractions = tripPlan.value?.days[dayIndex]?.attractions
    if (!attractions) return
    const target = direction === 'up' ? attrIndex - 1 : attrIndex + 1
    if (target < 0 || target >= attractions.length) return
    ;[attractions[attrIndex], attractions[target]] = [attractions[target], attractions[attrIndex]]
  }

  const graphCategories = computed(() => graphData.value?.categories ?? [])

  return {
    tripPlan,
    originalPlan,
    graphData,
    graphCategories,
    loadFromSession,
    saveToSession,
    beginEdit,
    cancelEdit,
    commitEdit,
    deleteAttraction,
    moveAttraction,
  }
})
