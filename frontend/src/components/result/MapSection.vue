<template>
  <div class="right-map">
    <a-card id="map" :bordered="false" class="map-card section-shellless">
      <div id="map-canvas" style="width: 100%; height: 100%"></div>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { watch, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { message } from 'ant-design-vue'
import AMapLoader from '@amap/amap-jsapi-loader'
import { Loader as GoogleMapsLoader } from '@googlemaps/js-api-loader'
import { useTripPlanStore } from '@/stores/tripPlan'

const props = defineProps<{
  active: boolean
}>()

const { t } = useI18n()
const tripStore = useTripPlanStore()

let map: any = null

const escapeHtml = (value: unknown): string => {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

const buildMarkerContent = (dayNo: number, stopNo: number): string => {
  return `
    <div class="tripstar-map-marker">
      <span class="tripstar-map-marker__core" aria-hidden="true">
        <svg fill="#ffffff" width="30px" height="30px" viewBox="0 0 256 256" id="Flat" xmlns="http://www.w3.org/2000/svg">
          <path d="M231.4248,109.2041,169.36426,86.63574,146.7959,24.57422a19.99984,19.99984,0,0,0-37.5918.001L86.63574,86.63574,24.57422,109.2041a19.99984,19.99984,0,0,0,.001,37.5918l62.06054,22.56836,22.56836,62.06152a19.99984,19.99984,0,0,0,37.5918-.001l22.56836-62.06054,62.06152-22.56836a19.99984,19.99984,0,0,0-.001-37.5918Zm-72.01562,38.24219a19.95591,19.95591,0,0,0-11.96289,11.96289l.001-.001L128,212.88672l-19.44629-53.47754A19.95279,19.95279,0,0,0,96.5918,147.44727L43.11328,128l53.47754-19.44629A19.95279,19.95279,0,0,0,108.55273,96.5918L128,43.11328l19.44629,53.47754a19.95279,19.95279,0,0,0,11.96191,11.96191L212.88672,128Z"/>
        </svg>
      </span>
      <span class="tripstar-map-marker__index" aria-hidden="true">${dayNo}-${stopNo}</span>
    </div>
  `
}

const buildInfoWindowContent = (attraction: any): string => {
  const name = escapeHtml(attraction.name || t('common.noData'))
  const address = escapeHtml(attraction.address || t('common.noData'))
  const visitDuration = Number.isFinite(attraction.visit_duration) ? attraction.visit_duration : '—'
  const dayAttractionText = escapeHtml(
    t('result.mapInfo.dayAttraction', { day: attraction.dayIndex + 1, index: attraction.attrIndex + 1 })
  )
  const minuteUnit = escapeHtml(t('result.minuteUnit'))
  return `
    <div class="tripstar-map-tooltip tripstar-map-tooltip--plain">
      <p class="tripstar-map-tooltip__line tripstar-map-tooltip__line--title">${name}</p>
      <p class="tripstar-map-tooltip__line">${dayAttractionText}</p>
      <p class="tripstar-map-tooltip__line">${address}</p>
      <p class="tripstar-map-tooltip__line">${visitDuration}${minuteUnit}</p>
    </div>
  `
}

type RouteMode = 'driving' | 'walking' | 'straight'
type RoutePoint = [number, number]

const ROUTE_STYLE_PRESETS: Record<RouteMode, any> = {
  driving: {
    strokeColor: '#37b4ff',
    strokeWeight: 3.5,
    strokeOpacity: 0.92,
    strokeStyle: 'solid',
    lineJoin: 'round',
    lineCap: 'round',
    outlineColor: 'rgba(4, 19, 32, 0.7)',
    borderWeight: 1,
  },
  walking: {
    strokeColor: '#6ad38f',
    strokeWeight: 3,
    strokeOpacity: 0.9,
    strokeStyle: 'dashed',
    strokeDasharray: [12, 8],
    lineJoin: 'round',
    lineCap: 'round',
    outlineColor: 'rgba(8, 32, 20, 0.5)',
    borderWeight: 0.8,
  },
  straight: {
    strokeColor: '#ffffff',
    strokeWeight: 1.5,
    strokeOpacity: 0.62,
    strokeStyle: 'solid',
    strokeDasharray: [10, 10],
    lineJoin: 'round',
    lineCap: 'round',
    outlineColor: 'rgba(33, 17, 8, 0.45)',
    borderWeight: 0.8,
  },
}

const detectRouteMode = (transportation: string): RouteMode => {
  const normalized = (transportation || '').toLowerCase()
  if (/(步行|徒步|散步|walk|walking)/i.test(normalized)) return 'walking'
  if (/(驾车|开车|自驾|打车|出租车|car|drive|driving|taxi)/i.test(normalized)) return 'driving'
  return 'driving'
}

const toRoutePoint = (raw: any): RoutePoint | null => {
  if (!raw) return null
  if (Array.isArray(raw) && raw.length >= 2) {
    const lng = Number(raw[0])
    const lat = Number(raw[1])
    return Number.isFinite(lng) && Number.isFinite(lat) ? [lng, lat] : null
  }
  if (typeof raw.getLng === 'function' && typeof raw.getLat === 'function') {
    const lng = Number(raw.getLng())
    const lat = Number(raw.getLat())
    return Number.isFinite(lng) && Number.isFinite(lat) ? [lng, lat] : null
  }
  if ('lng' in raw && 'lat' in raw) {
    const lng = Number(raw.lng)
    const lat = Number(raw.lat)
    return Number.isFinite(lng) && Number.isFinite(lat) ? [lng, lat] : null
  }
  if ('longitude' in raw && 'latitude' in raw) {
    const lng = Number(raw.longitude)
    const lat = Number(raw.latitude)
    return Number.isFinite(lng) && Number.isFinite(lat) ? [lng, lat] : null
  }
  return null
}

const parsePolylineString = (polyline: string): RoutePoint[] => {
  if (!polyline) return []
  return polyline
    .split(';')
    .map((pair) => pair.split(','))
    .map((parts) => {
      const lng = Number(parts[0])
      const lat = Number(parts[1])
      return Number.isFinite(lng) && Number.isFinite(lat) ? ([lng, lat] as RoutePoint) : null
    })
    .filter((point): point is RoutePoint => Boolean(point))
}

const dedupeRoutePath = (points: RoutePoint[]): RoutePoint[] => {
  if (points.length <= 1) return points
  return points.filter((point, index, array) => {
    if (index === 0) return true
    const prev = array[index - 1]
    return point[0] !== prev[0] || point[1] !== prev[1]
  })
}

const extractRoutePath = (result: any): RoutePoint[] => {
  const route = result?.routes?.[0] || result?.route?.paths?.[0] || result?.route?.routes?.[0] || null
  if (!route) return []
  const steps = route.steps || []
  const points: RoutePoint[] = []
  steps.forEach((step: any) => {
    if (Array.isArray(step?.path)) {
      step.path.forEach((node: any) => {
        const point = toRoutePoint(node)
        if (point) points.push(point)
      })
      return
    }
    if (typeof step?.polyline === 'string') {
      points.push(...parsePolylineString(step.polyline))
    }
  })
  if (points.length > 1) return dedupeRoutePath(points)
  if (typeof route?.polyline === 'string') {
    const fromRoute = dedupeRoutePath(parsePolylineString(route.polyline))
    if (fromRoute.length > 1) return fromRoute
  }
  return []
}

const searchRoutePath = (
  AMap: any,
  mode: Exclude<RouteMode, 'straight'>,
  start: RoutePoint,
  end: RoutePoint
): Promise<RoutePoint[] | null> => {
  return new Promise((resolve) => {
    const ServiceCtor = mode === 'walking' ? AMap.Walking : AMap.Driving
    if (!ServiceCtor) { resolve(null); return }
    const service = mode === 'driving'
      ? new ServiceCtor({ policy: AMap.DrivingPolicy?.LEAST_TIME ?? 0 })
      : new ServiceCtor({})
    service.search(start, end, (status: string, result: any) => {
      if (status !== 'complete') { resolve(null); return }
      const path = extractRoutePath(result)
      resolve(path.length > 1 ? path : null)
    })
  })
}

const initMap = async () => {
  const provider = import.meta.env.VITE_MAP_PROVIDER || 'amap'
  if (provider === 'google') {
    await initGoogleMap()
  } else {
    await initAMap()
  }
}

const initAMap = async () => {
  try {
    const AMap = await AMapLoader.load({
      key: import.meta.env.VITE_AMAP_WEB_JS_KEY,
      version: '2.0',
      plugins: ['AMap.Marker', 'AMap.Polyline', 'AMap.InfoWindow', 'AMap.Driving', 'AMap.Walking']
    })
    map = new AMap.Map('map-canvas', {
      zoom: 12,
      center: [116.397128, 39.916527],
      viewMode: '3D',
      mapStyle: 'amap://styles/darkblue'
    })
    await addAttractionMarkersAMap(AMap)
    message.success(t('result.messages.mapLoaded'))
  } catch (error) {
    console.error('高德地图加载失败:', error)
    message.error(t('result.messages.mapLoadFailed'))
  }
}

const initGoogleMap = async () => {
  try {
    const loader = new GoogleMapsLoader({
      apiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY,
      version: 'weekly',
      libraries: ['places']
    })
    const { Map } = await loader.importLibrary('maps') as google.maps.MapsLibrary
    const mapOptions: google.maps.MapOptions = {
      center: { lat: 39.916527, lng: 116.397128 },
      zoom: 12,
      mapId: 'DEMO_MAP_ID',
      styles: [
        { elementType: "geometry", stylers: [{ color: "#242f3e" }] },
        { elementType: "labels.text.stroke", stylers: [{ color: "#242f3e" }] },
        { elementType: "labels.text.fill", stylers: [{ color: "#746855" }] },
      ]
    }
    const mapElement = document.getElementById('map-canvas')
    if (mapElement) {
      map = new Map(mapElement, mapOptions)
      await addAttractionMarkersGoogle()
      message.success(t('result.messages.mapLoaded'))
    }
  } catch (error) {
    console.error('Google Maps 加载失败:', error)
    message.error(t('result.messages.mapLoadFailed'))
  }
}

const addAttractionMarkersAMap = async (AMap: any) => {
  if (!tripStore.tripPlan) return
  const markers: any[] = []
  const allAttractions: any[] = []
  let globalIndex = 0
  tripStore.tripPlan.days.forEach((day, dayIndex) => {
    day.attractions.forEach((attraction, attrIndex) => {
      globalIndex++
      if (attraction.location?.longitude && attraction.location?.latitude) {
        allAttractions.push({ ...attraction, dayIndex, attrIndex, globalIndex })
      }
    })
  })
  allAttractions.forEach((attraction, index) => {
    const marker = new AMap.Marker({
      position: [attraction.location.longitude, attraction.location.latitude],
      content: buildMarkerContent(attraction.dayIndex + 1, attraction.attrIndex + 1),
      anchor: 'center',
      zIndex: 120 + index,
    })
    const infoWindow = new AMap.InfoWindow({
      isCustom: true,
      content: buildInfoWindowContent(attraction),
      offset: new AMap.Pixel(0, -18),
      closeWhenClickMap: true,
    })
    marker.on('mouseover', () => infoWindow.open(map, marker.getPosition()))
    marker.on('mouseout', () => infoWindow.close())
    marker.on('click', () => infoWindow.open(map, marker.getPosition()))
    markers.push(marker)
  })
  map.add(markers)
  const routePolylines = await drawRoutesAMap(AMap, allAttractions)
  if (allAttractions.length > 0) {
    map.setFitView([...markers, ...routePolylines])
  }
}

const addAttractionMarkersGoogle = async () => {
  if (!tripStore.tripPlan) return
  const { AdvancedMarkerElement } = await google.maps.importLibrary("marker") as google.maps.MarkerLibrary
  const bounds = new google.maps.LatLngBounds()
  const allAttractions: any[] = []
  tripStore.tripPlan.days.forEach((day, dayIndex) => {
    day.attractions.forEach((attraction, attrIndex) => {
      if (attraction.location?.longitude && attraction.location?.latitude) {
        allAttractions.push({ ...attraction, dayIndex, attrIndex })
      }
    })
  })
  allAttractions.forEach((attraction) => {
    const position = { lat: attraction.location.latitude, lng: attraction.location.longitude }
    const markerElement = document.createElement('div')
    markerElement.innerHTML = buildMarkerContent(attraction.dayIndex + 1, attraction.attrIndex + 1)
    const marker = new AdvancedMarkerElement({
      map,
      position,
      content: markerElement,
      title: attraction.name,
    })
    const infoWindow = new google.maps.InfoWindow({
      content: buildInfoWindowContent(attraction),
    })
    marker.addListener('click', () => infoWindow.open(map, marker))
    bounds.extend(position)
  })
  map.fitBounds(bounds)
  await drawRoutesGoogle(allAttractions)
}

const drawRoutesAMap = async (AMap: any, attractions: any[]): Promise<any[]> => {
  if (attractions.length < 2 || !tripStore.tripPlan) return []
  const dayGroups: Record<number, any[]> = {}
  attractions.forEach(attr => {
    if (!dayGroups[attr.dayIndex]) dayGroups[attr.dayIndex] = []
    dayGroups[attr.dayIndex].push(attr)
  })
  const polylines: any[] = []
  for (const dayAttractions of Object.values(dayGroups)) {
    if (dayAttractions.length < 2) continue
    dayAttractions.sort((a: any, b: any) => a.attrIndex - b.attrIndex)
    const dayIndex = dayAttractions[0].dayIndex
    const transportation = tripStore.tripPlan.days?.[dayIndex]?.transportation || ''
    const preferredMode = detectRouteMode(transportation)
    for (let i = 0; i < dayAttractions.length - 1; i++) {
      const start = dayAttractions[i]
      const end = dayAttractions[i + 1]
      const startPoint: RoutePoint = [start.location.longitude, start.location.latitude]
      const endPoint: RoutePoint = [end.location.longitude, end.location.latitude]
      const plannedPath =
        preferredMode === 'straight'
          ? null
          : await searchRoutePath(AMap, preferredMode as Exclude<RouteMode, 'straight'>, startPoint, endPoint)
      const usePlannedRoute = Array.isArray(plannedPath) && plannedPath.length > 1
      const routeModeForStyle: RouteMode = usePlannedRoute ? preferredMode : 'straight'
      const path = usePlannedRoute ? plannedPath : [startPoint, endPoint]
      const style = ROUTE_STYLE_PRESETS[routeModeForStyle]
      const polyline = new AMap.Polyline({ path, ...style, showDir: true, zIndex: 90 })
      polylines.push(polyline)
    }
  }
  if (polylines.length > 0) map.add(polylines)
  return polylines
}

const drawRoutesGoogle = async (attractions: any[]) => {
  if (attractions.length < 2 || !tripStore.tripPlan) return
  const directionsService = new google.maps.DirectionsService()
  const dayGroups: Record<number, any[]> = {}
  attractions.forEach(attr => {
    if (!dayGroups[attr.dayIndex]) dayGroups[attr.dayIndex] = []
    dayGroups[attr.dayIndex].push(attr)
  })
  for (const dayAttractions of Object.values(dayGroups)) {
    if (dayAttractions.length < 2) continue
    dayAttractions.sort((a: any, b: any) => a.attrIndex - b.attrIndex)
    const dayIndex = dayAttractions[0].dayIndex
    const transportation = tripStore.tripPlan.days?.[dayIndex]?.transportation || ''
    const preferredMode = detectRouteMode(transportation)
    const travelMode = preferredMode === 'walking' ? google.maps.TravelMode.WALKING : google.maps.TravelMode.DRIVING
    for (let i = 0; i < dayAttractions.length - 1; i++) {
      const start = dayAttractions[i]
      const end = dayAttractions[i + 1]
      const request: google.maps.DirectionsRequest = {
        origin: { lat: start.location.latitude, lng: start.location.longitude },
        destination: { lat: end.location.latitude, lng: end.location.longitude },
        travelMode: travelMode
      }
      directionsService.route(request, (result, status) => {
        if (status === google.maps.DirectionsStatus.OK && result) {
          new google.maps.DirectionsRenderer({
            map: map,
            directions: result,
            suppressMarkers: true,
            polylineOptions: {
              strokeColor: ROUTE_STYLE_PRESETS[preferredMode].strokeColor,
              strokeWeight: 4
            }
          })
        }
      })
    }
  }
}

const ensureMapReady = async () => {
  if (!map) {
    await initMap()
    return
  }
  if (typeof map.resize === 'function') {
    map.resize()
  }
}

watch(() => props.active, async (active) => {
  if (active && tripStore.tripPlan) {
    await ensureMapReady()
  }
})

onMounted(async () => {
  if (props.active && tripStore.tripPlan) {
    await ensureMapReady()
  }
})
</script>

<style scoped>
.right-map {
  flex: 1;
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

.map-card {
  height: 100%;
  min-height: 500px;
  overflow: hidden;
}

.map-card :deep(.ant-card-body) {
  height: 100%;
  padding: 0;
}
</style>
