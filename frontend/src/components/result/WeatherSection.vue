<template>
  <a-card
    v-if="tripStore.tripPlan?.weather_info && tripStore.tripPlan.weather_info.length > 0"
    id="weather"
    :bordered="false"
    class="section-shellless weather-section-card"
  >
    <div v-if="selectedWeather" class="weather-dashboard">
      <section class="weather-side" :style="weatherSideStyle">
        <div class="weather-gradient"></div>

        <div class="date-container">
          <h2 class="date-dayname">{{ formatWeatherWeekday(selectedWeather.date) }}</h2>
          <span class="date-day">{{ formatWeatherDate(selectedWeather.date) }}</span>
          <span class="location">
            <span class="location-icon">
              <svg width="16px" height="16px" viewBox="-3 0 20 20" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
                  <g id="Page-1" stroke="none" stroke-width="1" fill="none" fill-rule="evenodd">
                      <g id="Dribbble-Light-Preview" transform="translate(-223.000000, -5439.000000)" fill="currentColor">
                          <g id="icons" transform="translate(56.000000, 160.000000)">
                              <path d="M176,5286.219 C176,5287.324 175.105,5288.219 174,5288.219 C172.895,5288.219 172,5287.324 172,5286.219 C172,5285.114 172.895,5284.219 174,5284.219 C175.105,5284.219 176,5285.114 176,5286.219 M174,5296 C174,5296 169,5289 169,5286 C169,5283.243 171.243,5281 174,5281 C176.757,5281 179,5283.243 179,5286 C179,5289 174,5296 174,5296 M174,5279 C170.134,5279 167,5282.134 167,5286 C167,5289.866 174,5299 174,5299 C174,5299 181,5289.866 181,5286 C181,5282.134 177.866,5279 174,5279" id="pin_sharp_circle-[#624]"></path>
                          </g>
                      </g>
                  </g>
              </svg>
            </span>
            {{ tripStore.tripPlan!.city }}
          </span>
        </div>

        <div class="weather-container">
          <div class="weather-hero-icon weather-icon" :class="selectedWeatherIconKind">
            <template v-if="selectedWeatherIconKind === 'sun-shower'">
              <div class="cloud"></div>
              <div class="sun"><div class="rays"></div></div>
              <div class="rain"></div>
            </template>
            <template v-else-if="selectedWeatherIconKind === 'thunder-storm'">
              <div class="cloud"></div>
              <div class="lightning">
                <div class="bolt"></div>
                <div class="bolt"></div>
              </div>
            </template>
            <template v-else-if="selectedWeatherIconKind === 'cloudy'">
              <div class="cloud"></div>
              <div class="cloud"></div>
            </template>
            <template v-else-if="selectedWeatherIconKind === 'flurries'">
              <div class="cloud"></div>
              <div class="snow">
                <div class="flake"></div>
                <div class="flake"></div>
              </div>
            </template>
            <template v-else-if="selectedWeatherIconKind === 'rainy'">
              <div class="cloud"></div>
              <div class="rain"></div>
            </template>
            <template v-else>
              <div class="sun"><div class="rays"></div></div>
            </template>
          </div>
          <h1 class="weather-temp">{{ formatWeatherTemp(selectedWeather.day_temp) }}</h1>
          <h3 class="weather-desc">{{ selectedWeather.day_weather }}</h3>
        </div>
      </section>

      <section class="weather-info-side">
        <div class="week-container week-container--top">
          <ul class="week-list">
            <li
              v-for="(weatherItem, weatherIndex) in weatherDisplayList"
              :key="`${weatherItem.date}-${weatherIndex}`"
              :class="{ active: weatherIndex === activeWeatherIndex }"
              @mouseenter="selectWeatherDay(weatherIndex)"
              @click="selectWeatherDay(weatherIndex)"
            >
              <div class="day-icon weather-icon weather-icon--small" :class="weatherItem._iconKind">
                <template v-if="weatherItem._iconKind === 'sun-shower'">
                  <div class="cloud"></div>
                  <div class="sun"><div class="rays"></div></div>
                  <div class="rain"></div>
                </template>
                <template v-else-if="weatherItem._iconKind === 'thunder-storm'">
                  <div class="cloud"></div>
                  <div class="lightning">
                    <div class="bolt"></div>
                    <div class="bolt"></div>
                  </div>
                </template>
                <template v-else-if="weatherItem._iconKind === 'cloudy'">
                  <div class="cloud"></div>
                  <div class="cloud"></div>
                </template>
                <template v-else-if="weatherItem._iconKind === 'flurries'">
                  <div class="cloud"></div>
                  <div class="snow">
                    <div class="flake"></div>
                    <div class="flake"></div>
                  </div>
                </template>
                <template v-else-if="weatherItem._iconKind === 'rainy'">
                  <div class="cloud"></div>
                  <div class="rain"></div>
                </template>
                <template v-else>
                  <div class="sun"><div class="rays"></div></div>
                </template>
              </div>
              <span class="day-name">{{ formatWeatherWeekday(weatherItem.date, true) }}</span>
              <span class="day-temp">{{ formatWeatherTemp(weatherItem.day_temp) }}</span>
            </li>
          </ul>
        </div>

        <div class="today-info-container">
          <div class="today-info">
            <div class="today-info-item">
              <span class="wea-title">{{ t('result.weatherDay') }}</span>
              <span class="value">{{ selectedWeather.day_weather }} · {{ formatWeatherTemp(selectedWeather.day_temp) }}</span>
            </div>
            <div class="today-info-item">
              <span class="wea-title">{{ t('result.weatherNight') }}</span>
              <span class="value">{{ selectedWeather.night_weather }} · {{ formatWeatherTemp(selectedWeather.night_temp) }}</span>
            </div>
            <div class="today-info-item">
              <span class="wea-title">{{ t('result.weatherPrecipitation') }}</span>
              <span class="value">{{ getWeatherPrecipitation(selectedWeather.day_weather) }}</span>
            </div>
            <div class="today-info-item">
              <span class="wea-title">{{ t('result.weatherHumidity') }}</span>
              <span class="value">{{ getWeatherHumidity(selectedWeather.day_weather) }}</span>
            </div>
            <div class="today-info-item">
              <span class="wea-title">{{ t('result.weatherWind') }}</span>
              <span class="value">{{ getWeatherWind(selectedWeather) }}</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  </a-card>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useTripPlanStore } from '@/stores/tripPlan'
import type { WeatherInfo } from '@/types'

const { t, locale } = useI18n()
const tripStore = useTripPlanStore()

const activeWeatherIndex = ref(0)

const localeTag = computed(() => {
  const currentLocale = String(locale.value || 'en').toLowerCase()
  if (currentLocale.startsWith('zh')) return 'zh-CN'
  if (currentLocale.startsWith('ja')) return 'ja-JP'
  return 'en-US'
})

const weatherList = computed<WeatherInfo[]>(() => tripStore.tripPlan?.weather_info ?? [])

const selectedWeather = computed<WeatherInfo | null>(() => {
  const list = weatherList.value
  if (list.length === 0) return null
  const safeIndex = Math.min(Math.max(activeWeatherIndex.value, 0), list.length - 1)
  return list[safeIndex]
})

const parseWeatherDate = (rawDate: string): Date | null => {
  if (!rawDate) return null
  const normalized = rawDate
    .replace(/年/g, '-').replace(/月/g, '-').replace(/日/g, '')
    .replace(/[./]/g, '-').trim()
  const parsedDate = new Date(normalized)
  if (!Number.isNaN(parsedDate.getTime())) return parsedDate
  const matched = rawDate.match(/(\d{4})\D+(\d{1,2})\D+(\d{1,2})/)
  if (!matched) return null
  const [, year, month, day] = matched
  const fallbackDate = new Date(Number(year), Number(month) - 1, Number(day))
  return Number.isNaN(fallbackDate.getTime()) ? null : fallbackDate
}

const formatWeatherDate = (rawDate: string): string => {
  const date = parseWeatherDate(rawDate)
  if (!date) return rawDate || '--'
  return new Intl.DateTimeFormat(localeTag.value, { month: 'short', day: 'numeric', year: 'numeric' }).format(date)
}

const formatWeatherWeekday = (rawDate: string, short = false): string => {
  const date = parseWeatherDate(rawDate)
  if (!date) return rawDate || '--'
  return new Intl.DateTimeFormat(localeTag.value, { weekday: short ? 'short' : 'long' }).format(date)
}

const formatWeatherTemp = (temperature: number | null | undefined): string => {
  if (!Number.isFinite(Number(temperature))) return '--'
  return `${Math.round(Number(temperature))}°C`
}

type WeatherIconKind = 'sun-shower' | 'thunder-storm' | 'cloudy' | 'flurries' | 'sunny' | 'rainy'

const getWeatherIconKind = (weatherText: string): WeatherIconKind => {
  const text = (weatherText || '').trim()
  const hasRain = /(雨|rain|shower|drizzle|sprinkle|阵雨|小雨|中雨|大雨|暴雨)/i.test(text)
  const hasSun = /(晴|sun|clear)/i.test(text)
  if (/(雷|thunder|storm|lightning|雷暴|雷阵雨)/i.test(text)) return 'thunder-storm'
  if (/(雪|snow|sleet|hail|冰雹|冻雨|雨夹雪)/i.test(text)) return 'flurries'
  if (hasRain && hasSun) return 'sun-shower'
  if (hasRain) return 'rainy'
  if (/(云|阴|cloud|overcast|雾|霾|fog|mist|haze|wind|breeze|gale)/i.test(text)) return 'cloudy'
  return 'sunny'
}

const selectedWeatherIconKind = computed<WeatherIconKind>(() => {
  if (!selectedWeather.value) return 'sunny'
  return getWeatherIconKind(`${selectedWeather.value.day_weather || ''} ${selectedWeather.value.night_weather || ''}`)
})

type WeatherDisplayItem = WeatherInfo & { _iconKind: WeatherIconKind }

const weatherDisplayList = computed<WeatherDisplayItem[]>(() => {
  return weatherList.value.map((item) => ({
    ...item,
    _iconKind: getWeatherIconKind(`${item.day_weather || ''} ${item.night_weather || ''}`),
  }))
})

const getWeatherGradient = (weatherText: string): string => {
  const text = (weatherText || '').toLowerCase()
  if (/(雷|thunder)/.test(text)) return 'linear-gradient(140deg, #3a4a86 0%, #5b3b8a 100%)'
  if (/(雪|snow|sleet|hail)/.test(text)) return 'linear-gradient(140deg, #8bc6ec 0%, #d9afd9 100%)'
  if (/(雨|rain|shower|drizzle)/.test(text)) return 'linear-gradient(140deg, #4b6cb7 0%, #182848 100%)'
  if (/(雾|霾|fog|mist|haze)/.test(text)) return 'linear-gradient(140deg, #7b8799 0%, #4a5568 100%)'
  if (/(阴|cloud|overcast)/.test(text)) return 'linear-gradient(140deg, #6d7f92 0%, #3f4c6b 100%)'
  return 'linear-gradient(140deg, #72edf2 0%, #5151e5 100%)'
}

const getWeatherPrecipitation = (weatherText: string): string => {
  const text = (weatherText || '').toLowerCase()
  if (/(雷|thunder|暴雨|storm)/.test(text)) return '85%'
  if (/(雨|rain|shower|drizzle)/.test(text)) return '65%'
  if (/(雪|snow|sleet|hail)/.test(text)) return '55%'
  if (/(阴|cloud|overcast)/.test(text)) return '30%'
  return '10%'
}

const getWeatherHumidity = (weatherText: string): string => {
  const text = (weatherText || '').toLowerCase()
  if (/(雷|thunder|暴雨|storm)/.test(text)) return '88%'
  if (/(雨|rain|shower|drizzle)/.test(text)) return '78%'
  if (/(雪|snow|sleet|hail)/.test(text)) return '72%'
  if (/(阴|cloud|overcast|雾|霾|fog|mist|haze)/.test(text)) return '62%'
  return '42%'
}

const getWeatherWind = (weather: WeatherInfo | null): string => {
  if (!weather) return '--'
  const direction = weather.wind_direction?.trim() || '--'
  const power = weather.wind_power?.trim() || '--'
  return `${direction} ${power}`.trim()
}

const selectWeatherDay = (index: number) => {
  if (index < 0 || index >= weatherList.value.length) return
  activeWeatherIndex.value = index
}

const weatherSideStyle = computed<Record<string, string>>(() => ({
  '--weather-gradient': getWeatherGradient(selectedWeather.value?.day_weather || ''),
}))

watch(
  weatherList,
  (list) => {
    if (list.length === 0) { activeWeatherIndex.value = 0; return }
    if (activeWeatherIndex.value > list.length - 1) activeWeatherIndex.value = 0
  },
  { immediate: true }
)
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

.weather-section-card {
  overflow: hidden;
}

.weather-dashboard {
  display: flex;
  height: 350px;
  overflow: hidden;
  background: none;
}

.weather-side {
  position: relative;
  flex: 0 0 300px;
  overflow: hidden;
  box-shadow: 0 0 20px -8px rgba(0, 0, 0, 0.36);
  transition: transform 300ms ease;
  transform: translateZ(0) scale(1.02) perspective(1200px);
}

.weather-side:hover {
  transform: scale(1.06) perspective(1400px) rotateY(6deg);
}

.weather-gradient {
  position: absolute;
  inset: 0;
  background-image: url("https://images.unsplash.com/photo-1559963110-71b394e7494d?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=675&q=80");
  opacity: 0.84;
}

.date-container {
  position: absolute;
  top: 38px;
  left: 38px;
  right: 28px;
  z-index: 2;
}

.date-dayname {
  margin: 0;
  font-size: 26px;
  line-height: 1.12;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.96);
}

.date-day {
  display: block;
  margin-top: 4px;
  font-size: 13px;
  letter-spacing: 0.03em;
  color: rgba(240, 247, 255, 0.84);
}

.location {
  display: inline-flex;
  align-items: center;
  margin-top: 8px;
  font-size: 16px;
  font-weight: bold;
  color: rgba(242, 248, 255, 0.9);
}

.location-icon {
  margin-right: 6px;
}

.weather-container {
  position: absolute;
  left: 28px;
  right: 28px;
  bottom: 28px;
  z-index: 2;
}

.weather-hero-icon {
  display: inline-block;
  color: #f7fbff;
  font-size: 0.78em;
  line-height: 1;
  margin-bottom: -22px;
  margin-left: -20px;
  filter: drop-shadow(0 8px 14px rgba(0, 0, 0, 0.18));
}

.weather-icon {
  position: relative;
  display: inline-block;
  width: 12em;
  height: 10em;
  animation: weather-float 5.5s ease-in-out infinite;
}

.weather-icon .cloud {
  position: absolute;
  z-index: 1;
  top: 50%;
  left: 50%;
  width: 3.6875em;
  height: 3.6875em;
  margin: -1.84375em;
  background: currentColor;
  border-radius: 50%;
  box-shadow:
    -2.1875em 0.6875em 0 -0.6875em,
    2.0625em 0.9375em 0 -0.9375em,
    0 0 0 0.375em #fff,
    -2.1875em 0.6875em 0 -0.3125em #fff,
    2.0625em 0.9375em 0 -0.5625em #fff;
}

.weather-icon .cloud:after {
  content: '';
  position: absolute;
  bottom: 0;
  left: -0.5em;
  display: block;
  width: 4.5625em;
  height: 1em;
  background: currentColor;
  box-shadow: 0 0.4375em 0 -0.0625em #fff;
}

.weather-icon .cloud:nth-child(2) {
  z-index: 0;
  background: #fff;
  box-shadow:
    -2.1875em 0.6875em 0 -0.6875em #fff,
    2.0625em 0.9375em 0 -0.9375em #fff,
    0 0 0 0.375em #fff,
    -2.1875em 0.6875em 0 -0.3125em #fff,
    2.0625em 0.9375em 0 -0.5625em #fff;
  opacity: 0.3;
  transform: scale(0.5) translate(6em, -3em);
  animation: weather-cloud 4s linear infinite;
}

.weather-icon .cloud:nth-child(2):after {
  background: #fff;
}

.weather-icon .sun {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 2.5em;
  height: 2.5em;
  margin: -1.25em;
  background: currentColor;
  border-radius: 50%;
  box-shadow: 0 0 0 0.375em #fff;
  animation: weather-spin 12s infinite linear;
}

.weather-icon .rays {
  position: absolute;
  top: -2em;
  left: 50%;
  display: block;
  width: 0.375em;
  height: 1.125em;
  margin-left: -0.1875em;
  background: #fff;
  border-radius: 0.25em;
  box-shadow: 0 5.375em #fff;
}

.weather-icon .rays:before,
.weather-icon .rays:after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  display: block;
  width: 0.375em;
  height: 1.125em;
  transform: rotate(60deg);
  transform-origin: 50% 3.25em;
  background: #fff;
  border-radius: 0.25em;
  box-shadow: 0 5.375em #fff;
}

.weather-icon .rays:before {
  transform: rotate(120deg);
}

.weather-icon .cloud + .sun {
  margin: -2em 1em;
}

.weather-icon .rain,
.weather-icon .lightning,
.weather-icon .snow {
  position: absolute;
  z-index: 2;
  top: 50%;
  left: 50%;
  width: 3.75em;
  height: 3.75em;
  margin: 0.375em 0 0 -2em;
  background: transparent;
}

.weather-icon .rain:after {
  content: '';
  position: absolute;
  z-index: 2;
  top: 50%;
  left: 50%;
  width: 1.125em;
  height: 1.125em;
  margin: -1em 0 0 -0.25em;
  background: #0cf;
  border-radius: 100% 0 60% 50% / 60% 0 100% 50%;
  box-shadow:
    0.625em 0.875em 0 -0.125em rgba(255, 255, 255, 0.2),
    -0.875em 1.125em 0 -0.125em rgba(255, 255, 255, 0.2),
    -1.375em -0.125em 0 rgba(255, 255, 255, 0.2);
  transform: rotate(-28deg);
  animation: weather-rain 3s linear infinite;
}

.weather-icon .bolt {
  position: absolute;
  top: 50%;
  left: 50%;
  margin: -0.25em 0 0 -0.125em;
  color: #fff;
  opacity: 0.3;
  animation: weather-lightning 2s linear infinite;
}

.weather-icon .bolt:nth-child(2) {
  width: 0.5em;
  height: 0.25em;
  margin: -1.75em 0 0 -1.875em;
  transform: translate(2.5em, 2.25em);
  opacity: 0.2;
  animation: weather-lightning 1.5s linear infinite;
}

.weather-icon .bolt:before,
.weather-icon .bolt:after {
  content: '';
  position: absolute;
  z-index: 2;
  top: 50%;
  left: 50%;
  margin: -1.625em 0 0 -1.0125em;
  border-top: 1.25em solid transparent;
  border-right: 0.75em solid;
  border-bottom: 0.75em solid;
  border-left: 0.5em solid transparent;
  transform: skewX(-10deg);
}

.weather-icon .bolt:after {
  margin: -0.25em 0 0 -0.25em;
  border-top: 0.75em solid;
  border-right: 0.5em solid transparent;
  border-bottom: 1.25em solid transparent;
  border-left: 0.75em solid;
  transform: skewX(-10deg);
}

.weather-icon .bolt:nth-child(2):before {
  margin: -0.75em 0 0 -0.5em;
  border-top: 0.625em solid transparent;
  border-right: 0.375em solid;
  border-bottom: 0.375em solid;
  border-left: 0.25em solid transparent;
}

.weather-icon .bolt:nth-child(2):after {
  margin: -0.125em 0 0 -0.125em;
  border-top: 0.375em solid;
  border-right: 0.25em solid transparent;
  border-bottom: 0.625em solid transparent;
  border-left: 0.375em solid;
}

.weather-icon .flake:before,
.weather-icon .flake:after {
  content: '\2744';
  position: absolute;
  top: 50%;
  left: 50%;
  margin: -1.025em 0 0 -1.0125em;
  color: #fff;
  line-height: 1em;
  opacity: 0.2;
  animation: weather-spin 8s linear infinite reverse;
}

.weather-icon .flake:after {
  margin: 0.125em 0 0 -1em;
  font-size: 1.5em;
  opacity: 0.4;
  animation: weather-spin 14s linear infinite;
}

.weather-icon .flake:nth-child(2):before {
  margin: -0.5em 0 0 0.25em;
  font-size: 1.25em;
  opacity: 0.2;
  animation: weather-spin 10s linear infinite;
}

.weather-icon .flake:nth-child(2):after {
  margin: 0.375em 0 0 0.125em;
  font-size: 2em;
  opacity: 0.4;
  animation: weather-spin 16s linear infinite reverse;
}

.weather-temp {
  margin: 8px 0 0;
  font-size: 56px;
  line-height: 0.95;
  font-weight: 800;
  color: #fff;
  letter-spacing: -0.02em;
}

.weather-desc {
  margin: 8px 0 0;
  font-size: 20px;
  color: rgba(245, 249, 255, 0.94);
  font-weight: 600;
}

.weather-info-side {
  flex: 1;
  min-width: 0;
  padding: 16px 30px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.today-info {
  padding: 10px 12px;
}

.today-info-item {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 8px;
  font-size: 12px;
  line-height: 1.3;
}

.today-info-item + .today-info-item {
  margin-top: 6px;
  padding-top: 6px;
}

.today-info-item .wea-title {
  color: rgba(235, 243, 252, 0.809);
  letter-spacing: 0.04em;
  text-transform: uppercase;
  font-size: 17px;
  font-weight: 600;
  padding: 3px 0;
}

.today-info-item .value {
  color: rgba(255, 255, 255, 0.9);
  text-align: right;
  font-size: 16px;
}

.week-container {
  margin-top: 0;
  padding-top: 0;
}

.week-container--top {
  margin-bottom: 2px;
}

.week-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.week-list > li {
  width: 86px;
  padding: 8px 8px;
  border-radius: 12px;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease, color 0.2s ease;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.03);
  color: rgba(238, 245, 253, 0.78);
}

.week-list > li:hover {
  transform: translateY(-3px);
  background: rgba(255, 255, 255, 0.12);
  color: rgba(5, 12, 20, 0.9);
  box-shadow: 0 10px 28px rgba(9, 15, 22, 0.32);
}

.week-list > li.active {
  background: rgba(255, 255, 255, 0.9);
  color: rgba(9, 14, 24, 0.92);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.22);
}

.week-list > li .day-icon {
  display: block;
  margin: 0 auto;
}

.week-list > li .day-icon.weather-icon--small {
  width: 12em;
  height: 10em;
  font-size: 0.3em;
  color: inherit;
  animation-duration: 6.2s;
}

.week-list > li .day-name {
  display: block;
  margin-top: 6px;
  text-align: center;
  font-size: 12px;
  letter-spacing: 0.03em;
}

.week-list > li .day-temp {
  display: block;
  text-align: center;
  margin-top: 3px;
  font-weight: 700;
  font-size: 12px;
}

@keyframes weather-spin {
  100% { transform: rotate(360deg); }
}

@keyframes weather-float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-2px); }
}

@keyframes weather-cloud {
  0% { opacity: 0; }
  50% { opacity: 0.3; }
  100% { opacity: 0; transform: scale(0.5) translate(-200%, -3em); }
}

@keyframes weather-rain {
  0% {
    background: #0cf;
    box-shadow:
      0.625em 0.875em 0 -0.125em rgba(255, 255, 255, 0.2),
      -0.875em 1.125em 0 -0.125em rgba(255, 255, 255, 0.2),
      -1.375em -0.125em 0 #0cf;
  }
  25% {
    box-shadow:
      0.625em 0.875em 0 -0.125em rgba(255, 255, 255, 0.2),
      -0.875em 1.125em 0 -0.125em #0cf,
      -1.375em -0.125em 0 rgba(255, 255, 255, 0.2);
  }
  50% {
    background: rgba(255, 255, 255, 0.3);
    box-shadow:
      0.625em 0.875em 0 -0.125em #0cf,
      -0.875em 1.125em 0 -0.125em rgba(255, 255, 255, 0.2),
      -1.375em -0.125em 0 rgba(255, 255, 255, 0.2);
  }
  100% {
    box-shadow:
      0.625em 0.875em 0 -0.125em rgba(255, 255, 255, 0.2),
      -0.875em 1.125em 0 -0.125em rgba(255, 255, 255, 0.2),
      -1.375em -0.125em 0 #0cf;
  }
}

@keyframes weather-lightning {
  45% { color: #fff; background: #fff; opacity: 0.2; }
  50% { color: #0cf; background: #0cf; opacity: 1; }
  55% { color: #fff; background: #fff; opacity: 0.2; }
}

@media (max-width: 768px) {
  .weather-dashboard {
    flex-direction: column;
    min-height: auto;
    border-radius: 16px;
  }

  .weather-side {
    flex: 0 0 auto;
    width: 100%;
    min-height: 260px;
    border-radius: 16px 16px 0 0;
    transform: none !important;
  }

  .weather-info-side {
    padding: 12px;
  }

  .weather-temp {
    font-size: 46px;
  }

  .weather-desc {
    font-size: 18px;
  }

  .week-list {
    justify-content: space-between;
  }

  .week-list > li {
    width: calc(33.333% - 7px);
    min-width: 88px;
    padding: 8px 6px;
  }
}
</style>
