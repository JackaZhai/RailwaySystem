# 前端一键启动脚本

本文档介绍如何使用一键启动脚本来快速启动铁路客运分析系统的前端开发服务器。

## 可用脚本

| 脚本文件 | 描述 | 适用平台 |
|---------|------|---------|
| `start_frontend.py` | 功能完整的Python脚本，包含环境检查、依赖安装、代码检查等 | 所有平台 |
| `start_frontend_simple.py` | 简化版Python脚本，快速启动 | 所有平台 |
| `start_frontend.bat` | Windows批处理文件，双击即可运行 | Windows |
| `start_frontend.sh` | Shell脚本，适用于Unix-like系统 | Linux/macOS |

## 快速开始

### Windows用户
1. 双击 `start_frontend.bat`
2. 或打开命令提示符，运行：
   ```cmd
   start_frontend.bat
   ```

### 所有平台（使用Python）
```bash
# 使用完整功能脚本
python start_frontend.py

# 或使用简化版
python start_frontend_simple.py
```

### Linux/macOS用户
```bash
# 添加执行权限
chmod +x start_frontend.sh

# 运行脚本
./start_frontend.sh
```

## 脚本功能

### `start_frontend.py` (完整功能)
- ✅ 检查Node.js和npm版本
- ✅ 自动安装前端依赖（如果需要）
- ✅ 运行TypeScript类型检查
- ✅ 运行ESLint代码检查
- ✅ 启动Vite开发服务器
- ✅ 自动打开浏览器
- ✅ 实时显示服务器日志
- ✅ 优雅的进程管理

**命令行选项：**
```bash
python start_frontend.py --help

选项：
  --install-only    只安装依赖，不启动服务器
  --no-install      跳过依赖安装
  --port PORT       指定端口（默认：5173）
  --host HOST       指定主机（默认：localhost）
  --skip-lint       跳过代码检查
  --help            显示帮助信息
```

### `start_frontend_simple.py` (简化版)
- ✅ 基本环境检查
- ✅ 自动依赖安装
- ✅ 启动开发服务器
- ✅ 自动打开浏览器

### `start_frontend.bat` (Windows批处理)
- ✅ 检查Node.js环境
- ✅ 自动安装依赖
- ✅ 启动开发服务器
- ✅ 简单的错误处理

### `start_frontend.sh` (Shell脚本)
- ✅ 检查Node.js环境
- ✅ 自动安装依赖
- ✅ 启动开发服务器
- ✅ 适用于Unix-like系统

## 手动启动（备用方法）

如果脚本无法工作，可以手动启动：

```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖（如果需要）
npm install

# 3. 启动开发服务器
npm run dev

# 服务器将在 http://localhost:5173 启动
```

## 故障排除

### 常见问题

1. **"Node.js未安装"错误**
   - 从 [nodejs.org](https://nodejs.org/) 下载安装Node.js
   - 确保Node.js和npm已添加到PATH环境变量

2. **依赖安装失败**
   - 检查网络连接
   - 尝试清理npm缓存：`npm cache clean --force`
   - 删除 `frontend/node_modules` 和 `frontend/package-lock.json` 后重试

3. **端口被占用**
   - 使用 `--port` 参数指定其他端口：
     ```bash
     python start_frontend.py --port 3000
     ```

4. **编码问题（Windows）**
   - 使用批处理文件 `start_frontend.bat`
   - 或在命令提示符中使用chcp命令：`chcp 65001`

### 环境要求

- **Node.js**: v16.0.0 或更高版本
- **npm**: v7.0.0 或更高版本
- **Python**: 3.6+（仅Python脚本需要）
- **磁盘空间**: 至少200MB可用空间

## 开发服务器信息

- **URL**: http://localhost:5173
- **热重载**: 支持
- **API代理**: 配置为 `http://localhost:8000`
- **构建工具**: Vite

## 停止服务器

- 在终端中按 **Ctrl+C**
- 或关闭终端窗口

## 更新日志

### 2025-12-14
- 创建所有启动脚本
- 添加完整的环境检查功能
- 支持跨平台使用
- 更新项目文档