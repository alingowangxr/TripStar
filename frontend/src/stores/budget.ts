import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useTripPlanStore } from './tripPlan'

type BudgetItemType = 'attraction' | 'hotel' | 'meal' | 'transport'
type BudgetSortMode = 'amountDesc' | 'amountAsc' | 'dayAsc' | 'dayDesc'

export interface BudgetDetailItem {
  id: string
  type: BudgetItemType
  dayIndex: number | null
  dayNumber: number | null
  name: string
  amount: number
  sourceIndex?: number
}

interface BudgetRestorePayload {
  type: BudgetItemType
  dayIndex: number
  sourceIndex: number
  data: any
}

interface BudgetRestoreItem {
  uid: string
  base: BudgetDetailItem
  payload: BudgetRestorePayload
}

export const useBudgetStore = defineStore('budget', () => {
  const filterType = ref<'all' | BudgetItemType>('all')
  const sortMode = ref<BudgetSortMode>('amountDesc')
  const pendingItems = ref<BudgetRestoreItem[]>([])

  const tripStore = useTripPlanStore()

  const budgetItems = computed<BudgetDetailItem[]>(() => {
    const plan = tripStore.tripPlan
    if (!plan) return []
    const items: BudgetDetailItem[] = []
    plan.days.forEach((day, di) => {
      day.attractions.forEach((a, ai) => {
        if ((a.ticket_price ?? 0) > 0)
          items.push({ id: `attr-${di}-${ai}`, type: 'attraction', dayIndex: di, dayNumber: di + 1, name: a.name, amount: a.ticket_price ?? 0, sourceIndex: ai })
      })
      if (day.hotel?.estimated_cost && day.hotel.estimated_cost > 0)
        items.push({ id: `hotel-${di}`, type: 'hotel', dayIndex: di, dayNumber: di + 1, name: day.hotel.name, amount: day.hotel.estimated_cost })
      day.meals.forEach((m, mi) => {
        if ((m.estimated_cost ?? 0) > 0)
          items.push({ id: `meal-${di}-${mi}`, type: 'meal', dayIndex: di, dayNumber: di + 1, name: m.name, amount: m.estimated_cost ?? 0, sourceIndex: mi })
      })
    })
    if (plan.budget?.total_transportation && plan.budget.total_transportation > 0)
      items.push({ id: 'transport', type: 'transport', dayIndex: null, dayNumber: null, name: '交通费用', amount: plan.budget.total_transportation })
    return items
  })

  const filteredBudgetItems = computed(() => {
    let items = filterType.value === 'all' ? budgetItems.value : budgetItems.value.filter(i => i.type === filterType.value)
    return [...items].sort((a, b) => {
      switch (sortMode.value) {
        case 'amountDesc': return b.amount - a.amount
        case 'amountAsc': return a.amount - b.amount
        case 'dayAsc': return (a.dayNumber ?? 999) - (b.dayNumber ?? 999)
        case 'dayDesc': return (b.dayNumber ?? 999) - (a.dayNumber ?? 999)
        default: return 0
      }
    })
  })

  function recalculate(transportationOverride?: number) {
    const plan = tripStore.tripPlan
    if (!plan) return
    const totals = { total_attractions: 0, total_hotels: 0, total_meals: 0, total_transportation: 0 }
    plan.days.forEach(day => {
      day.attractions.forEach(a => { totals.total_attractions += a.ticket_price ?? 0 })
      if (day.hotel?.estimated_cost) totals.total_hotels += day.hotel.estimated_cost
      day.meals.forEach(m => { totals.total_meals += m.estimated_cost ?? 0 })
    })
    totals.total_transportation = transportationOverride ?? plan.budget?.total_transportation ?? 0
    if (!plan.budget) plan.budget = { ...totals, total: 0 }
    else Object.assign(plan.budget, totals)
    plan.budget.total = totals.total_attractions + totals.total_hotels + totals.total_meals + totals.total_transportation
    tripStore.saveToSession()
  }

  function deleteItem(item: BudgetDetailItem) {
    const plan = tripStore.tripPlan
    if (!plan) return
    const uid = `restore-${Date.now()}`
    if (item.type === 'attraction' && item.dayIndex !== null && item.sourceIndex !== undefined) {
      const removed = plan.days[item.dayIndex].attractions.splice(item.sourceIndex, 1)[0]
      pendingItems.value.push({ uid, base: item, payload: { type: 'attraction', dayIndex: item.dayIndex, sourceIndex: item.sourceIndex, data: removed } })
    } else if (item.type === 'hotel' && item.dayIndex !== null) {
      const removed = plan.days[item.dayIndex].hotel
      plan.days[item.dayIndex].hotel = undefined
      pendingItems.value.push({ uid, base: item, payload: { type: 'hotel', dayIndex: item.dayIndex, sourceIndex: 0, data: removed } })
    } else if (item.type === 'meal' && item.dayIndex !== null && item.sourceIndex !== undefined) {
      const removed = plan.days[item.dayIndex].meals.splice(item.sourceIndex, 1)[0]
      pendingItems.value.push({ uid, base: item, payload: { type: 'meal', dayIndex: item.dayIndex, sourceIndex: item.sourceIndex, data: removed } })
    }
    recalculate()
  }

  function restoreItem(uid: string) {
    const idx = pendingItems.value.findIndex(p => p.uid === uid)
    if (idx === -1) return
    const { payload } = pendingItems.value[idx]
    const plan = tripStore.tripPlan
    if (!plan) return
    if (payload.type === 'attraction') plan.days[payload.dayIndex].attractions.splice(payload.sourceIndex, 0, payload.data)
    else if (payload.type === 'hotel') plan.days[payload.dayIndex].hotel = payload.data
    else if (payload.type === 'meal') plan.days[payload.dayIndex].meals.splice(payload.sourceIndex, 0, payload.data)
    pendingItems.value.splice(idx, 1)
    recalculate()
  }

  function editItemAmount(item: BudgetDetailItem, newAmount: number) {
    const plan = tripStore.tripPlan
    if (!plan) return
    if (item.type === 'attraction' && item.dayIndex !== null && item.sourceIndex !== undefined)
      plan.days[item.dayIndex].attractions[item.sourceIndex].ticket_price = newAmount
    else if (item.type === 'hotel' && item.dayIndex !== null && plan.days[item.dayIndex].hotel)
      plan.days[item.dayIndex].hotel!.estimated_cost = newAmount
    else if (item.type === 'meal' && item.dayIndex !== null && item.sourceIndex !== undefined)
      plan.days[item.dayIndex].meals[item.sourceIndex].estimated_cost = newAmount
    else if (item.type === 'transport')
      recalculate(newAmount)
    recalculate()
  }

  return { filterType, sortMode, pendingItems, budgetItems, filteredBudgetItems, recalculate, deleteItem, restoreItem, editItemAmount }
})
