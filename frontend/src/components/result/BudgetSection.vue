<template>
  <div class="top-info-section">
    <div class="left-info">
      <a-card
        v-if="tripStore.tripPlan?.budget"
        id="budget"
        :bordered="false"
        class="budget-card section-shellless"
      >
        <div class="budget-detail-panel">
          <div class="budget-toolbar">
            <div class="budget-toolbar-item">
              <span class="budget-toolbar-label">{{ t('result.budget.filterLabel') }}</span>
              <a-select v-model:value="budgetFilterType" size="small" class="budget-select">
                <a-select-option value="all">{{ t('result.budget.filterAll') }}</a-select-option>
                <a-select-option value="attraction">{{ t('result.budget.attraction') }}</a-select-option>
                <a-select-option value="hotel">{{ t('result.budget.hotel') }}</a-select-option>
                <a-select-option value="meal">{{ t('result.budget.meal') }}</a-select-option>
                <a-select-option value="transport">{{ t('result.budget.transport') }}</a-select-option>
              </a-select>
            </div>
            <div class="budget-toolbar-item">
              <span class="budget-toolbar-label">{{ t('result.budget.sortLabel') }}</span>
              <a-select v-model:value="budgetSortMode" size="small" class="budget-select">
                <a-select-option value="amountDesc">{{ t('result.budget.sortAmountDesc') }}</a-select-option>
                <a-select-option value="amountAsc">{{ t('result.budget.sortAmountAsc') }}</a-select-option>
                <a-select-option value="dayAsc">{{ t('result.budget.sortDayAsc') }}</a-select-option>
                <a-select-option value="dayDesc">{{ t('result.budget.sortDayDesc') }}</a-select-option>
              </a-select>
            </div>
          </div>

          <div v-if="filteredBudgetItems.length > 0" class="budget-detail-list">
            <div class="budget-detail-row budget-detail-header">
              <span>{{ t('result.budget.detailType') }}</span>
              <span>{{ t('result.budget.detailDay') }}</span>
              <span>{{ t('result.budget.detailName') }}</span>
              <span>{{ t('result.budget.detailAmount') }}</span>
              <span>{{ t('result.budget.detailAction') }}</span>
            </div>
            <div
              v-for="item in filteredBudgetItems"
              :key="item.id"
              class="budget-detail-row"
            >
              <span class="budget-detail-type">{{ getBudgetTypeLabel(item.type) }}</span>
              <span class="budget-detail-day">
                {{ item.dayNumber ? t('common.dayNumber', { day: item.dayNumber }) : '--' }}
              </span>
              <span class="budget-detail-name">{{ item.name }}</span>
              <span class="budget-detail-amount">¥{{ formatBudgetAmount(item.amount) }}</span>
              <span class="budget-action-wrap">
                <button
                  type="button"
                  class="budget-icon-btn budget-edit-btn"
                  :title="t('result.budget.editPrice')"
                  @click="editBudgetItemAmount(item)"
                >
                  <svg fill="currentColor" width="20px" height="20px" viewBox="0 0 256.00098 256.00098" id="Flat" xmlns="http://www.w3.org/2000/svg">
                    <path d="M216.001,203.833h-76l27.91015-27.90967.00684-.00635.00635-.00683,56.563-56.5625a28.03348,28.03348,0,0,0-.001-39.59766L179.23145,34.49512a28.03347,28.03347,0,0,0-39.59766,0L83.07471,91.0542l-.01026.00928-.00927.01025L26.49609,147.63281a28.03171,28.03171,0,0,0,0,39.59766L63.585,224.31836a12.00286,12.00286,0,0,0,8.48535,3.51465H216.001a12,12,0,0,0,0-24ZM156.60449,51.46582a4.00207,4.00207,0,0,1,5.65625,0L207.51562,96.7207a4.005,4.005,0,0,1,0,5.65723l-48.083,48.083L108.521,99.54932ZM106.05957,203.833H77.041L43.4668,170.25977a4.00385,4.00385,0,0,1,0-5.65625L91.55029,116.52l50.91114,50.91113Z"/>
                  </svg>
                </button>
                <button
                  type="button"
                  class="budget-icon-btn budget-delete-btn"
                  :title="t('common.delete')"
                  @click="deleteBudgetItem(item)"
                >
                  <svg fill="currentColor" width="21px" height="21px" viewBox="0 0 256 256" id="Flat" xmlns="http://www.w3.org/2000/svg">
                    <path d="M215.99609,48H180V36A28.03146,28.03146,0,0,0,152,8H104A28.03146,28.03146,0,0,0,76,36V48H39.99609a12,12,0,0,0,0,24h4V208a20.0226,20.0226,0,0,0,20,20h128a20.0226,20.0226,0,0,0,20-20V72h4a12,12,0,0,0,0-24ZM100,36a4.00458,4.00458,0,0,1,4-4h48a4.00458,4.00458,0,0,1,4,4V48H100Zm87.99609,168h-120V72h120ZM116,104v64a12,12,0,0,1-24,0V104a12,12,0,0,1,24,0Zm48,0v64a12,12,0,0,1-24,0V104a12,12,0,0,1,24,0Z"/>
                  </svg>
                </button>
              </span>
            </div>
          </div>
          <a-empty v-else :description="t('result.budget.noDetails')" />
        </div>
      </a-card>
    </div>

    <div class="right-budget-summary" v-if="tripStore.tripPlan?.budget">
      <div class="budget-summary-panel">
        <div class="budget-summary-title">{{ t('result.budget.title') }}</div>
        <div class="budget-summary-total-wrap">
          <span class="budget-summary-currency">¥</span>
          <span class="budget-summary-total-value">{{ formatBudgetAmount(tripStore.tripPlan.budget?.total ?? 0) }}</span>
        </div>
        <div class="budget-summary-sub-grid">
          <div class="budget-summary-sub-item">
            <div class="budget-summary-sub-value">¥{{ formatBudgetAmount(tripStore.tripPlan.budget?.total_attractions ?? 0) }}</div>
            <div class="budget-summary-sub-label">{{ t('result.budget.attraction') }}</div>
          </div>
          <div class="budget-summary-sub-item">
            <div class="budget-summary-sub-value">¥{{ formatBudgetAmount(tripStore.tripPlan.budget?.total_hotels ?? 0) }}</div>
            <div class="budget-summary-sub-label">{{ t('result.budget.hotel') }}</div>
          </div>
          <div class="budget-summary-sub-item">
            <div class="budget-summary-sub-value">¥{{ formatBudgetAmount(tripStore.tripPlan.budget?.total_meals ?? 0) }}</div>
            <div class="budget-summary-sub-label">{{ t('result.budget.meal') }}</div>
          </div>
          <div class="budget-summary-sub-item">
            <div class="budget-summary-sub-value">¥{{ formatBudgetAmount(tripStore.tripPlan.budget?.total_transportation ?? 0) }}</div>
            <div class="budget-summary-sub-label">{{ t('result.budget.transport') }}</div>
          </div>
        </div>

        <div class="budget-pending-wrap">
          <div class="budget-pending-title">{{ t('result.budget.pendingTitle') }}</div>
          <div v-if="pendingBudgetItems.length === 0" class="budget-pending-empty">
            {{ t('result.budget.pendingEmpty') }}
          </div>
          <div v-else class="budget-pending-list">
            <div
              v-for="pendingItem in pendingBudgetItems"
              :key="pendingItem.uid"
              class="budget-pending-item"
            >
              <span class="budget-pending-name">{{ pendingItem.base.name }}</span>
              <a-button
                type="link"
                size="small"
                class="budget-restore-btn"
                @click="restoreBudgetItem(pendingItem)"
              >
                {{ t('result.budget.restore') }}
              </a-button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { message } from 'ant-design-vue'
import { useTripPlanStore } from '@/stores/tripPlan'

defineProps<{
  editMode: boolean
}>()

const { t } = useI18n()
const tripStore = useTripPlanStore()

type BudgetItemType = 'attraction' | 'hotel' | 'meal' | 'transport'
type BudgetSortMode = 'amountDesc' | 'amountAsc' | 'dayAsc' | 'dayDesc'

type BudgetDetailItem = {
  id: string
  type: BudgetItemType
  dayIndex: number | null
  dayNumber: number | null
  name: string
  amount: number
  sourceIndex?: number
}

type BudgetRestorePayload =
  | { type: 'attraction'; attraction: any; insertIndex: number }
  | { type: 'meal'; meal: any; insertIndex: number }
  | { type: 'hotel'; hotel: any; accommodation: string }
  | { type: 'transport'; transportation: string }

type BudgetRestoreItem = {
  uid: string
  base: BudgetDetailItem
  payload: BudgetRestorePayload
}

const budgetFilterType = ref<'all' | BudgetItemType>('all')
const budgetSortMode = ref<BudgetSortMode>('amountDesc')
const pendingBudgetItems = ref<BudgetRestoreItem[]>([])

const toBudgetNumber = (value: unknown): number => {
  const numeric = Number(value)
  if (!Number.isFinite(numeric) || numeric <= 0) return 0
  return numeric
}

const roundBudgetAmount = (value: number): number => {
  return Math.round((value + Number.EPSILON) * 100) / 100
}

const formatBudgetAmount = (value: number): string => {
  const rounded = roundBudgetAmount(value)
  return Number.isInteger(rounded) ? String(rounded) : rounded.toFixed(2)
}

const getBudgetTypeLabel = (type: BudgetItemType): string => {
  const labels: Record<BudgetItemType, string> = {
    attraction: t('result.budget.attraction'),
    hotel: t('result.budget.hotel'),
    meal: t('result.budget.meal'),
    transport: t('result.budget.transport'),
  }
  return labels[type]
}

const getMealLabel = (type: string): string => {
  const labels: Record<string, string> = {
    breakfast: t('result.meals.breakfast'),
    lunch: t('result.meals.lunch'),
    dinner: t('result.meals.dinner'),
    snack: t('result.meals.snack'),
  }
  return labels[type] || type
}

const cloneData = <T>(data: T): T => JSON.parse(JSON.stringify(data)) as T

const recalculateBudgetTotals = (transportationOverride?: number) => {
  if (!tripStore.tripPlan) return
  let attractionTotal = 0
  let hotelTotal = 0
  let mealTotal = 0
  tripStore.tripPlan.days.forEach((day) => {
    day.attractions.forEach((attraction) => {
      attractionTotal += toBudgetNumber(attraction.ticket_price)
    })
    if (day.hotel) {
      hotelTotal += toBudgetNumber(day.hotel.estimated_cost)
    }
    day.meals.forEach((meal) => {
      mealTotal += toBudgetNumber(meal.estimated_cost)
    })
  })
  const transportationTotal = roundBudgetAmount(
    transportationOverride ?? toBudgetNumber(tripStore.tripPlan.budget?.total_transportation)
  )
  tripStore.tripPlan.budget = {
    total_attractions: roundBudgetAmount(attractionTotal),
    total_hotels: roundBudgetAmount(hotelTotal),
    total_meals: roundBudgetAmount(mealTotal),
    total_transportation: transportationTotal,
    total: roundBudgetAmount(attractionTotal + hotelTotal + mealTotal + transportationTotal),
  }
}

const budgetItems = computed<BudgetDetailItem[]>(() => {
  if (!tripStore.tripPlan) return []
  const items: BudgetDetailItem[] = []
  tripStore.tripPlan.days.forEach((day, dayIndex) => {
    const dayNumber = day.day_index + 1
    day.attractions.forEach((attraction, attractionIndex) => {
      const amount = roundBudgetAmount(toBudgetNumber(attraction.ticket_price))
      if (amount <= 0) return
      items.push({
        id: `attraction-${dayIndex}-${attractionIndex}`,
        type: 'attraction',
        dayIndex,
        dayNumber,
        name: attraction.name,
        amount,
        sourceIndex: attractionIndex,
      })
    })
    if (day.hotel) {
      const amount = roundBudgetAmount(toBudgetNumber(day.hotel.estimated_cost))
      if (amount > 0) {
        items.push({
          id: `hotel-${dayIndex}`,
          type: 'hotel',
          dayIndex,
          dayNumber,
          name: day.hotel.name,
          amount,
        })
      }
    }
    day.meals.forEach((meal, mealIndex) => {
      const amount = roundBudgetAmount(toBudgetNumber(meal.estimated_cost))
      if (amount <= 0) return
      items.push({
        id: `meal-${dayIndex}-${mealIndex}`,
        type: 'meal',
        dayIndex,
        dayNumber,
        name: `${getMealLabel(meal.type)} · ${meal.name}`,
        amount,
        sourceIndex: mealIndex,
      })
    })
  })
  const transportTotal = roundBudgetAmount(toBudgetNumber(tripStore.tripPlan.budget?.total_transportation))
  const transportDays = tripStore.tripPlan.days
    .map((day, dayIndex) => ({ day, dayIndex }))
    .filter(({ day }) => Boolean(day.transportation && day.transportation.trim()))
  if (transportTotal > 0 && transportDays.length > 0) {
    const avg = roundBudgetAmount(transportTotal / transportDays.length)
    let remaining = transportTotal
    transportDays.forEach(({ day, dayIndex }, index) => {
      const amount = index === transportDays.length - 1 ? remaining : Math.min(avg, remaining)
      remaining = roundBudgetAmount(remaining - amount)
      items.push({
        id: `transport-${dayIndex}`,
        type: 'transport',
        dayIndex,
        dayNumber: day.day_index + 1,
        name: day.transportation,
        amount: roundBudgetAmount(amount),
      })
    })
  }
  return items
})

const filteredBudgetItems = computed<BudgetDetailItem[]>(() => {
  let items = budgetItems.value
  if (budgetFilterType.value !== 'all') {
    items = items.filter((item) => item.type === budgetFilterType.value)
  }
  const sorted = [...items]
  sorted.sort((a, b) => {
    const dayA = a.dayNumber ?? Number.MAX_SAFE_INTEGER
    const dayB = b.dayNumber ?? Number.MAX_SAFE_INTEGER
    switch (budgetSortMode.value) {
      case 'amountAsc': return a.amount - b.amount
      case 'dayAsc': return dayA - dayB || b.amount - a.amount
      case 'dayDesc': return dayB - dayA || b.amount - a.amount
      case 'amountDesc':
      default: return b.amount - a.amount
    }
  })
  return sorted
})

const editBudgetItemAmount = (item: BudgetDetailItem) => {
  if (!tripStore.tripPlan || item.dayIndex === null) return
  const day = tripStore.tripPlan.days[item.dayIndex]
  if (!day) return
  const input = window.prompt(
    t('result.budget.editPrompt', { name: item.name, amount: formatBudgetAmount(item.amount) }),
    formatBudgetAmount(item.amount)
  )
  if (input === null) return
  const numeric = Number(input.trim())
  if (!Number.isFinite(numeric) || numeric < 0) {
    message.warning(t('result.messages.budgetInvalidAmount'))
    return
  }
  const nextAmount = roundBudgetAmount(numeric)
  if (nextAmount === roundBudgetAmount(item.amount)) return
  const confirmed = window.confirm(
    t('result.budget.editConfirm', { name: item.name, amount: formatBudgetAmount(nextAmount) })
  )
  if (!confirmed) return
  let changed = false
  if (item.type === 'attraction' && typeof item.sourceIndex === 'number' && day.attractions[item.sourceIndex]) {
    day.attractions[item.sourceIndex].ticket_price = nextAmount
    changed = true
  }
  if (item.type === 'meal' && typeof item.sourceIndex === 'number' && day.meals[item.sourceIndex]) {
    day.meals[item.sourceIndex].estimated_cost = nextAmount
    changed = true
  }
  if (item.type === 'hotel' && day.hotel) {
    day.hotel.estimated_cost = nextAmount
    changed = true
  }
  const transportationTotal =
    item.type === 'transport'
      ? Math.max(0, roundBudgetAmount(toBudgetNumber(tripStore.tripPlan.budget?.total_transportation) - item.amount + nextAmount))
      : undefined
  if (item.type === 'transport' && day.transportation && day.transportation.trim()) {
    changed = true
  }
  if (!changed) return
  recalculateBudgetTotals(transportationTotal)
  sessionStorage.setItem('tripPlan', JSON.stringify(tripStore.tripPlan))
  message.success(t('result.messages.budgetAmountUpdated'))
}

const deleteBudgetItem = (item: BudgetDetailItem) => {
  if (!tripStore.tripPlan || item.dayIndex === null) return
  const day = tripStore.tripPlan.days[item.dayIndex]
  if (!day) return
  let changed = false
  let restorePayload: BudgetRestorePayload | null = null
  if (item.type === 'attraction' && typeof item.sourceIndex === 'number') {
    const attraction = day.attractions[item.sourceIndex]
    if (attraction) {
      restorePayload = { type: 'attraction', attraction: cloneData(attraction), insertIndex: item.sourceIndex }
      day.attractions.splice(item.sourceIndex, 1)
      changed = true
    }
  }
  if (item.type === 'meal' && typeof item.sourceIndex === 'number') {
    const meal = day.meals[item.sourceIndex]
    if (meal) {
      restorePayload = { type: 'meal', meal: cloneData(meal), insertIndex: item.sourceIndex }
      day.meals.splice(item.sourceIndex, 1)
      changed = true
    }
  }
  if (item.type === 'hotel') {
    if (day.hotel) {
      restorePayload = { type: 'hotel', hotel: cloneData(day.hotel), accommodation: day.accommodation || '' }
      day.hotel = undefined
      day.accommodation = ''
      changed = true
    }
  }
  if (item.type === 'transport') {
    if (day.transportation && day.transportation.trim()) {
      restorePayload = { type: 'transport', transportation: day.transportation }
      day.transportation = ''
      changed = true
    }
  }
  if (!changed || !restorePayload) return
  pendingBudgetItems.value.unshift({
    uid: `${item.id}-${Date.now()}`,
    base: cloneData(item),
    payload: restorePayload,
  })
  const transportationTotal =
    item.type === 'transport'
      ? Math.max(0, roundBudgetAmount(toBudgetNumber(tripStore.tripPlan.budget?.total_transportation) - roundBudgetAmount(item.amount)))
      : undefined
  recalculateBudgetTotals(transportationTotal)
  sessionStorage.setItem('tripPlan', JSON.stringify(tripStore.tripPlan))
  message.success(t('result.messages.budgetItemDeleted'))
}

const restoreBudgetItem = (pendingItem: BudgetRestoreItem) => {
  if (!tripStore.tripPlan || pendingItem.base.dayIndex === null) return
  const day = tripStore.tripPlan.days[pendingItem.base.dayIndex]
  if (!day) return
  let changed = false
  if (pendingItem.payload.type === 'attraction') {
    const insertAt = Math.max(0, Math.min(pendingItem.payload.insertIndex, day.attractions.length))
    day.attractions.splice(insertAt, 0, cloneData(pendingItem.payload.attraction))
    changed = true
  }
  if (pendingItem.payload.type === 'meal') {
    const insertAt = Math.max(0, Math.min(pendingItem.payload.insertIndex, day.meals.length))
    day.meals.splice(insertAt, 0, cloneData(pendingItem.payload.meal))
    changed = true
  }
  if (pendingItem.payload.type === 'hotel') {
    day.hotel = cloneData(pendingItem.payload.hotel)
    day.accommodation = pendingItem.payload.accommodation
    changed = true
  }
  if (pendingItem.payload.type === 'transport') {
    day.transportation = pendingItem.payload.transportation
    changed = true
  }
  if (!changed) return
  const transportationTotal =
    pendingItem.base.type === 'transport'
      ? roundBudgetAmount(toBudgetNumber(tripStore.tripPlan.budget?.total_transportation) + pendingItem.base.amount)
      : undefined
  recalculateBudgetTotals(transportationTotal)
  pendingBudgetItems.value = pendingBudgetItems.value.filter((item) => item.uid !== pendingItem.uid)
  sessionStorage.setItem('tripPlan', JSON.stringify(tripStore.tripPlan))
  message.success(t('result.messages.budgetItemRestored'))
}
</script>

<style scoped>
.top-info-section {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.left-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section-shellless {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}

.section-shellless:hover {
  box-shadow: none !important;
  border-color: transparent !important;
}

:deep(.section-shellless > .ant-card-head) {
  display: none !important;
}

:deep(.section-shellless > .ant-card-body) {
  padding: 0 !important;
  background: rgba(3, 8, 13, 0.726);
  border-radius: 14px;
}

.budget-card {
  height: fit-content;
}

.budget-detail-panel {
  min-height: 100%;
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: rgba(3, 10, 15, 0.88);
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.budget-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.12);
}

.budget-toolbar-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.budget-toolbar-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.72);
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.budget-select {
  width: 180px;
}

.budget-select :deep(.ant-select-selector) {
  border-radius: 10px !important;
  border-color: rgba(255, 255, 255, 0.24) !important;
  background: rgba(0, 0, 0, 0.2) !important;
  color: rgba(255, 255, 255, 0.86) !important;
}

.budget-select :deep(.ant-select-arrow) {
  color: rgba(255, 255, 255, 0.72) !important;
}

.budget-detail-list {
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 12px;
  overflow: hidden;
  background: rgba(0, 0, 0, 0.18);
}

.budget-detail-row {
  display: grid;
  grid-template-columns: 112px 96px minmax(0, 1fr) 120px 86px;
  align-items: center;
  gap: 10px;
  padding: 11px 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.01);
}

.budget-detail-row:last-child {
  border-bottom: none;
}

.budget-detail-header {
  background: rgba(255, 255, 255, 0.04);
  font-size: 12px;
  color: rgba(255, 255, 255, 0.64);
  letter-spacing: 0.03em;
  text-transform: uppercase;
}

.budget-detail-type,
.budget-detail-day,
.budget-detail-name,
.budget-detail-amount {
  color: rgba(255, 255, 255, 0.86);
  font-size: 13px;
}

.budget-detail-name {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.budget-detail-amount {
  font-weight: 600;
  color: #ffd5c6;
}

.budget-action-wrap {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.budget-icon-btn {
  width: 22px;
  height: 22px;
  border: none;
  background: transparent;
  padding: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.budget-icon-btn svg {
  width: 16px;
  height: 16px;
}

.budget-edit-btn {
  color: rgba(255, 255, 255, 0.68);
}

.budget-delete-btn {
  color: rgba(255, 255, 255, 0.68);
}

.budget-edit-btn:hover,
.budget-delete-btn:hover {
  color: #fff;
  transform: scale(1.1);
}

.right-budget-summary {
  flex: 0 0 360px;
}

.budget-summary-panel {
  min-height: 100%;
  border-radius: 14px;
  border: 1.2px solid rgba(255, 255, 255, 0.14);
  background: rgba(3, 10, 15, 0.88);
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.budget-summary-title {
  color: rgba(255, 255, 255, 0.92);
  font-size: 34px;
  font-weight: 300;
  letter-spacing: 0.02em;
  line-height: 1;
}

.budget-summary-total-wrap {
  display: flex;
  align-items: flex-start;
  gap: 4px;
}

.budget-summary-currency {
  font-size: 42px;
  line-height: 1;
  color: rgba(255, 255, 255, 0.9);
}

.budget-summary-total-value {
  font-size: 78px;
  line-height: 0.88;
  font-weight: 300;
  color: rgba(255, 255, 255, 0.96);
  letter-spacing: 0.01em;
}

.budget-summary-sub-grid {
  margin-top: 6px;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px 12px;
}

.budget-summary-sub-item {
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: 8px;
}

.budget-summary-sub-value {
  font-size: 32px;
  line-height: 1;
  color: #ffd4c3;
}

.budget-summary-sub-label {
  margin-top: 6px;
  font-size: 12px;
  line-height: 1.4;
  letter-spacing: 0.04em;
  color: rgba(255, 255, 255, 0.65);
  text-transform: uppercase;
}

.budget-pending-wrap {
  margin-top: 4px;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.12);
}

.budget-pending-title {
  font-size: 12px;
  letter-spacing: 0.04em;
  color: rgba(255, 255, 255, 0.72);
  margin-bottom: 8px;
  text-transform: uppercase;
}

.budget-pending-empty {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.45);
  padding: 8px 0;
}

.budget-pending-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.budget-pending-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 8px 10px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.09);
}

.budget-pending-name {
  flex: 1;
  min-width: 0;
  color: rgba(255, 255, 255, 0.84);
  font-size: 13px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.budget-restore-btn {
  padding: 0 !important;
}

@media (max-width: 768px) {
  .top-info-section {
    flex-direction: column;
  }

  .left-info {
    flex: auto;
  }

  .right-budget-summary {
    flex: auto;
    width: 100%;
  }

  .budget-summary-panel {
    min-height: auto;
  }

  .budget-summary-title {
    font-size: 30px;
  }

  .budget-summary-total-value {
    font-size: 56px;
  }

  .budget-summary-sub-value {
    font-size: 24px;
  }

  .budget-toolbar {
    gap: 8px;
  }

  .budget-detail-panel {
    min-height: auto;
    padding: 14px;
  }

  .budget-toolbar-item {
    width: 100%;
    justify-content: space-between;
  }

  .budget-select {
    width: 170px;
  }

  .budget-detail-list {
    overflow-x: auto;
  }

  .budget-detail-row {
    min-width: 620px;
  }
}
</style>
