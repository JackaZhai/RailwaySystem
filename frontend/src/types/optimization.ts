export type OptimizationRangeType = 'today' | 'week' | 'month' | 'custom'
export type OptimizationLineGroup = 'all' | 'trunk' | 'branch' | 'airport'
export type OptimizationDayType = 'weekday' | 'weekend' | 'holiday'
export type OptimizationPlanStatus = 'draft' | 'running' | 'ready' | 'failed'

export interface OptimizationTimeRange {
  type: OptimizationRangeType
  startDate?: string
  endDate?: string
}

export interface OptimizationFilters {
  timeRange: OptimizationTimeRange
  lineGroup: OptimizationLineGroup
  dayType: OptimizationDayType
}

export interface OptimizationSnapshot {
  efficiencyScore: number
  loadMatch: number
  peakAbsorb: number
  capacityElastic: number
  overloadedRatio: number
  focusLine: string
}

export interface OptimizationKpis {
  averageOccupancy: number
  maxSectionLoad: number
  overloadedCount: number
  idleCount: number
}

export interface OptimizationLineLoad {
  id: number
  name: string
  code: string
  occupancy: number
  sectionLoad: number
  trend: number
  peakSegment: string
}

export interface OptimizationOdAlert {
  segment: string
  load: number
  duration: string
  suggestion: string
}

export interface OptimizationOdMatrixPair {
  from: string
  to: string
  total: number
  days: number
}

export interface OptimizationOdMatrix {
  pairs: OptimizationOdMatrixPair[]
}

export interface OptimizationDensityCell {
  name: string
  density: number
}

export interface OptimizationDensityRow {
  line: string
  trains: OptimizationDensityCell[]
}

export interface OptimizationDensityMatrix {
  trains: string[]
  matrix: OptimizationDensityRow[]
}

export interface OptimizationTimetableWindow {
  time: string
  load: number
  suggestion: string
}

export interface OptimizationHub {
  name: string
  role: string
  degree: number
  betweenness: number
  closeness: number
  trend: number
}

export interface OptimizationRecommendation {
  priority: 'P0' | 'P1' | 'P2'
  priorityClass: 'priority-high' | 'priority-medium' | 'priority-low'
  type: string
  title: string
  detail: string
  impact: string
  line: string
}

export interface OptimizationScenario {
  id: string
  name: string
  status: OptimizationPlanStatus
  updatedAt: string
  owner: string
  tags: string[]
}

export interface OptimizationPlanSummary {
  id: string
  title: string
  status: OptimizationPlanStatus
  createdAt: string
  expectedImpact: string
}

export interface OptimizationInsight {
  title: string
  detail: string
  tag: string
  impact: string
}

export interface OptimizationOverview {
  updatedAt: string
  snapshot: OptimizationSnapshot
  kpis: OptimizationKpis
  lines: OptimizationLineLoad[]
  odAlerts: OptimizationOdAlert[]
  odMatrix: OptimizationOdMatrix
  density: OptimizationDensityMatrix
  timetable: OptimizationTimetableWindow[]
  hubs: OptimizationHub[]
  recommendations: OptimizationRecommendation[]
  scenarios: OptimizationScenario[]
  insights: OptimizationInsight[]
  lastPlan?: OptimizationPlanSummary
}

export interface OptimizationPlanRequest {
  filters: OptimizationFilters
  goal: string
  constraints: string[]
  notes?: string
}

export interface OptimizationPlanResult {
  planId: string
  status: OptimizationPlanStatus
  summary: OptimizationPlanSummary
  recommendations: OptimizationRecommendation[]
}
