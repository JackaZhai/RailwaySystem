# RailwaySystem

成渝地区铁路客运智能分析与可视化系统的项目文档如下：

- [可行性分析](docs/FeasibilityAnalysis.md)
- [需求规格说明](docs/RequirementsSpecification.md)
- [架构设计](docs/ArchitectureDesign.md)
- [项目管理计划](docs/ProjectManagementPlan.md)

每份文档分别从战略可行性、需求定义、架构设计与交付治理等角度，对系统进行全面描述。

## 本地运行指南

### 后端（Django REST API）
1. 进入后端目录并创建虚拟环境：
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate
   ```
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 迁移数据库（默认使用 `db/railway.sqlite3`，可通过 `DJANGO_DB_*` 环境变量覆盖）：
   ```bash
   python manage.py migrate
   ```
4. 启动开发服务（默认监听 8000 端口）：
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

### 前端（Vite + React）
1. 进入前端目录并安装依赖：
   ```bash
   cd frontend
   npm install
   ```
2. 启动前端开发服务器（默认监听 5173 端口，可通过 Vite 提示访问）：
   ```bash
   npm run dev
   ```
3. 生产构建与预览：
   ```bash
   npm run build
   npm run preview
   ```
