import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { PassengerRecord, Station, Train, Route } from '@/types/data'

/**
 * 铁路数据状态管理
 */
export const useDataStore = defineStore('data', () => {
  // 状态
  const passengerRecords = ref<PassengerRecord[]>([])
  const stations = ref<Station[]>([])
  const trains = ref<Train[]>([])
  const routes = ref<Route[]>([])
  const isLoading = ref(false)
  const lastUpdated = ref<Date | null>(null)
  const dataSources = ref<string[]>([])
  const selectedDataSource = ref<string | null>(null)

  // 计算属性
  const totalPassengerCount = computed(() => {
    return passengerRecords.value.reduce((sum, record) => sum + record.passengerCount, 0)
  })

  const stationCount = computed(() => stations.value.length)
  const trainCount = computed(() => trains.value.length)
  const routeCount = computed(() => routes.value.length)

  const stationMap = computed(() => {
    const map = new Map<number, Station>()
    stations.value.forEach(station => {
      map.set(station.id, station)
    })
    return map
  })

  // 操作
  const loadPassengerRecords = async (data: PassengerRecord[]) => {
    passengerRecords.value = data
    lastUpdated.value = new Date()
  }

  const loadStations = async (data: Station[]) => {
    stations.value = data
  }

  const loadTrains = async (data: Train[]) => {
    trains.value = data
  }

  const loadRoutes = async (data: Route[]) => {
    routes.value = data
  }

  const addPassengerRecord = (record: PassengerRecord) => {
    passengerRecords.value.push(record)
  }

  const updatePassengerRecord = (id: number, updates: Partial<PassengerRecord>) => {
    const index = passengerRecords.value.findIndex(record => record.id === id)
    if (index !== -1) {
      passengerRecords.value[index] = { ...passengerRecords.value[index], ...updates } as PassengerRecord
    }
  }

  const deletePassengerRecord = (id: number) => {
    const index = passengerRecords.value.findIndex(record => record.id === id)
    if (index !== -1) {
      passengerRecords.value.splice(index, 1)
    }
  }

  const getStationById = (id: number) => {
    return stations.value.find(station => station.id === id)
  }

  const getStationByCode = (code: string) => {
    return stations.value.find(station => station.code === code)
  }

  const getRecordsByStation = (stationId: number) => {
    return passengerRecords.value.filter(record => record.stationId === stationId)
  }

  const getRecordsByDateRange = (start: Date, end: Date) => {
    return passengerRecords.value.filter(record => {
      const recordDate = new Date(record.timestamp)
      return recordDate >= start && recordDate <= end
    })
  }

  const clearAllData = () => {
    passengerRecords.value = []
    stations.value = []
    trains.value = []
    routes.value = []
    lastUpdated.value = null
  }

  const setDataSource = (source: string) => {
    selectedDataSource.value = source
    // 这里可以添加从指定数据源加载数据的逻辑
  }

  const addDataSource = (source: string) => {
    if (!dataSources.value.includes(source)) {
      dataSources.value.push(source)
    }
  }

  const removeDataSource = (source: string) => {
    const index = dataSources.value.indexOf(source)
    if (index !== -1) {
      dataSources.value.splice(index, 1)
    }
  }

  return {
    // 状态
    passengerRecords,
    stations,
    trains,
    routes,
    isLoading,
    lastUpdated,
    dataSources,
    selectedDataSource,

    // 计算属性
    totalPassengerCount,
    stationCount,
    trainCount,
    routeCount,
    stationMap,

    // 操作
    loadPassengerRecords,
    loadStations,
    loadTrains,
    loadRoutes,
    addPassengerRecord,
    updatePassengerRecord,
    deletePassengerRecord,
    getStationById,
    getStationByCode,
    getRecordsByStation,
    getRecordsByDateRange,
    clearAllData,
    setDataSource,
    addDataSource,
    removeDataSource,
  }
})