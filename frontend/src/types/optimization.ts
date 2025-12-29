export type DayType = 'workday' | 'weekend' | 'all'
export type Direction = 'up' | 'down' | 'all'
export type Granularity = '15min' | 'hour' | 'day'

export interface RouteOptFilters {
  timeRange: [string, string]
  dayType: DayType
  granularity: Granularity
  lineIds: string[]
  direction: Direction
  threshold: {
    overload: number
    idle: number
  }
}

export interface RouteLine {
  id: string
  name: string
  directions: string[]
  dateRange?: {
    minDate: string | null
    maxDate: string | null
  }
}

export interface LineStation {
  id: string
  name: string
  seq: number
}

export interface RouteKpi {
  overloadLineCount: number
  idleLineCount: number
  topSection: {
    lineId: string
    direction: string
    fromStationId: string
    toStationId: string
    p95FullRate: number
  } | null
  peakHours: Array<{ hour: number; value: number }>
  suggestionCount: {
    addTrips: number
    timetable: number
    hub: number
  }
}

export interface LineLoadHeatmap {
  xAxis: string[]
  yAxis: Array<{ lineId: string; name: string }>
  points: Array<{ x: number; y: number; avgLoad: number; p95Load: number; overMinutes: number }>
}

export interface LineLoadTrend {
  series: Array<{
    lineId: string
    direction: string
    points: Array<{ t: string; avgLoad: number; p95Load: number }>
  }>
}

export interface SectionCorridor {
  lineId: string
  direction: string
  segments: Array<{
    fromStationId: string
    toStationId: string
    avgFullRate: number
    p95FullRate: number
    peakHour: number
    flow: number
    topOD: Array<{ oStationId: string; dStationId: string; flow: number }>
  }>
}

export interface TripHeatmap {
  trips: Array<{ tripId: string; departTime: string; lineId?: string; trainId?: string }>
  segments: Array<{ fromStationId: string; toStationId: string }>
  cells: Array<{ tripId: string; segIndex: number; load: number; flow: number }>
}

export interface TimetableScatter {
  points: Array<{ departTime: string; avgLoad: number; p95Load: number; sampleTrips: number }>
}

export interface SuggestionList {
  total: number
  items: Array<{
    id: string
    type: 'addTrips' | 'timetable' | 'hub'
    title: string
    lineId: string
    direction: string
    timeWindow: string
    segment: { fromStationId: string; toStationId: string } | null
    reason: string
    confidence: string
    impact: { p95Before: number; p95After: number; overMinutesDropPct: number }
    cost: { extraTrips: number; opCostIndex: number }
    status: string
  }>
}

export interface SuggestionDetail {
  id: string
  evidence: {
    lineHeatmapRef: { lineId: string; peakHours: number[] }
    corridorTopSegments: Array<{ fromStationId: string; toStationId: string; p95FullRate: number }> | null
    topTrips: Array<{ tripId: string; departTime: string; p95Load: number }>
  }
  action: {
    addTrips: { count: number; headwayFromMin: number; headwayToMin: number } | null
    timetableAdjust: Array<any>
  }
  simulationAssumption: {
    splitRule: string
    note: string
  }
}

export interface HubMetrics {
  nodes: Array<{
    stationId: string
    name: string
    degree: number
    betweenness: number
    closeness: number
    inOutFlow: number
    transferFlow: number
  }>
  edges: Array<{ fromStationId: string; toStationId: string; weight: number }>
}
