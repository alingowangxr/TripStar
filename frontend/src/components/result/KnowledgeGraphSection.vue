<template>
  <a-card id="knowledge-graph" :bordered="false" class="kg-card section-shellless">
    <div id="kg-chart-container" style="width: 100%; height: 600px;"></div>
    <div class="kg-legend">
      <span v-for="cat in tripStore.graphCategories" :key="cat.name" class="kg-legend-item">
        <span class="kg-legend-dot" :style="getKgLegendDotStyle(cat.name)"></span>
        {{ getCategoryLabel(cat.name) }}
      </span>
    </div>
  </a-card>
</template>

<script setup lang="ts">
import { watch, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import * as echarts from 'echarts'
import { useTripPlanStore } from '@/stores/tripPlan'
import type { GraphCategory } from '@/types'

const props = defineProps<{
  active: boolean
}>()

const { t } = useI18n()
const tripStore = useTripPlanStore()

let kgChart: echarts.ECharts | null = null
let kgResizeHandler: (() => void) | null = null

const kgNodeSymbolCache = new Map<string, string>()
const kgLegendDotStyleCache = new Map<string, Record<string, string>>()

const CATEGORY_KEY_MAP: Record<string, string> = {
  '城市': 'city', '都市': 'city', 'city': 'city',
  '日程': 'schedule', '行程': 'schedule', 'schedule': 'schedule',
  '景点': 'attraction', '観光地': 'attraction', 'attraction': 'attraction',
  '酒店': 'hotel', 'ホテル': 'hotel', 'hotel': 'hotel',
  '餐饮': 'meal', '食事': 'meal', 'meal': 'meal',
  '天气': 'weather', '天気': 'weather', 'weather': 'weather',
  '预算': 'budget', '予算': 'budget', 'budget': 'budget',
  '偏好/建议': 'suggestion', '好み/提案': 'suggestion', 'preference/suggestion': 'suggestion',
}

const CATEGORY_COLORS: Record<string, string> = {
  city: '#4A90D9', schedule: '#5B8FF9', attraction: '#5AD8A6',
  hotel: '#F6BD16', meal: '#E8684A', weather: '#6DC8EC',
  budget: '#FF9845', suggestion: '#B37FEB',
}

const normalizeCategoryKey = (name: string): string => {
  const key = name.toLowerCase()
  return CATEGORY_KEY_MAP[name] || CATEGORY_KEY_MAP[key] || name
}

const getCategoryColor = (name: string): string => {
  const key = normalizeCategoryKey(name)
  return CATEGORY_COLORS[key] || '#999'
}

const getCategoryLabel = (name: string): string => {
  const key = normalizeCategoryKey(name)
  if (key in CATEGORY_COLORS) {
    return t(`result.graph.categories.${key}`)
  }
  return name
}

type KgNodeVisualPreset = {
  size: number
  gradientStart: string
  gradientEnd: string | null
}

const KG_NODE_CATEGORY_COLORS: Record<string, { start: string; end: string | null }> = {
  city: { start: '#0B3D91', end: '#5EEAD4' },
  schedule: { start: '#0000FF', end: '#E06BE0' },
  attraction: { start: '#0F7A32', end: '#C8FF6A' },
  hotel: { start: '#f59e0b', end: '#fde68a' },
  meal: { start: '#B91C1C', end: '#FDBA74' },
  weather: { start: '#0369A1', end: '#BFDBFE' },
  budget: { start: '#ea580c', end: '#fdba74' },
  suggestion: { start: '#9333ea', end: '#f0abfc' },
}

const getKgCategoryPalette = (categoryName: string): { start: string; end: string | null } => {
  const categoryKey = normalizeCategoryKey(categoryName || '')
  return KG_NODE_CATEGORY_COLORS[categoryKey] || { start: getCategoryColor(categoryName), end: null }
}

const KG_NODE_SIZE_SCALE = 1.25

const getKgNodeVisualPreset = (rawSize: number, categoryName: string): KgNodeVisualPreset => {
  const baseSize = rawSize >= 70 ? 100 : rawSize >= 45 ? 80 : 60
  const size = Math.round(baseSize * KG_NODE_SIZE_SCALE)
  const palette = getKgCategoryPalette(categoryName)
  return { size, gradientStart: palette.start, gradientEnd: palette.end }
}

const buildFeatherCircleSvgDataUrl = (size: number, start: string, end: string | null): string => {
  const center = size / 2
  const radius = Math.round(size * 0.34)
  const gradientDef = end
    ? `<linearGradient id="kgNodeGradient" x1="0%" y1="0%" x2="0%" y2="100%">
         <stop offset="0%" stop-color="${start}" />
         <stop offset="100%" stop-color="${end}" />
       </linearGradient>`
    : ''
  const fillColor = end ? 'url(#kgNodeGradient)' : start
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
    <defs>
      ${gradientDef}
      <filter id="kgNodeBlur" x="-30%" y="-30%" width="160%" height="160%">
        <feGaussianBlur stdDeviation="4" />
      </filter>
    </defs>
    <circle cx="${center}" cy="${center}" r="${radius}" fill="${fillColor}" filter="url(#kgNodeBlur)" />
  </svg>`
  return `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`
}

const getKgNodeSymbol = (visual: KgNodeVisualPreset): string => {
  const cacheKey = `${visual.size}-${visual.gradientStart}-${visual.gradientEnd ?? 'solid'}`
  const cachedSymbol = kgNodeSymbolCache.get(cacheKey)
  if (cachedSymbol) return cachedSymbol
  const symbol = `image://${buildFeatherCircleSvgDataUrl(visual.size, visual.gradientStart, visual.gradientEnd)}`
  kgNodeSymbolCache.set(cacheKey, symbol)
  return symbol
}

const getKgLegendDotStyle = (categoryName: string): Record<string, string> => {
  const palette = getKgCategoryPalette(categoryName)
  const cacheKey = `${palette.start}-${palette.end ?? 'solid'}`
  const cachedStyle = kgLegendDotStyleCache.get(cacheKey)
  if (cachedStyle) return cachedStyle
  const dataUrl = buildFeatherCircleSvgDataUrl(24, palette.start, palette.end)
  const style = { backgroundImage: `url("${dataUrl}")` }
  kgLegendDotStyleCache.set(cacheKey, style)
  return style
}

const buildKgBoundaryPositionMap = (
  nodes: any[],
  edges: any[],
  categories: GraphCategory[],
  width: number,
  height: number
): Map<string, { x: number; y: number }> => {
  const nodeKey = (id: unknown): string => String(id)
  const degreeMap = new Map<string, number>()
  nodes.forEach((node) => degreeMap.set(nodeKey(node.id), 0))
  edges.forEach((edge) => {
    const sourceKey = nodeKey(edge.source)
    const targetKey = nodeKey(edge.target)
    degreeMap.set(sourceKey, (degreeMap.get(sourceKey) || 0) + 1)
    degreeMap.set(targetKey, (degreeMap.get(targetKey) || 0) + 1)
  })
  let rootNodeKey = nodes.length > 0 ? nodeKey(nodes[0].id) : ''
  let maxDegree = -1
  nodes.forEach((node) => {
    const key = nodeKey(node.id)
    const degree = degreeMap.get(key) || 0
    if (degree > maxDegree) { maxDegree = degree; rootNodeKey = key }
  })
  const groupedNodes = new Map<string, any[]>()
  nodes.forEach((node) => {
    const key = nodeKey(node.id)
    if (key === rootNodeKey) return
    const categoryName = categories?.[Number(node.category)]?.name || ''
    const categoryKey = normalizeCategoryKey(categoryName || 'misc')
    if (!groupedNodes.has(categoryKey)) groupedNodes.set(categoryKey, [])
    groupedNodes.get(categoryKey)!.push(node)
  })
  const orderedGroupKeys = Array.from(groupedNodes.keys()).sort((a, b) => {
    return (groupedNodes.get(b)?.length || 0) - (groupedNodes.get(a)?.length || 0)
  })
  const cx = width / 2
  const cy = height / 2
  const outerRadiusX = Math.max(80, width / 2 - 24)
  const outerRadiusY = Math.max(80, height / 2 - 24)
  const layerFactors = [1, 0.9, 0.8, 0.7]
  const positionMap = new Map<string, { x: number; y: number }>()
  if (rootNodeKey) positionMap.set(rootNodeKey, { x: cx, y: cy })
  orderedGroupKeys.forEach((groupKey, groupIndex) => {
    const group = groupedNodes.get(groupKey) || []
    if (group.length === 0) return
    const baseAngle = -Math.PI / 2 + (2 * Math.PI * groupIndex) / Math.max(1, orderedGroupKeys.length)
    const spread = Math.min(1.25, Math.max(0.55, group.length * 0.03))
    const layerStride = Math.max(1, Math.ceil(group.length / layerFactors.length))
    group.forEach((node, nodeIndex) => {
      const t = group.length === 1 ? 0 : nodeIndex / (group.length - 1) - 0.5
      const angle = baseAngle + t * spread
      const layerIndex = Math.min(layerFactors.length - 1, Math.floor(nodeIndex / layerStride))
      const layerFactor = layerFactors[layerIndex]
      const visualSize = Number(node.__visual?.size) || 90
      const nodeRadius = Math.round(visualSize * 0.34)
      const marginX = nodeRadius + 8
      const marginY = nodeRadius + 8
      let x = cx + Math.cos(angle) * outerRadiusX * layerFactor
      let y = cy + Math.sin(angle) * outerRadiusY * layerFactor
      x = Math.max(marginX, Math.min(width - marginX, x))
      y = Math.max(marginY, Math.min(height - marginY, y))
      positionMap.set(nodeKey(node.id), { x, y })
    })
  })
  return positionMap
}

const initKnowledgeGraph = () => {
  if (!tripStore.graphData) return
  const container = document.getElementById('kg-chart-container')
  if (!container) return
  if (kgChart) kgChart.dispose()
  kgChart = echarts.init(container, 'grey')
  const containerWidth = Math.max(container.clientWidth, 320)
  const containerHeight = Math.max(container.clientHeight, 320)
  const nodesWithVisual = tripStore.graphData.nodes.map((node) => {
    const rawSize = Number(node.symbolSize) || 40
    const categoryName = tripStore.graphData?.categories?.[Number(node.category)]?.name || ''
    const visual = getKgNodeVisualPreset(rawSize, categoryName)
    return { ...node, __visual: visual }
  })
  const boundaryPositionMap = buildKgBoundaryPositionMap(
    nodesWithVisual, tripStore.graphData.edges, tripStore.graphData.categories, containerWidth, containerHeight
  )
  const kgForceGravity = containerWidth < 500 ? 0.2 : 0.06
  const kgForceRepulsion = containerWidth < 500 ? 360 : 520
  const kgForceEdgeLength: [number, number] = containerWidth < 500 ? [60, 140] : [95, 220]

  const option: echarts.EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(12, 23, 32, 0.94)',
      borderColor: 'rgba(215, 110, 66, 0.35)',
      borderWidth: 1,
      padding: [12, 16],
      textStyle: { color: '#fff', fontSize: 13 },
      formatter: (params: any) => {
        if (params.dataType === 'node') {
          const catName = tripStore.graphData?.categories[params.data.category]?.name || ''
          const cat = getCategoryLabel(catName)
          let tip = `<b style="color:#ffe3d6;font-size:15px">${params.data.name}</b><br/>`
          tip += `<span style="color:#aaa">${t('result.graph.type')}:</span>${cat}<br/>`
          if (params.data.value) {
            tip += `<span style="color:#aaa">${t('result.graph.detail')}:</span>${params.data.value}`
          }
          return tip
        }
        if (params.dataType === 'edge') {
          return `<span style="color:#ffe3d6">${params.data.label || t('result.graph.relation')}</span>`
        }
        return ''
      }
    },
    legend: { show: false },
    animationDuration: 1500,
    animationEasingUpdate: 'quinticInOut',
    series: [
      {
        type: 'graph',
        layout: 'force',
        data: nodesWithVisual.map(node => {
          const visual = node.__visual as KgNodeVisualPreset
          const nodeSymbol = getKgNodeSymbol(visual)
          const point = boundaryPositionMap.get(String(node.id))
          const labelFontSize = visual.size >= 140 ? 10 : visual.size >= 110 ? 9 : 8
          const labelMaxChars = visual.size >= 140 ? 7 : visual.size >= 110 ? 6 : 5
          const labelWidth = Math.round(visual.size * 0.52)
          return {
            ...node,
            x: point?.x ?? containerWidth / 2,
            y: point?.y ?? containerHeight / 2,
            fixed: Boolean(point && point.x === containerWidth / 2 && point.y === containerHeight / 2),
            symbol: nodeSymbol,
            symbolSize: visual.size,
            itemStyle: {
              ...(node.itemStyle || {}),
              borderColor: 'rgba(0, 0, 0, 0)',
              borderWidth: 0,
              shadowBlur: 0,
              shadowColor: 'rgba(0, 0, 0, 0)',
            },
            label: {
              show: visual.size >= 60,
              position: 'inside' as const,
              distance: 0,
              fontSize: labelFontSize,
              width: labelWidth,
              overflow: 'truncate',
              ellipsis: '…',
              align: 'center' as const,
              verticalAlign: 'middle' as const,
              lineHeight: labelFontSize + 2,
              color: '#fff',
              fontWeight: 'bold' as const,
              formatter: (params: any) => {
                const name = String(params.data.name || '')
                return name.length > labelMaxChars ? name.slice(0, labelMaxChars) + '…' : name
              },
            },
          }
        }),
        links: tripStore.graphData.edges.map(edge => ({
          ...edge,
          lineStyle: {
            color: 'rgba(255, 255, 255, 0.15)',
            width: 1.5,
            curveness: 0.1,
          },
          label: {
            show: true,
            formatter: edge.label || '',
            fontSize: 10,
            color: 'rgba(255, 255, 255, 0.45)',
          },
        })),
        categories: tripStore.graphData.categories,
        roam: true,
        draggable: true,
        force: {
          initLayout: 'none',
          repulsion: kgForceRepulsion,
          gravity: kgForceGravity,
          edgeLength: kgForceEdgeLength,
          friction: 0.2,
          layoutAnimation: true,
        },
        emphasis: {
          focus: 'adjacency',
          lineStyle: { width: 4, color: '#d76e42' },
          itemStyle: { borderColor: '#d76e42', borderWidth: 3 },
        },
        edgeSymbol: ['none', 'arrow'],
        edgeSymbolSize: [0, 8],
      },
    ],
  }
  kgChart.setOption(option)

  if (kgResizeHandler) window.removeEventListener('resize', kgResizeHandler)
  kgResizeHandler = () => {
    if (!tripStore.graphData) return
    initKnowledgeGraph()
  }
  window.addEventListener('resize', kgResizeHandler)
}

const ensureGraphReady = async () => {
  if (!tripStore.graphData) return
  if (!kgChart) {
    initKnowledgeGraph()
    return
  }
  kgChart.resize()
}

watch(() => props.active, async (active) => {
  if (active) await ensureGraphReady()
})

onMounted(async () => {
  if (props.active) await ensureGraphReady()
})

onUnmounted(() => {
  if (kgResizeHandler) {
    window.removeEventListener('resize', kgResizeHandler)
    kgResizeHandler = null
  }
  if (kgChart) {
    kgChart.dispose()
    kgChart = null
  }
})
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

.kg-card {
  margin-top: 20px;
}

.kg-card :deep(.ant-card-body) {
  padding: 0 0 16px 0;
}

.kg-legend {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 16px;
  padding: 12px 20px 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  background: rgba(6, 8, 14, 0.86);
  border-radius: 0 0 16px 16px;
}

.kg-legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

.kg-legend-dot {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: inline-block;
  background-position: center;
  background-size: contain;
  background-repeat: no-repeat;
}
</style>
