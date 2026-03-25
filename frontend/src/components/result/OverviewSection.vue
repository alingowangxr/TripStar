<template>
  <a-card
    id="overview"
    :bordered="false"
    class="overview-card section-shellless"
  >
    <div v-if="overviewAttractions.length > 0" ref="overviewSwiperContainerRef" class="overview-swiper">
      <div class="swiper">
        <div class="swiper-wrapper">
          <OverviewAttractionCard
            v-for="(item, index) in overviewAttractions"
            :key="`${item.dayArrayIndex}-${item.order}-${item.name}`"
            :item="item"
            :image-src="getAttractionImage(item.name, index)"
            :active="activeOverviewCard === index"
            @hover="setActiveOverviewCard(index)"
            @image-error="handleImageError"
            @select-day="emit('navigate-to-days', $event)"
          />
        </div>
      </div>
    </div>
    <a-empty v-else :description="t('common.noData')" />
    <div class="overview-meta">
      <span class="overview-meta-item" style="color: #ffd5c6; font-weight: 700;">
        {{ t('result.dateRange', { start: tripStore.tripPlan!.start_date, end: tripStore.tripPlan!.end_date }) }}
      </span>
      <span v-if="tripStore.tripPlan!.overall_suggestions" class="overview-meta-item">
        {{ tripStore.tripPlan!.overall_suggestions }}
      </span>
    </div>
  </a-card>
</template>

<script setup lang="ts">
import { ref, computed, watch, onUnmounted, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import Swiper from 'swiper'
import { EffectCoverflow, Keyboard, Mousewheel } from 'swiper/modules'
import OverviewAttractionCard from '@/components/OverviewAttractionCard.vue'
import { useTripPlanStore } from '@/stores/tripPlan'
import { useCacheStore } from '@/stores/cache'

defineProps<{
  editMode: boolean
}>()

const emit = defineEmits<{
  (e: 'navigate-to-days', dayIndex: number): void
}>()

const { t } = useI18n()
const tripStore = useTripPlanStore()
const cacheStore = useCacheStore()

const activeOverviewCard = ref(1)
const overviewSwiperContainerRef = ref<HTMLElement | null>(null)
let overviewSwiper: Swiper | null = null

type OverviewAttractionItem = {
  name: string
  address: string
  visit_duration: number
  description: string
  ticket_price?: number
  dayNumber: number
  dayArrayIndex: number
  order: number
}

const overviewAttractions = computed<OverviewAttractionItem[]>(() => {
  if (!tripStore.tripPlan) return []
  const items: OverviewAttractionItem[] = []
  tripStore.tripPlan.days.forEach((day, dayArrayIndex) => {
    const dayNumber =
      typeof day.day_index === 'number' && Number.isFinite(day.day_index)
        ? day.day_index + 1
        : dayArrayIndex + 1
    day.attractions.forEach((attraction, order) => {
      items.push({
        name: attraction.name,
        address: attraction.address,
        visit_duration: attraction.visit_duration,
        description: attraction.description,
        ticket_price: attraction.ticket_price,
        dayNumber,
        dayArrayIndex,
        order,
      })
    })
  })
  return items
})

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

const destroyOverviewSwiper = () => {
  if (overviewSwiper) {
    overviewSwiper.destroy(true, true)
    overviewSwiper = null
  }
}

const initOverviewSwiper = async () => {
  await nextTick()
  if (!overviewSwiperContainerRef.value || overviewAttractions.value.length === 0) {
    destroyOverviewSwiper()
    return
  }
  const root = overviewSwiperContainerRef.value.querySelector('.swiper') as HTMLElement | null
  if (!root) return
  destroyOverviewSwiper()
  overviewSwiper = new Swiper(root, {
    modules: [EffectCoverflow, Keyboard, Mousewheel],
    effect: 'coverflow',
    grabCursor: true,
    centeredSlides: true,
    coverflowEffect: {
      rotate: 0,
      stretch: 0,
      depth: 100,
      modifier: 2.5,
    },
    keyboard: { enabled: true },
    mousewheel: { thresholdDelta: 70 },
    spaceBetween: 30,
    loop: false,
    breakpoints: {
      640: { slidesPerView: 3 },
      1024: { slidesPerView: 4 },
    },
    on: {
      slideChange: (swiper) => {
        activeOverviewCard.value = swiper.activeIndex
      },
    },
  })
  const initialIndex = Math.min(1, overviewAttractions.value.length - 1)
  activeOverviewCard.value = initialIndex
  overviewSwiper.slideTo(initialIndex, 0, false)
}

const setActiveOverviewCard = (index: number) => {
  activeOverviewCard.value = index
  if (overviewSwiper && overviewSwiper.activeIndex !== index) {
    overviewSwiper.slideTo(index)
  }
}

watch(
  overviewAttractions,
  (items) => {
    if (items.length === 0) {
      activeOverviewCard.value = -1
      return
    }
    if (activeOverviewCard.value < 0 || activeOverviewCard.value >= items.length) {
      activeOverviewCard.value = Math.min(1, items.length - 1)
    }
    void initOverviewSwiper()
  },
  { immediate: true }
)

onUnmounted(() => {
  destroyOverviewSwiper()
})

// Initialize swiper on mount
initOverviewSwiper()
</script>

<style scoped>
@import 'swiper/css';

.overview-card {
  margin-bottom: 20px;
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

.overview-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 18px;
}

.overview-meta-item {
  display: inline-flex;
  align-items: center;
  padding: 3px 12px;
  color: rgba(236, 243, 250, 0.78);
  font-size: 12px;
  line-height: 1.5;
}

.overview-swiper {
  padding: 8px 2px 10px;
}

.overview-swiper .swiper {
  padding: 0 0 0.6rem;
  margin-top: -2rem;
  margin-bottom: -2rem;
  overflow: hidden;
  border-radius: 12px;
}

.overview-swiper .swiper-wrapper {
  align-items: flex-end;
  min-height: 32rem;
}

@media (max-width: 768px) {
  .overview-meta {
    gap: 8px;
    margin-bottom: 14px;
  }

  .overview-meta-item {
    width: 100%;
    border-radius: 12px;
  }

  .overview-swiper .swiper-wrapper {
    gap: 1rem;
    min-height: 27rem;
  }

  .overview-swiper .swiper {
    padding: 2.4rem 0 0.6rem;
  }
}
</style>
