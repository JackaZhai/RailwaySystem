# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a full-stack railway passenger analytics and visualization system for the Chengdu-Chongqing region in China. The system provides intelligent analysis of railway passenger flow, optimization recommendations, and interactive visualization dashboards for railway operations management.

**Technology Stack:**
- **Backend**: Django 4.2+ with Django REST Framework, SQLite (default), pandas, numpy, statsmodels
- **Frontend**: React 18.2+ with TypeScript, Vite, Recharts, React Leaflet
- **Data Processing**: ARIMA forecasting, temporal/spatial analysis, station evaluation

## Development Commands

### Backend Setup
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Apply migrations
python backend/manage.py migrate

# Run development server
python backend/manage.py runserver 0.0.0.0:8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev  # Runs on http://localhost:5173 with proxy to backend
```

### Testing
```bash
# Backend tests
python backend/manage.py test

# Frontend linting
cd frontend
npm run lint
```

### Building for Production
```bash
# Frontend production build
cd frontend
npm run build
npm run preview  # Preview production build
```

### Data Loading
```bash
# Load sample data (optional)
python backend/manage.py shell -c "from backend.data_management.services import load_sample_data; load_sample_data()"
```

## Architecture Overview

### Directory Structure
```
backend/                         # Django REST API
├── analytics/                   # Passenger flow analysis, temporal trends, forecasting
├── data_management/            # Core data models (PassengerRecord), data ingestion
├── line_optimization/          # Line optimization recommendations
├── station_evaluation/         # Station metrics calculation
├── railway_backend/            # Django project settings
└── tests/                      # Backend test suite

frontend/                       # React TypeScript application
├── src/                        # React components, styles, API integration
├── vite.config.ts              # Vite configuration with proxy to backend
└── package.json                # Frontend dependencies and scripts

db/                             # Database migrations (infrastructure)
docs/                           # Project documentation (Chinese)
```

### Key API Endpoints
- `POST /api/data/records/ingest/` - Upload CSV/Excel data
- `GET /api/analytics/flow/` - Passenger flow analysis by station/line
- `GET /api/analytics/temporal/` - Temporal trends with frequency parameter
- `GET /api/analytics/spatial/` - Spatial distribution for mapping
- `GET /api/analytics/forecast/` - ARIMA forecasting (requires station and line parameters)
- `GET /api/lines/loads/` - Line load metrics
- `GET /api/lines/recommendations/` - Line optimization recommendations
- `GET /api/stations/metrics/` - Station performance metrics

### Data Model
The core model is `PassengerRecord` (in `backend/data_management/models.py`) with fields:
- `timestamp`: DateTime of record
- `station`, `line`: Location identifiers
- `direction`: Direction indicator (optional)
- `passengers_in`, `passengers_out`: Passenger counts
- `metadata`: JSON field for extensibility
- `created_at`, `updated_at`: Auto timestamps

## Environment Variables

Configure via environment variables (see `docs/configuration.md`):
- `DJANGO_SECRET_KEY`: Django secret key
- `DJANGO_DEBUG`: Enable debug mode (`true`/`false`)
- `DJANGO_ALLOWED_HOSTS`: Comma-separated hostnames
- Database configuration: `DJANGO_DB_ENGINE`, `DJANGO_DB_NAME`, `DJANGO_DB_USER`, `DJANGO_DB_PASSWORD`, `DJANGO_DB_HOST`, `DJANGO_DB_PORT`

## Backend Configuration

**Defaults in `backend/railway_backend/settings.py`:**
- Database: SQLite at `backend/db/railway.sqlite3` (can be overridden via environment variables)
- Language: `zh-hans` (Chinese)
- Time zone: `Asia/Shanghai`
- REST framework configured for JSON-only API (no HTML renderers) with DjangoFilterBackend for filtering
- Installed apps include all backend modules: `data_management`, `analytics`, `line_optimization`, `station_evaluation`

## Development Notes

- The frontend Vite dev server proxies API requests to `http://localhost:8000` by default (configured in `frontend/vite.config.ts`).
- Frontend uses Axios for HTTP requests, Recharts for charts, and React Leaflet for maps.
- Backend migrations are stored in each Django app's `migrations/` directory; infrastructure SQL scripts go in `db/migrations/`.
- Default SQLite database is created at `backend/db/railway.sqlite3` when migrations are applied.
- The system is designed for the Chengdu-Chongqing railway network but can be adapted to other regions.
- Documentation is primarily in Chinese (in `docs/`), but code comments are in English.
- Use `npm run lint` to check TypeScript/React code quality.

## Testing

### Backend Testing
```bash
# Run all Django tests
python backend/manage.py test

# Run specific test module
python backend/manage.py test backend.tests.test_data_ingestion

# Test coverage (requires coverage installed)
coverage run --source='backend' manage.py test
coverage report
```

**Test Coverage:**
- `test_data_ingestion.py`: Data ingestion service validation
- `test_analytics_views.py`: Analytics API endpoints
- `test_forecasting.py`: ARIMA forecasting utilities
- `test_line_optimization.py`: Line optimization services and views
- `test_station_evaluation.py`: Station evaluation services and views
- `test_integration.py`: Integration tests
- `test_station_metrics.py`: Station metrics calculation

### Frontend Testing
```bash
cd frontend
npm run lint  # ESLint checking
# Add frontend tests as needed
```

### Development Dependencies
Development dependencies are in `backend/requirements-dev.txt`:
- `coverage`, `pytest`, `pytest-django`: Testing framework
- `black`, `flake8`, `mypy`: Code formatting and linting

## 高德地图集成

### 配置
- API Key: 存储在 `frontend/src/config.ts` 中 (GAODE_MAP_CONFIG.API_KEY)
- 瓦片服务: 提供了三种地图类型: normal(标准街道图), satellite(卫星图), roadnet(路网图)
- 车站坐标: 预定义了成渝地区15个主要火车站的地理坐标

### 地图组件
- `GaodeTileLayer`: 高德地图瓦片图层组件，支持三种地图类型切换
- `MapControls`: 地图控制组件，提供图层切换、缩放、定位功能
- 默认中心点: 成都 (30.6595, 104.0659)
- 默认缩放级别: 12

### 功能特性
1. **图层切换**: 支持标准地图、卫星地图、路网地图三种视图
2. **车站标记**: 根据客流数据动态调整标记大小
3. **信息提示**: 鼠标悬停显示车站详细客流数据
4. **定位功能**: 支持浏览器定位到用户当前位置
5. **响应式设计**: 适配不同屏幕尺寸

### 使用说明
地图组件已集成到"空间分布"面板中，用户可以通过地图上方的控制按钮切换图层、缩放地图或定位到当前位置。车站标记的大小与总客流量成正比。

## Testing Integration

After making changes:
1. Run backend tests: `python backend/manage.py test`
2. Verify data ingestion via `POST /api/data/records/ingest/`
3. Check analytics endpoints return expected data
4. Run frontend linting: `npm run lint` in frontend directory
5. Ensure the dashboard loads correctly with sample data
6. Test map functionality: verify tile loading, layer switching, and marker interactions