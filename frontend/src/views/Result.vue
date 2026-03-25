<template>
  <div class="result-container">
    <div class="lower-shade"></div>

    <NavBar @brand-click="goBack" @cta-click="goBack" />

    <main class="result-main">
      <div v-if="tripStore.tripPlan" class="content-wrapper">
        <div class="top-switch-nav">
          <div class="top-switch-menu-wrap">
            <a-menu class="top-switch-menu" mode="horizontal" :selected-keys="[activeSection]" @click="scrollToSection">
              <a-menu-item key="overview">
                <span>{{ t('result.side.overview') }}</span>
              </a-menu-item>
              <a-menu-item key="budget" v-if="tripStore.tripPlan.budget">
                <span>{{ t('result.side.budget') }}</span>
              </a-menu-item>
              <a-menu-item key="map">
                <span>{{ t('result.side.map') }}</span>
              </a-menu-item>
              <a-menu-item key="days">
                <span>{{ t('result.side.days') }}</span>
              </a-menu-item>
              <a-menu-item key="knowledge-graph">
                <span>{{ t('result.side.graph') }}</span>
              </a-menu-item>
              <a-menu-item key="weather" v-if="tripStore.tripPlan.weather_info && tripStore.tripPlan.weather_info.length > 0">
                <span>{{ t('result.side.weather') }}</span>
              </a-menu-item>
            </a-menu>
          </div>

          <div class="top-switch-actions">
            <a-space size="middle" wrap>
              <a-button v-if="!editMode" @click="toggleEditMode" type="default">
                {{ t('result.editTrip') }}
              </a-button>
              <a-button v-else @click="saveChanges" type="primary">
                {{ t('result.saveChanges') }}
              </a-button>
              <a-button v-if="editMode" @click="cancelEdit" type="default">
                {{ t('result.cancelEdit') }}
              </a-button>

              <a-dropdown v-if="!editMode">
                <template #overlay>
                  <a-menu>
                    <a-menu-item key="image" @click="exportAsImage">
                      {{ t('result.exportImage') }}
                    </a-menu-item>
                    <a-menu-item key="pdf" @click="exportAsPDF">
                      {{ t('result.exportPdf') }}
                    </a-menu-item>
                  </a-menu>
                </template>
                <a-button type="default">
                  {{ t('result.exportTrip') }} <DownOutlined />
                </a-button>
              </a-dropdown>
            </a-space>
          </div>
        </div>

        <!-- Section components -->
        <OverviewSection
          v-show="activeSection === 'overview'"
          :edit-mode="editMode"
          @navigate-to-days="goToDayFromOverview"
        />

        <!-- Budget + Map share the same wrapper row -->
        <div class="top-info-section" v-show="['budget', 'map'].includes(activeSection)">
          <BudgetSection
            v-show="activeSection === 'budget'"
            :edit-mode="editMode"
          />
          <div class="right-map" v-show="activeSection === 'map'">
            <MapSection :active="activeSection === 'map'" />
          </div>
        </div>

        <KnowledgeGraphSection
          v-show="activeSection === 'knowledge-graph'"
          :active="activeSection === 'knowledge-graph'"
        />

        <DaysSection
          v-show="activeSection === 'days'"
          :edit-mode="editMode"
          ref="daysSectionRef"
        />

        <WeatherSection
          v-show="activeSection === 'weather'"
        />
      </div>

      <div v-else class="empty-state-panel">
        <a-empty :description="t('result.noTripPlan')">
          <template #description>
            <span class="empty-desc">{{ t('result.noTripPlanDesc') }}</span>
          </template>
          <a-button class="empty-back-btn" type="primary" @click="goBack">{{ t('result.backCreateTrip') }}</a-button>
        </a-empty>
      </div>
    </main>

    <!-- 回到顶部按钮 -->
    <a-back-top :visibility-height="300">
      <div class="back-top-button">
        Top
      </div>
    </a-back-top>

    <AIChat />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { message } from 'ant-design-vue'
import { DownOutlined } from '@ant-design/icons-vue'
import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'
import NavBar from '@/components/NavBar.vue'
import AIChat from '@/components/AIChat.vue'
import OverviewSection from '@/components/result/OverviewSection.vue'
import BudgetSection from '@/components/result/BudgetSection.vue'
import MapSection from '@/components/result/MapSection.vue'
import DaysSection from '@/components/result/DaysSection.vue'
import KnowledgeGraphSection from '@/components/result/KnowledgeGraphSection.vue'
import WeatherSection from '@/components/result/WeatherSection.vue'
import { useTripPlanStore } from '@/stores/tripPlan'
import { useCacheStore } from '@/stores/cache'

const router = useRouter()
const { t } = useI18n()
const tripStore = useTripPlanStore()
const cacheStore = useCacheStore()

const activeSection = ref('overview')
const editMode = ref(false)
const daysSectionRef = ref<InstanceType<typeof DaysSection> | null>(null)

onMounted(async () => {
  tripStore.loadFromSession()
  if (!tripStore.tripPlan) return
  // Load attraction photos
  const allAttractions = tripStore.tripPlan.days.flatMap(day => day.attractions)
  await cacheStore.loadAttractionPhotos(allAttractions.map(a => ({ name: a.name })))
})

const goBack = () => {
  router.push('/')
}

const scrollToSection = ({ key }: { key: string }) => {
  if (key.startsWith('day-')) {
    const dayIndex = Number(key.replace('day-', ''))
    if (!Number.isNaN(dayIndex)) {
      if (daysSectionRef.value) daysSectionRef.value.activeDays = [dayIndex]
      activeSection.value = 'days'
      return
    }
  }
  activeSection.value = key
}

const goToDayFromOverview = (dayArrayIndex: number) => {
  if (daysSectionRef.value) daysSectionRef.value.activeDays = [dayArrayIndex]
  activeSection.value = 'days'
}

const toggleEditMode = () => {
  tripStore.beginEdit()
  editMode.value = true
  message.info(t('result.messages.enterEditMode'))
}

const saveChanges = () => {
  tripStore.commitEdit()
  editMode.value = false
  message.success(t('result.messages.changesSaved'))
}

const cancelEdit = () => {
  tripStore.cancelEdit()
  editMode.value = false
  message.info(t('result.messages.editCanceled'))
}

// ========== Export helpers ==========
const buildExportHTML = (): string => {
  if (!tripStore.tripPlan) return ''
  const tp = tripStore.tripPlan as any

  const mealLabels: Record<string, string> = {
    breakfast: t('result.meals.breakfast'),
    lunch: t('result.meals.lunch'),
    dinner: t('result.meals.dinner'),
    snack: t('result.meals.snack'),
  }

  let daysHTML = ''
  tp.days.forEach((day: any) => {
    let attractionsHTML = ''
    day.attractions.forEach((a: any, ai: number) => {
      const photoUrl = cacheStore.attractionPhotos[a.name] || ''
      const durationText = t('result.export.durationLine', { duration: a.visit_duration || '—' })
      const imgTag = photoUrl
        ? `<img src="${photoUrl}" style="width:100%;height:160px;object-fit:cover;border-radius:8px;margin-bottom:8px;" crossorigin="anonymous" />`
        : `<div style="width:100%;height:80px;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:8px;margin-bottom:8px;display:flex;align-items:center;justify-content:center;color:#fff;font-size:18px;font-weight:bold;">${a.name}</div>`
      attractionsHTML += `
        <div style="flex:0 0 48%;background:#fff;border-radius:10px;padding:14px;box-shadow:0 2px 8px rgba(0,0,0,0.07);margin-bottom:14px;">
          ${imgTag}
          <h4 style="margin:0 0 6px;font-size:15px;color:#1a1a1a;">${ai + 1}. ${a.name}</h4>
          <p style="margin:2px 0;font-size:12px;color:#555;">${a.address || '—'}</p>
          <p style="margin:2px 0;font-size:12px;color:#555;">${durationText}${a.ticket_price ? `  |  ¥${a.ticket_price}` : ''}</p>
          <p style="margin:4px 0;font-size:12px;color:#666;">${a.description || ''}</p>
        </div>`
    })

    let mealsHTML = ''
    if (day.meals && day.meals.length) {
      mealsHTML = `<div style="margin-top:10px;"><strong style="color:#333;">${t('result.export.mealTitle')}</strong><div style="display:flex;flex-wrap:wrap;gap:10px;margin-top:6px;">`
      day.meals.forEach((m: any) => {
        mealsHTML += `<div style="background:#fffbe6;padding:8px 14px;border-radius:8px;font-size:12px;color:#333;"><b>${mealLabels[m.type] || m.type}</b>: ${m.name || t('result.export.noMealRecommendation')}${m.estimated_cost ? ` (¥${m.estimated_cost})` : ''}</div>`
      })
      mealsHTML += '</div></div>'
    }

    daysHTML += `
      <div style="background:#ffffff;border-radius:14px;padding:20px;margin-bottom:18px;box-shadow:0 2px 10px rgba(0,0,0,0.06);">
        <h3 style="margin:0 0 14px;color:#667eea;font-size:18px;">${t('result.export.dayTitle', { day: day.day_index + 1 })} <span style="font-size:14px;color:#888;margin-left:8px;">${day.date || ''}</span></h3>
        <div style="display:flex;flex-wrap:wrap;gap:12px;">${attractionsHTML}</div>
        ${mealsHTML}
      </div>`
  })

  let budgetHTML = ''
  if (tp.budget) {
    const b = tp.budget
    budgetHTML = `
      <div style="background:#ffffff;border-radius:14px;padding:20px;margin-bottom:18px;box-shadow:0 2px 10px rgba(0,0,0,0.06);">
        <h3 style="margin:0 0 14px;color:#667eea;">${t('result.budget.title')}</h3>
        <div style="display:flex;flex-wrap:wrap;gap:10px;margin-bottom:14px;">
          <div style="flex:1;min-width:120px;background:#f5f7fa;padding:14px;border-radius:10px;text-align:center;">
            <div style="font-size:12px;color:#888;">${t('result.budget.attraction')}</div><div style="font-size:20px;font-weight:bold;color:#333;">¥${b.total_attractions || 0}</div>
          </div>
          <div style="flex:1;min-width:120px;background:#f5f7fa;padding:14px;border-radius:10px;text-align:center;">
            <div style="font-size:12px;color:#888;">${t('result.budget.hotel')}</div><div style="font-size:20px;font-weight:bold;color:#333;">¥${b.total_hotels || 0}</div>
          </div>
          <div style="flex:1;min-width:120px;background:#f5f7fa;padding:14px;border-radius:10px;text-align:center;">
            <div style="font-size:12px;color:#888;">${t('result.budget.meal')}</div><div style="font-size:20px;font-weight:bold;color:#333;">¥${b.total_meals || 0}</div>
          </div>
          <div style="flex:1;min-width:120px;background:#f5f7fa;padding:14px;border-radius:10px;text-align:center;">
            <div style="font-size:12px;color:#888;">${t('result.budget.transport')}</div><div style="font-size:20px;font-weight:bold;color:#333;">¥${b.total_transportation || 0}</div>
          </div>
        </div>
        <div style="background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;padding:16px 20px;border-radius:12px;display:flex;justify-content:space-between;align-items:center;">
          <span style="font-size:16px;">${t('result.budget.total')}</span>
          <span style="font-size:26px;font-weight:bold;">¥${b.total || 0}</span>
        </div>
      </div>`
  }

  let weatherHTML = ''
  if (tp.weather_info) {
    if (Array.isArray(tp.weather_info) && tp.weather_info.length > 0) {
      let weatherCards = ''
      tp.weather_info.forEach((w: any) => {
        weatherCards += `
          <div style="flex:1;min-width:180px;background:#2b2d3c;padding:16px;border-radius:12px;margin:5px;">
            <div style="text-align:center;color:#00e5ff;font-weight:bold;margin-bottom:12px;font-size:15px;">${w.date}</div>
            <div style="display:flex;align-items:center;margin-bottom:10px;">
              <div style="line-height:1.2;">
                <div style="font-size:12px;color:#99b0c9;margin-bottom:2px;">${t('result.export.daytime')}</div>
                <div style="font-size:14px;color:#fff;font-weight:600;">${w.day_weather} ${w.day_temp}°C</div>
              </div>
            </div>
            <div style="display:flex;align-items:center;margin-bottom:12px;">
              <div style="line-height:1.2;">
                <div style="font-size:12px;color:#99b0c9;margin-bottom:2px;">${t('result.export.nighttime')}</div>
                <div style="font-size:14px;color:#fff;font-weight:600;">${w.night_weather} ${w.night_temp}°C</div>
              </div>
            </div>
            <div style="border-top:1px solid rgba(255,255,255,0.1);padding-top:10px;text-align:center;font-size:12px;color:#99b0c9;">
              ${w.wind_direction} ${w.wind_power}
            </div>
          </div>`
      })
      weatherHTML = `
        <div style="background:#ffffff;border-radius:14px;padding:20px;margin-bottom:18px;box-shadow:0 2px 10px rgba(0,0,0,0.06);">
          <h3 style="margin:0 0 14px;color:#667eea;">${t('result.export.weatherTitle')}</h3>
          <div style="display:flex;flex-wrap:wrap;gap:10px;">${weatherCards}</div>
        </div>`
    } else {
      weatherHTML = `
        <div style="background:#ffffff;border-radius:14px;padding:20px;margin-bottom:18px;box-shadow:0 2px 10px rgba(0,0,0,0.06);">
          <h3 style="margin:0 0 10px;color:#667eea;">${t('result.export.weatherTitle')}</h3>
          <p style="font-size:14px;color:#333;line-height:1.8;">${typeof tp.weather_info === 'string' ? tp.weather_info : JSON.stringify(tp.weather_info)}</p>
        </div>`
    }
  }

  let hotelHTML = ''
  if (tp.hotel_recommendations && tp.hotel_recommendations.length) {
    let hotelItems = ''
    tp.hotel_recommendations.forEach((h: any) => {
      hotelItems += `<div style="background:#e3f2fd;padding:12px 16px;border-radius:10px;margin-bottom:8px;">
        <b style="color:#1565c0;">${h.name || t('result.export.hotelFallback')}</b>
        ${h.price ? `<span style="float:right;color:#e65100;font-weight:bold;">¥${h.price}${t('result.export.perNight')}</span>` : ''}
        ${h.address ? `<p style="margin:4px 0 0;font-size:12px;color:#555;">${h.address}</p>` : ''}
      </div>`
    })
    hotelHTML = `
      <div style="background:#ffffff;border-radius:14px;padding:20px;margin-bottom:18px;box-shadow:0 2px 10px rgba(0,0,0,0.06);">
        <h3 style="margin:0 0 14px;color:#1976d2;">${t('result.hotelTitle')}</h3>
        ${hotelItems}
      </div>`
  }

  return `
    <div style="width:800px;padding:30px;background:#f0f2f5;font-family:'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;color:#333;">
      <div style="text-align:center;margin-bottom:24px;">
        <h1 style="margin:0;font-size:28px;color:#333;">${t('result.export.title', { city: tp.city })}</h1>
        <p style="margin:6px 0 0;font-size:14px;color:#888;">${t('result.export.subtitle', {
          start: tp.start_date || '',
          end: tp.end_date || '',
          days: tp.days?.length || 0,
        })}</p>
        ${tp.overall_suggestions ? `<p style="margin:8px auto 0;max-width:600px;font-size:13px;color:#666;line-height:1.6;">${tp.overall_suggestions}</p>` : ''}
      </div>
      ${budgetHTML}
      ${daysHTML}
      ${hotelHTML}
      ${weatherHTML}
      <div style="text-align:center;padding:16px;color:#aaa;font-size:12px;">${t('result.export.footer')}</div>
    </div>`
}

const exportAsImage = async () => {
  try {
    message.loading({ content: t('result.messages.generatingImage'), key: 'export', duration: 0 })
    const exportContainer = document.createElement('div')
    exportContainer.innerHTML = buildExportHTML()
    exportContainer.style.position = 'absolute'
    exportContainer.style.left = '-9999px'
    document.body.appendChild(exportContainer)
    const canvas = await html2canvas(exportContainer, {
      backgroundColor: '#f0f2f5',
      scale: 2,
      logging: false,
      useCORS: true,
      allowTaint: true,
    })
    document.body.removeChild(exportContainer)
    const link = document.createElement('a')
    link.download = `${t('result.export.filePrefix')}_${tripStore.tripPlan?.city}_${new Date().getTime()}.png`
    link.href = canvas.toDataURL('image/png')
    link.click()
    message.success({ content: t('result.messages.imageSuccess'), key: 'export' })
  } catch (error: any) {
    console.error('导出图片失败:', error)
    message.error({ content: t('result.messages.imageFailed', { error: error.message }), key: 'export' })
  }
}

const exportAsPDF = async () => {
  try {
    message.loading({ content: t('result.messages.generatingPdf'), key: 'export', duration: 0 })
    const exportContainer = document.createElement('div')
    exportContainer.innerHTML = buildExportHTML()
    exportContainer.style.position = 'absolute'
    exportContainer.style.left = '-9999px'
    document.body.appendChild(exportContainer)
    const canvas = await html2canvas(exportContainer, {
      backgroundColor: '#f0f2f5',
      scale: 2,
      logging: false,
      useCORS: true,
      allowTaint: true,
    })
    document.body.removeChild(exportContainer)
    const imgData = canvas.toDataURL('image/png')
    const pdf = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' })
    const imgWidth = 210
    const imgHeight = (canvas.height * imgWidth) / canvas.width
    let heightLeft = imgHeight
    let position = 0
    pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
    heightLeft -= 297
    while (heightLeft > 0) {
      position = heightLeft - imgHeight
      pdf.addPage()
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
      heightLeft -= 297
    }
    pdf.save(`${t('result.export.filePrefix')}_${tripStore.tripPlan?.city}_${new Date().getTime()}.pdf`)
    message.success({ content: t('result.messages.pdfSuccess'), key: 'export' })
  } catch (error: any) {
    console.error('导出PDF失败:', error)
    message.error({ content: t('result.messages.pdfFailed', { error: error.message }), key: 'export' })
  }
}
</script>

<style scoped>
/* ===== Landing 同款视觉基底 - 结果页 ===== */

.result-container {
  min-height: 100vh;
  background: linear-gradient(180deg, #0d171d 0%, #142430 58%, #0f1a22 100%);
  color: #ecf3fa;
  position: relative;
  isolation: isolate;
  overflow-x: hidden;
}

.lower-shade {
  position: fixed;
  inset: 0% 0 -1px 0;
  z-index: 0;
  pointer-events: none;
  background: rgba(6, 14, 20, 0.72);
}

.lower-shade::before {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  top: -28px;
  height: 28px;
  background: linear-gradient(to bottom, rgba(6, 14, 20, 0), rgba(6, 14, 20, 0.92));
}

.result-main {
  position: relative;
  z-index: 2;
  padding: 70px 20px 44px;
}

.content-wrapper {
  max-width: 1400px;
  margin: 0 auto;
  display: block;
  border: 1.2px solid rgba(236, 243, 250, 0.2);
  border-radius: 22px;
  background: rgba(12, 23, 32, 0.56);
  backdrop-filter: blur(18px);
  box-shadow: 0 24px 80px rgba(4, 11, 18, 0.52);
  padding: 20px;
}

.top-switch-nav {
  display: flex;
  align-items: center;
  gap: 12px;
  justify-content: space-between;
  margin-bottom: 16px;
}

.top-switch-menu-wrap {
  flex: 1;
  min-width: 0;
  overflow-x: hidden;
  overflow-y: hidden;
}

.top-switch-menu {
  width: 100%;
  min-width: 0;
  border-bottom: 1px solid rgba(236, 243, 250, 0.16) !important;
  background: transparent !important;
}

.top-switch-menu :deep(.ant-menu-item) {
  color: rgba(232, 239, 247, 0.75) !important;
  border-radius: 10px 10px 0 0;
  margin-right: 4px !important;
  transition: all 0.2s ease;
}

.top-switch-menu :deep(.ant-menu-item:hover) {
  color: rgba(236, 243, 250, 0.95) !important;
}

.top-switch-menu :deep(.ant-menu-item-selected) {
  color: #ffe3d6 !important;
}

.top-switch-menu :deep(.ant-menu-item-selected::after),
.top-switch-menu :deep(.ant-menu-item-active::after),
.top-switch-menu :deep(.ant-menu-item:hover::after) {
  border-bottom-color: #d76e42 !important;
}

.top-switch-menu :deep(.ant-menu-overflow) {
  flex-wrap: nowrap;
}

.top-switch-actions {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
}

.top-switch-actions :deep(.ant-btn-default) {
  border: 1.2px solid rgba(236, 243, 250, 0.24) !important;
  background: rgba(12, 23, 32, 0.56) !important;
  color: #ecf3fa !important;
  border-radius: 999px !important;
  height: 34px !important;
  padding: 0 12px !important;
  font-size: 12px !important;
  font-weight: 600;
  letter-spacing: 0.04em;
}

.top-switch-actions :deep(.ant-btn-primary) {
  border: 1.2px solid rgba(215, 110, 66, 0.5) !important;
  background: rgba(215, 110, 66, 0.24) !important;
  color: #ffe3d6 !important;
  border-radius: 999px !important;
  height: 34px !important;
  padding: 0 12px !important;
  font-size: 12px !important;
  font-weight: 600;
  letter-spacing: 0.04em;
  box-shadow: none !important;
}

.empty-state-panel {
  max-width: 900px;
  margin: 0 auto;
  border: 1.2px solid rgba(236, 243, 250, 0.2);
  border-radius: 22px;
  background: rgba(12, 23, 32, 0.56);
  backdrop-filter: blur(18px);
  box-shadow: 0 24px 80px rgba(4, 11, 18, 0.52);
  padding: 44px 20px;
  text-align: center;
}

.empty-desc {
  color: rgba(228, 236, 245, 0.72);
}

.empty-back-btn {
  border: 1.2px solid rgba(215, 110, 66, 0.5) !important;
  background: rgba(215, 110, 66, 0.24) !important;
  color: #ffe3d6 !important;
  border-radius: 999px !important;
  min-height: 34px !important;
  padding: 0 14px !important;
  font-size: 12px !important;
  font-weight: 600;
  letter-spacing: 0.04em;
  box-shadow: none !important;
}

/* 顶部信息区布局 */
.top-info-section {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.right-map {
  flex: 1;
}

/* 回到顶部按钮 */
.back-top-button {
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, #d76e42 0%, #a14625 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.03em;
  box-shadow: 0 4px 20px rgba(215, 110, 66, 0.38);
  cursor: pointer;
  transition: all 0.3s ease;
}

.back-top-button:hover {
  transform: scale(1.15);
  box-shadow: 0 6px 28px rgba(215, 110, 66, 0.48);
}

/* 卡片样式 - 玻璃拟态暗色 */
:deep(.ant-card) {
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.04) !important;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.08) !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  margin-bottom: 20px;
  transition: all 0.3s ease;
  animation: fadeInUp 0.6s ease-out;
  color: rgba(255, 255, 255, 0.8);
}

:deep(.ant-card:hover) {
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
  border-color: rgba(215, 110, 66, 0.26) !important;
}

:deep(.ant-card-head) {
  background: linear-gradient(135deg, rgba(215, 110, 66, 0.2) 0%, rgba(161, 70, 37, 0.14) 100%) !important;
  color: #ffe3d6 !important;
  border-radius: 16px 16px 0 0;
  font-weight: 600;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06) !important;
}

:deep(.ant-card-head-title) {
  color: #ffe3d6 !important;
  font-size: 18px;
}

:deep(.ant-card-head-title span) {
  color: #ffe3d6 !important;
}

:deep(.ant-card-body) {
  color: rgba(255, 255, 255, 0.8);
}

:deep(.ant-card-body p) {
  color: rgba(255, 255, 255, 0.7);
}

:deep(.ant-card-body strong) {
  color: rgba(255, 255, 255, 0.5);
}

/* Empty 暗色 */
:deep(.ant-empty-description) {
  color: rgba(255, 255, 255, 0.4) !important;
}

/* 动画 */
@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .result-main {
    padding: 60px 10px 24px;
  }

  .content-wrapper {
    padding: 14px;
  }

  .top-switch-nav {
    gap: 8px;
  }

  .top-switch-menu-wrap {
    overflow-x: auto;
    overflow-y: hidden;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
    -ms-overflow-style: none;
  }

  .top-switch-menu {
    min-width: max-content;
  }

  .top-switch-menu-wrap::-webkit-scrollbar {
    width: 0;
    height: 0;
    display: none;
  }

  .top-switch-actions {
    max-width: 44%;
  }

  .top-switch-actions :deep(.ant-space) {
    column-gap: 6px !important;
    row-gap: 6px !important;
  }

  .top-switch-actions :deep(.ant-btn-default),
  .top-switch-actions :deep(.ant-btn-primary) {
    height: 32px !important;
    padding: 0 10px !important;
    font-size: 11px !important;
  }

  .top-info-section {
    flex-direction: column;
  }
}
</style>

<style>
:root {
  --tripstar-map-accent: #d76e42;
  --tripstar-map-accent-strong: #a14625;
  --tripstar-map-surface: rgba(17, 29, 38, 0.96);
  --tripstar-map-border: rgba(215, 110, 66, 0.35);
  --tripstar-map-text-main: #f6fbff;
  --tripstar-map-text-sub: rgba(240, 246, 252, 0.72);
}

.tripstar-map-marker {
  position: relative;
  width: 34px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.tripstar-map-marker__core {
  position: relative;
  z-index: 1;
  width: 20px;
  height: 20px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.tripstar-map-marker__icon {
  width: 12px;
  height: 12px;
  stroke: #ffffff;
  stroke-width: 1.6;
  stroke-linecap: round;
  stroke-linejoin: round;
  fill: none;
}

.tripstar-map-marker__index {
  position: absolute;
  top: calc(100% + 1px);
  left: 50%;
  transform: translateX(-50%);
  font-size: 15px;
  font-weight: bold;
  line-height: 1;
  color: #ffffff;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.9);
  white-space: nowrap;
  pointer-events: none;
}

.tripstar-map-tooltip {
  max-width: min(320px, calc(100vw - 40px));
  background: transparent;
  border: none;
  box-shadow: none;
  padding: 0;
  color: var(--tripstar-map-text-main);
  pointer-events: none;
}

.tripstar-map-tooltip__line {
  margin: 0;
  font-size: 12px;
  line-height: 1.45;
  color: #ffd6c7 !important;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.85);
  background-color: rgba(0, 0, 0, 0.05);
  white-space: nowrap;
}

.tripstar-map-tooltip__line + .tripstar-map-tooltip__line {
  margin-top: 2px;
}

.tripstar-map-tooltip__line--title {
  font-size: 15px;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.85);
  font-weight: 700;
  color: #ffffff !important;
}

#map-canvas .amap-info-content {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 0 !important;
}

#map-canvas .amap-info-sharp {
  display: none !important;
}
</style>
