<template>
  <a-card :bordered="false" class="days-card section-shellless">
    <a-collapse v-model:activeKey="activeDays" accordion>
      <a-collapse-panel
        v-for="(day, index) in tripStore.tripPlan!.days"
        :key="index"
        :id="`day-${index}`"
      >
        <template #header>
          <div class="day-header">
            <span class="day-title">{{ t('common.dayNumber', { day: day.day_index + 1 }) }}</span>
            <span class="day-date">{{ day.date }}</span>
          </div>
        </template>

        <!-- 行程基本信息 -->
        <div class="day-info">
          <div class="info-row">
            <span class="label">{{ t('result.dayDescription') }}</span>
            <span class="value">{{ day.description }}</span>
          </div>
          <div class="info-row">
            <span class="label">{{ t('result.dayTransport') }}</span>
            <span class="value">{{ day.transportation }}</span>
          </div>
          <div class="info-row">
            <span class="label">{{ t('result.dayAccommodation') }}</span>
            <span class="value">{{ day.accommodation }}</span>
          </div>
        </div>

        <!-- 景点安排 -->
        <a-divider orientation="left">{{ t('result.attractionTitle') }}</a-divider>
        <a-list
          :data-source="day.attractions"
          :grid="{ gutter: 16, column: 2 }"
        >
          <template #renderItem="{ item, index: attrIndex }">
            <a-list-item>
              <a-card :title="item.name" size="small" class="attraction-card">
                <!-- 编辑模式下的操作按钮 -->
                <template #extra v-if="editMode">
                  <a-space>
                    <a-button
                      size="small"
                      @click="handleMoveAttraction(day.day_index, attrIndex, 'up')"
                      :disabled="attrIndex === 0"
                    >
                      Up
                    </a-button>
                    <a-button
                      size="small"
                      @click="handleMoveAttraction(day.day_index, attrIndex, 'down')"
                      :disabled="attrIndex === day.attractions.length - 1"
                    >
                      Down
                    </a-button>
                    <a-button
                      size="small"
                      danger
                      @click="handleDeleteAttraction(day.day_index, attrIndex)"
                    >
                      {{ t('common.delete') }}
                    </a-button>
                  </a-space>
                </template>

                <!-- 景点图片 -->
                <div class="attraction-image-wrapper">
                  <img
                    :src="getAttractionImage(item.name, attrIndex)"
                    :alt="item.name"
                    class="attraction-image"
                    @error="handleImageError"
                  />
                  <div class="attraction-badge">
                    <span class="badge-number">{{ attrIndex + 1 }}</span>
                  </div>
                  <div v-if="item.ticket_price" class="price-tag">
                    ¥{{ item.ticket_price }}
                  </div>
                </div>

                <!-- 编辑模式下可编辑的字段 -->
                <div v-if="editMode">
                  <p><strong>{{ t('result.fieldAddress') }}:</strong></p>
                  <a-input v-model:value="item.address" size="small" style="margin-bottom: 8px" />

                  <p><strong>{{ t('result.fieldVisitDurationMinutes') }}:</strong></p>
                  <a-input-number v-model:value="item.visit_duration" :min="10" :max="480" size="small" style="width: 100%; margin-bottom: 8px" />

                  <p><strong>{{ t('result.fieldDescription') }}:</strong></p>
                  <a-textarea v-model:value="item.description" :rows="2" size="small" style="margin-bottom: 8px" />
                </div>

                <!-- 查看模式 -->
                <div v-else>
                  <p><strong>{{ t('result.fieldAddress') }}:</strong> {{ item.address }}</p>
                  <p><strong>{{ t('result.fieldVisitDuration') }}:</strong> {{ item.visit_duration }}{{ t('result.minuteUnit') }}</p>
                  <p><strong>{{ t('result.fieldDescription') }}:</strong> {{ item.description }}</p>
                  <p v-if="item.rating"><strong>{{ t('result.fieldRating') }}:</strong> {{ item.rating }}</p>
                </div>
              </a-card>
            </a-list-item>
          </template>
        </a-list>

        <!-- 酒店推荐 -->
        <a-divider v-if="day.hotel" orientation="left">{{ t('result.hotelTitle') }}</a-divider>
        <a-card v-if="day.hotel" size="small" class="hotel-card">
          <template #title>
            <span class="hotel-title">{{ day.hotel.name }}</span>
          </template>
          <a-descriptions :column="2" size="small">
            <a-descriptions-item :label="t('result.fieldAddress')">{{ day.hotel.address }}</a-descriptions-item>
            <a-descriptions-item :label="t('result.fieldType')">{{ day.hotel.type }}</a-descriptions-item>
            <a-descriptions-item :label="t('result.fieldPriceRange')">{{ day.hotel.price_range }}</a-descriptions-item>
            <a-descriptions-item :label="t('result.fieldRating')">{{ day.hotel.rating }}</a-descriptions-item>
            <a-descriptions-item :label="t('result.fieldDistance')" :span="2">{{ day.hotel.distance }}</a-descriptions-item>
          </a-descriptions>
        </a-card>

        <!-- 餐饮安排 -->
        <a-divider orientation="left">{{ t('result.mealsTitle') }}</a-divider>
        <a-descriptions :column="1" bordered size="small">
          <a-descriptions-item
            v-for="meal in day.meals"
            :key="meal.type"
            :label="getMealLabel(meal.type)"
          >
            {{ meal.name }}
            <span v-if="meal.description"> - {{ meal.description }}</span>
          </a-descriptions-item>
        </a-descriptions>
      </a-collapse-panel>
    </a-collapse>
  </a-card>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { message } from 'ant-design-vue'
import { useTripPlanStore } from '@/stores/tripPlan'
import { useCacheStore } from '@/stores/cache'

defineProps<{
  editMode: boolean
}>()

const { t } = useI18n()
const tripStore = useTripPlanStore()
const cacheStore = useCacheStore()

const activeDays = ref<number[]>([0])

const getMealLabel = (type: string): string => {
  const labels: Record<string, string> = {
    breakfast: t('result.meals.breakfast'),
    lunch: t('result.meals.lunch'),
    dinner: t('result.meals.dinner'),
    snack: t('result.meals.snack'),
  }
  return labels[type] || type
}

const getAttractionImage = (name: string, _index: number): string => {
  if (cacheStore.attractionPhotos[name]) {
    return cacheStore.attractionPhotos[name]
  }
  const bg = '#1a262f'
  const textColor = 'rgba(255,255,255,0.4)'
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300">
    <rect width="400" height="300" fill="${bg}"/>
    <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-family="sans-serif" font-size="24" font-weight="bold" fill="${textColor}">${name}</text>
  </svg>`
  return `data:image/svg+xml;base64,${btoa(unescape(encodeURIComponent(svg)))}`
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  const label = encodeURIComponent(t('result.imageLoadFailed'))
  img.src = `data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect width="400" height="300" fill="%231a262f"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" font-family="sans-serif" font-size="18" fill="rgba(255,255,255,0.4)"%3E${label}%3C/text%3E%3C/svg%3E`
}

const handleDeleteAttraction = (dayIndex: number, attrIndex: number) => {
  if (!tripStore.tripPlan) return
  const day = tripStore.tripPlan.days[dayIndex]
  if (day.attractions.length <= 1) {
    message.warning(t('result.messages.keepOneAttraction'))
    return
  }
  tripStore.deleteAttraction(dayIndex, attrIndex)
  message.success(t('result.messages.attractionDeleted'))
}

const handleMoveAttraction = (dayIndex: number, attrIndex: number, direction: 'up' | 'down') => {
  tripStore.moveAttraction(dayIndex, attrIndex, direction)
}

// Expose activeDays for parent to control
defineExpose({ activeDays })
</script>

<style scoped>
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

.days-card {
  margin-top: 20px;
}

.day-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.day-title {
  font-size: 18px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.85);
}

.day-date {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.35);
}

.day-info {
  margin-bottom: 20px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.info-row {
  display: flex;
  gap: 12px;
  margin-bottom: 8px;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-row .label {
  font-weight: 600;
  color: rgba(255, 255, 255, 0.45);
  min-width: 100px;
}

.info-row .value {
  color: rgba(255, 255, 255, 0.8);
  flex: 1;
}

.attraction-image-wrapper {
  position: relative;
  margin-bottom: 12px;
  border-radius: 12px;
  overflow: hidden;
}

.attraction-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
  transition: transform 0.4s ease;
}

.attraction-image-wrapper:hover .attraction-image {
  transform: scale(1.08);
}

.attraction-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  background: linear-gradient(135deg, #d76e42 0%, #a14625 100%);
  color: white;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  box-shadow: 0 4px 12px rgba(215, 110, 66, 0.35);
}

.badge-number {
  font-size: 18px;
}

.price-tag {
  position: absolute;
  top: 12px;
  right: 12px;
  background: rgba(215, 110, 66, 0.9);
  color: white;
  padding: 4px 14px;
  border-radius: 20px;
  font-weight: bold;
  font-size: 14px;
  box-shadow: 0 4px 12px rgba(215, 110, 66, 0.3);
  backdrop-filter: blur(10px);
}

.hotel-card {
  background: rgba(215, 110, 66, 0.1) !important;
  border: 1px solid rgba(215, 110, 66, 0.26) !important;
}

.hotel-card :deep(.ant-card-head) {
  background: linear-gradient(135deg, rgba(215, 110, 66, 0.9) 0%, rgba(161, 70, 37, 0.9) 100%) !important;
}

.hotel-title {
  color: white !important;
  font-weight: 600;
}

.hotel-card :deep(.ant-descriptions-item-label) {
  color: rgba(255, 255, 255, 0.5) !important;
}

.hotel-card :deep(.ant-descriptions-item-content) {
  color: rgba(255, 255, 255, 0.8) !important;
}

:deep(.ant-collapse) {
  border: none;
  background: transparent;
}

:deep(.ant-collapse-item) {
  margin-bottom: 16px;
  border: 1px solid rgba(255, 255, 255, 0.08) !important;
  border-radius: 16px !important;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.02);
}

:deep(.ant-collapse-header) {
  background: rgba(255, 255, 255, 0.04) !important;
  padding: 16px 20px !important;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8) !important;
}

:deep(.ant-collapse-expand-icon) {
  color: rgba(255, 255, 255, 0.4) !important;
}

:deep(.ant-collapse-content) {
  border-top: 1px solid rgba(255, 255, 255, 0.06) !important;
  background: transparent !important;
}

:deep(.ant-collapse-content-box) {
  padding: 20px;
  color: rgba(255, 255, 255, 0.7);
}

:deep(.ant-descriptions) {
  background: transparent;
}

:deep(.ant-descriptions-bordered .ant-descriptions-item-label) {
  background: rgba(255, 255, 255, 0.04) !important;
  color: rgba(255, 255, 255, 0.5) !important;
  border-color: rgba(255, 255, 255, 0.06) !important;
}

:deep(.ant-descriptions-bordered .ant-descriptions-item-content) {
  background: transparent !important;
  color: rgba(255, 255, 255, 0.8) !important;
  border-color: rgba(255, 255, 255, 0.06) !important;
}

:deep(.ant-descriptions-item-label) {
  color: rgba(255, 255, 255, 0.5) !important;
}

:deep(.ant-descriptions-item-content) {
  color: rgba(255, 255, 255, 0.8) !important;
}

:deep(.ant-divider) {
  border-color: rgba(255, 255, 255, 0.08) !important;
  color: rgba(255, 255, 255, 0.6) !important;
}

:deep(.ant-divider-inner-text) {
  color: rgba(255, 255, 255, 0.6) !important;
}

:deep(.ant-list-item) {
  transition: all 0.3s ease;
}

:deep(.ant-list-item:hover) {
  transform: scale(1.02);
}
</style>
