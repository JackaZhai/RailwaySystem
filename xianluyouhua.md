下面给你 **1) 低保真原型（按你现有界面风格）** 和 **2) 接口字段设计（可直接给后端/前端对齐）**。我会尽量做到“你拿去就能开工”。

---

## 1) 低保真原型（线路优化页）

> 假设你右侧内容区宽 1200~1400px，整体保持你当前的“标题 + 副标题 + 内容卡片”风格。

### 1.1 页面整体线框（单页工作台）

```
┌────────────────────────────────────────────────────────────┐
│ 线路优化  （线路负载分析和优化建议）                         │
│ [时间范围] [工作日/周末] [线路多选] [方向] [阈值] [粒度]  [导出] │
├────────────────────────────────────────────────────────────┤
│ KPI卡片区                                                    │
│ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐         │
│ │过载线路│ │闲置线路│ │最挤断面│ │高峰时段│ │建议总数│         │
│ └───────┘ └───────┘ └───────┘ └───────┘ └───────┘         │
├────────────────────────────────────────────────────────────┤
│ Tabs： [线路负载] [断面分析] [车次分析] [枢纽识别]            │
│ ┌────────────────────────────────────────────────────────┐ │
│ │ 左：主图表(70%)                         右：详情(30%)   │ │
│ │ ┌──────────────────────────────┐  ┌─────────────────┐ │ │
│ │ │ 线路负载：线路×时间 热力图     │  │ 选中对象概览     │ │ │
│ │ │ 或：趋势折线（avg/p95）        │  │ - 指标卡         │ │ │
│ │ └──────────────────────────────┘  │ - Top断面/Top车次 │ │ │
│ │                                    │ - 一键生成建议    │ │ │
│ │                                    └─────────────────┘ │ │
│ └────────────────────────────────────────────────────────┘ │
├────────────────────────────────────────────────────────────┤
│ 优化建议区（列表 + 抽屉详情）                                 │
│ ┌────────────────────────────────────────────────────────┐ │
│ │ [类型筛选] [影响排序] [置信度] [状态] [批量导出]          │ │
│ │ ┌────────────────────────────────────────────────────┐ │ │
│ │ │ 建议表格：线路/区间/时段/原因/动作/预计效果/状态      │ │ │
│ │ └────────────────────────────────────────────────────┘ │ │
│ └────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

---

### 1.2 各 Tab 的低保真内容（你按这个拆组件就行）

#### A) 线路负载 Tab（宏观发现问题）

**主图（左）**：线路×时间热力图 或 “趋势折线图”

* 热力图：行=线路(或线路+方向)，列=小时/15min，色=满载率/上座率
* 点击一个格子 → 右侧详情刷新 + 下钻到断面 Tab

**右侧详情（右）**：

* 选中线路/时段的：avgLoad、p95Load、超载分钟数
* TOP 3 断面（最拥挤区间）
* 按钮：**“生成建议”**（跳到建议抽屉，预填线路+时段）

#### B) 断面分析 Tab（定位哪个区间出问题）

**主图（左）**：站序“断面走廊热力条”

* 横轴=站序区间（A-B、B-C…），颜色=断面满载率
* hover：显示客流、满载率、峰值时间、Top OD
* click：锁定区间 → 右侧显示“该区间 Top 车次” + 可生成建议

**右侧（右）**：

* 区间概览（B-C）：P95满载率、持续天数、峰值发生时段
* Top OD 列表
* “查看车次分析”按钮（切到车次 Tab 并带参）

#### C) 车次分析 Tab（为时刻表优化服务）

**主图（左）**：车次×区间热力表 + 发车时刻 vs 载客散点

* 车次热力：行=车次，列=区间，色=载客/上座率
* 散点：横=发车时刻，纵=上座率（识别“某些时刻过挤/过空”）

**右侧（右）**：

* 选中车次：最挤区间、最挤时段
* 按钮：**“建议高峰加密/平峰稀疏”**（生成建议）

#### D) 枢纽识别 Tab（网络分析）

**主图（左）**：网络图（可简化为 TopN 节点图）

* 节点大小=介数中心性，颜色可选=客流量
* 点击节点 → 右侧站点详情

**右侧（右）**：

* 站点中心性（度/介数/接近）
* 连接线路、换乘强度
* 风险提示：高介数 + 周边断面高负载 = 系统性瓶颈

---

### 1.3 建议抽屉（统一承载“可解释建议”）

从任意 Tab 触发“生成建议”，打开抽屉：

```
[建议详情 Drawer]
- 标题：1号线 上行 B-C 7:30-8:30 长期过载
- 触发规则：连续10个工作日 P95>1.0
- 证据：小图（热力图截取 + 断面走廊截取 + 车次热力截取）
- 建议动作：
  - 增开：+2 班（间隔 10min -> 7min）
  - 或 调整：将 7:10 班次后移至 7:20
- 影响评估：
  - 峰值满载率 1.15 -> 0.96（模拟）
  - 超载分钟数减少 38%
- 操作：采纳/驳回/导出
```

---

## 2) 接口字段设计（前后端对齐版）

### 2.0 统一约定（强烈建议）

**过滤条件 Filters（所有接口通用）**

```json
{
  "timeRange": ["2025-12-01", "2025-12-07"],
  "dayType": "workday",          // workday/weekend/all
  "granularity": "hour",         // 15min/hour/day
  "lineIds": ["L1", "L2"],
  "direction": "up",             // up/down/all
  "threshold": {
    "overload": 1.0,
    "idle": 0.35
  }
}
```

**返回统一包装（便于前端处理）**

```json
{ "code": 0, "msg": "ok", "data": { } }
```

---

### 2.1 线路优化页初始化（线路列表、站点序列）

**GET** `/api/lines`

```json
[
  { "id": "L1", "name": "1号线", "directions": ["up","down"] }
]
```

**GET** `/api/lines/{lineId}/stations?direction=up`

```json
{
  "lineId": "L1",
  "direction": "up",
  "stations": [
    { "id": "S1", "name": "站A", "seq": 1 },
    { "id": "S2", "name": "站B", "seq": 2 }
  ]
}
```

---

### 2.2 KPI 卡片

**POST** `/api/route-opt/kpi`
**Body**：Filters

**Response**

```json
{
  "overloadLineCount": 5,
  "idleLineCount": 3,
  "topSection": {
    "lineId": "L1",
    "direction": "up",
    "fromStationId": "S2",
    "toStationId": "S3",
    "p95FullRate": 1.15
  },
  "peakHours": [
    { "hour": 8, "value": 1.08 },
    { "hour": 18, "value": 1.03 }
  ],
  "suggestionCount": {
    "addTrips": 8,
    "timetable": 6,
    "hub": 2
  }
}
```

---

### 2.3 线路负载 Tab

#### A) 线路×时间热力图

**POST** `/api/route-opt/line-load/heatmap`
**Body**：Filters

**Response（按点返回，适合热力图）**

```json
{
  "xAxis": ["06:00","07:00","08:00"],
  "yAxis": [
    { "lineId": "L1", "name": "1号线(上行)" },
    { "lineId": "L2", "name": "2号线(上行)" }
  ],
  "points": [
    { "x": 0, "y": 0, "avgLoad": 0.82, "p95Load": 1.05, "overMinutes": 12 },
    { "x": 1, "y": 0, "avgLoad": 0.93, "p95Load": 1.12, "overMinutes": 25 }
  ]
}
```

#### B) 线路趋势折线（可选）

**POST** `/api/route-opt/line-load/trend`

```json
{
  "series": [
    {
      "lineId": "L1",
      "direction": "up",
      "points": [
        { "t": "2025-12-01 08:00", "avgLoad": 0.9, "p95Load": 1.1 }
      ]
    }
  ]
}
```

---

### 2.4 断面分析 Tab（核心）

**POST** `/api/route-opt/section-load/corridor`
**Body**（Filters + 单线路更合理）

```json
{
  "timeRange": ["2025-12-01","2025-12-07"],
  "dayType": "workday",
  "granularity": "hour",
  "lineId": "L1",
  "direction": "up"
}
```

**Response（按站序区间返回）**

```json
{
  "lineId": "L1",
  "direction": "up",
  "segments": [
    {
      "fromStationId": "S1",
      "toStationId": "S2",
      "avgFullRate": 0.78,
      "p95FullRate": 0.96,
      "peakHour": 8,
      "flow": 5200,
      "topOD": [
        { "oStationId": "S1", "dStationId": "S5", "flow": 800 }
      ]
    },
    {
      "fromStationId": "S2",
      "toStationId": "S3",
      "avgFullRate": 0.95,
      "p95FullRate": 1.15,
      "peakHour": 8,
      "flow": 8300,
      "topOD": [
        { "oStationId": "S2", "dStationId": "S6", "flow": 1200 }
      ]
    }
  ]
}
```

> 这里 `flow` 是该断面的客流量（断面满载率用 `p95FullRate` 就够你做热力色阶）。

---

### 2.5 车次分析 Tab

#### A) 车次×区间热力表

**POST** `/api/route-opt/trip-load/heatmap`
**Body**

```json
{
  "timeRange": ["2025-12-01","2025-12-07"],
  "dayType": "workday",
  "lineId": "L1",
  "direction": "up",
  "focusSegment": { "fromStationId": "S2", "toStationId": "S3" }  // 可选
}
```

**Response**

```json
{
  "trips": [
    { "tripId": "T1001", "departTime": "07:20" },
    { "tripId": "T1003", "departTime": "07:30" }
  ],
  "segments": [
    { "fromStationId": "S1", "toStationId": "S2" },
    { "fromStationId": "S2", "toStationId": "S3" }
  ],
  "cells": [
    { "tripId": "T1001", "segIndex": 0, "load": 0.72, "flow": 380 },
    { "tripId": "T1001", "segIndex": 1, "load": 1.08, "flow": 560 }
  ]
}
```

#### B) 发车时刻 vs 客流（用于频次优化）

**POST** `/api/route-opt/timetable/demand-scatter`

```json
{
  "lineId": "L1",
  "direction": "up",
  "timeRange": ["2025-12-01","2025-12-07"],
  "dayType": "workday"
}
```

**Response**

```json
{
  "points": [
    { "departTime": "07:10", "avgLoad": 0.65, "p95Load": 0.82, "sampleTrips": 35 },
    { "departTime": "07:30", "avgLoad": 0.92, "p95Load": 1.12, "sampleTrips": 35 }
  ]
}
```

---

### 2.6 优化建议（列表 + 详情）

#### A) 建议列表

**POST** `/api/route-opt/suggestions/list`
**Body**

```json
{
  "filters": { ... },
  "types": ["addTrips","timetable","hub"],
  "sortBy": "impact",
  "page": 1,
  "pageSize": 20
}
```

**Response**

```json
{
  "total": 42,
  "items": [
    {
      "id": "SG001",
      "type": "addTrips",
      "title": "1号线(上行) B-C 7:30-8:30 增开2班",
      "lineId": "L1",
      "direction": "up",
      "timeWindow": "07:30-08:30",
      "segment": { "fromStationId": "S2", "toStationId": "S3" },
      "reason": "连续10工作日 P95满载率>1.0",
      "confidence": "high",
      "impact": { "p95Before": 1.15, "p95After": 0.96, "overMinutesDropPct": 0.38 },
      "cost": { "extraTrips": 2, "opCostIndex": 1.2 },
      "status": "pending"
    }
  ]
}
```

#### B) 建议详情（抽屉）

**GET** `/api/route-opt/suggestions/{id}`

```json
{
  "id": "SG001",
  "evidence": {
    "lineHeatmapRef": { "lineId": "L1", "peakHours": [8] },
    "corridorTopSegments": [
      { "fromStationId": "S2", "toStationId": "S3", "p95FullRate": 1.15 }
    ],
    "topTrips": [
      { "tripId": "T1003", "departTime": "07:30", "p95Load": 1.2 }
    ]
  },
  "action": {
    "addTrips": { "count": 2, "headwayFromMin": 10, "headwayToMin": 7 },
    "timetableAdjust": []
  },
  "simulationAssumption": {
    "splitRule": "even", 
    "note": "新增班次均分分担"
  }
}
```

> `evidence` 里放你要展示的“证据数据”，抽屉里就能直接画小图/列表，不用再请求一堆接口（当然也可以按需懒加载）。

---

### 2.7 枢纽识别（网络分析）

**POST** `/api/route-opt/hubs/metrics`

```json
{
  "timeRange": ["2025-12-01","2025-12-07"],
  "dayType": "workday",
  "topN": 30
}
```

**Response**

```json
{
  "nodes": [
    {
      "stationId": "S10",
      "name": "枢纽站X",
      "degree": 6,
      "betweenness": 0.23,
      "closeness": 0.41,
      "inOutFlow": 120000,
      "transferFlow": 45000
    }
  ],
  "edges": [
    { "fromStationId": "S10", "toStationId": "S11", "weight": 0.8 }
  ]
}
```

---

## 你现在可以直接开工的“前端落地建议”

* **filters 统一放在 RouteOptimization.vue**（pinia 或组件 state 都行）
* 子图表组件都只收 `:filters="filters"`，内部 watch 触发请求
* “点击热力图 → 切 Tab + 带上 focusSegment/lineId/hour”
  建议用一个 `pageState`：

  ```js
  { activeTab, focusLineId, focusSegment, focusHour }
  ```

---

如果你愿意，我下一步可以把 **“低保真线框图”** 画得更像真实页面（按 Element Plus 的 card / grid 样式），并把上面接口再补一份 **字段口径说明**（比如 avgLoad、fullRate、p95 的计算口径与单位），这样你给后端就更不容易扯皮。
