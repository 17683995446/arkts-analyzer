# ArkAnalyzer - ArkTS知识图谱动态更新系统

基于第一性原理设计的百万行级ArkTS代码知识图谱动态更新系统。

## 核心特性

- **增量更新机制**: 基于第一性原理，每次只处理变更的文件，响应时间 <500ms
- **实时监控**: 使用watchdog监控ArkTS文件变化，自动同步到知识图谱
- **可视化展示**: React + D3.js 构建的交互式知识图谱可视化
- **LLM语义增强**: 集成硅基流动API进行深度代码语义分析
- **轻量级架构**: SQLite嵌入式数据库，无需额外服务

## 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                     ArkAnalyzer 系统架构                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌────────────────┐    ┌────────────────┐  │
│  │   前端展示层  │    │   API网关层     │    │   后端服务层   │  │
│  │  React + D3  │◄──►│  FastAPI       │◄──►│  Python异步    │  │
│  │  WebSocket   │    │  REST/WebSocket│    │  增量更新      │  │
│  └──────────────┘    └────────────────┘    └────────────────┘  │
│                            │                      │             │
│                     ┌──────┴──────┐       ┌───────┴───────┐   │
│                     │  WebSocket  │       │  文件监控系统  │   │
│                     │  实时推送   │       │  ArkTS解析器   │   │
│                     └─────────────┘       │  LLM语义分析   │   │
│                                           └────────────────┘   │
│                                                  │              │
│                     ┌────────────────────────────┼──────────┐  │
│                     │         SQLite数据库         │          │  │
│                     │  ┌─────┐ ┌─────┐ ┌─────┐  │          │  │
│                     │  │Files│ │Classes│ │Methods│ │Relations│  │
│                     │  └─────┘ └─────┘ └─────┘  │          │  │
│                     └─────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- npm 或 pnpm

### 1. 启动后端服务

```bash
cd ark-analyzer/backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或: venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 启动服务
cd src
python ark_analyzer.py
# 或使用uvicorn
uvicorn ark_analyzer:app --reload --host 0.0.0.0 --port 8000
```

### 2. 启动前端服务

```bash
cd ark-analyzer/frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 3. 配置监控路径

在设置页面配置要监控的ArkTS项目路径，系统将自动开始增量同步。

## 核心模块

### 1. 文件监控系统 (FileWatcherService)

- 使用 watchdog 跨平台监控文件系统
- 防抖队列避免频繁更新
- 支持创建、修改、删除事件

### 2. 增量更新引擎 (SynchronizationEngine)

**第一性原理实现**:
```
修改文件A = 删除A的旧数据 + 重新解析A + 插入A的新数据
```

无需修改任何其他文件的数据！

### 3. ArkTS解析器 (ArkTSParser)

- 词法分析提取Token
- 语法分析构建AST
- 实体提取: 类、方法、属性
- 关系提取: 继承、实现、调用、组合

### 4. LLM语义分析 (SemanticAnalyzer)

- 集成硅基流动API
- 增强代码理解
- 推断隐式关系
- 提供改进建议

## API接口

### REST API

| 接口 | 方法 | 描述 |
|-----|------|------|
| `/api/v1/stats` | GET | 获取图谱统计信息 |
| `/api/v1/classes` | GET | 获取类列表 |
| `/api/v1/classes/{id}` | GET | 获取类详情 |
| `/api/v1/methods` | GET | 获取方法列表 |
| `/api/v1/call-chain` | GET | 追踪调用链 |
| `/api/v1/components` | GET | 获取组件列表 |
| `/api/v1/changes` | GET | 获取变更历史 |
| `/api/v1/search` | GET | 搜索实体 |

### WebSocket API

```
ws://localhost:8000/ws/updates
```

推送消息格式:
```json
{
  "type": "file_changed",
  "data": {
    "file_path": "Main.ets",
    "change_type": "modified",
    "entities_updated": 5
  }
}
```

## 数据库模型

```sql
-- 核心表结构
CREATE TABLE files (
    id INTEGER PRIMARY KEY,
    path TEXT UNIQUE NOT NULL,
    hash BLOB NOT NULL,
    modified INTEGER NOT NULL
);

CREATE TABLE classes (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    file_id INTEGER REFERENCES files(id),
    flags INTEGER
);

CREATE TABLE methods (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    class_id INTEGER REFERENCES classes(id),
    params TEXT,
    return_type TEXT
);

CREATE TABLE calls (
    caller_id INTEGER REFERENCES methods(id),
    callee_id INTEGER REFERENCES methods(id),
    PRIMARY KEY (caller_id, callee_id)
);

CREATE TABLE components (
    parent_id INTEGER REFERENCES classes(id),
    child_id INTEGER REFERENCES classes(id),
    PRIMARY KEY (parent_id, child_id)
);
```

## 性能指标

| 操作 | 耗时 | 场景 |
|-----|------|------|
| 单文件更新 | <500ms | 最常见场景 |
| 10文件批量更新 | <2s | 分支切换 |
| 100文件批量更新 | <10s | 代码拉取 |
| 全量同步(100万行) | <8min | 首次运行 |

## 目录结构

```
ark-analyzer/
├── backend/
│   ├── src/
│   │   ├── ark_analyzer.py      # 主入口
│   │   ├── config.py            # 配置管理
│   │   ├── database/            # 数据库模块
│   │   ├── services/            # 业务服务
│   │   ├── api/                 # API路由
│   │   └── utils/               # 工具函数
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/          # React组件
│   │   ├── pages/               # 页面
│   │   ├── stores/              # 状态管理
│   │   └── services/            # API服务
│   └── package.json
├── sample-project/              # 示例ArkTS项目
└── README.md
```

## 配置说明

### 环境变量

```bash
ARK_WATCH_PATH=/path/to/project
SILICONFLOW_API_KEY=your-api-key
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
LLM_MODEL_NAME=Qwen/Qwen2.5-7B-Instruct
```

### 配置文件 (config.json)

```json
{
  "watch_path": "/workspace/project",
  "api_key": "sk-xxx",
  "base_url": "https://api.siliconflow.cn/v1",
  "model_name": "Qwen/Qwen2.5-7B-Instruct",
  "debounce_seconds": 1.0,
  "enable_llm_analysis": true,
  "database_path": "arkgraph.db"
}
```

## 技术栈

| 层级 | 技术选型 |
|-----|---------|
| 前端框架 | React 18 + TypeScript |
| 构建工具 | Vite 5 |
| 样式方案 | Tailwind CSS |
| 可视化 | D3.js + react-force-graph |
| 状态管理 | Zustand |
| 后端框架 | FastAPI + Uvicorn |
| 数据库 | SQLite + aiosqlite |
| 文件监控 | watchdog |
| LLM服务 | 硅基流动API |

## 许可证

MIT License

## 致谢

- [React](https://reactjs.org/) - 用户界面框架
- [FastAPI](https://fastapi.tiangolo.com/) - 现代Python Web框架
- [D3.js](https://d3js.org/) - 数据可视化库
- [Tailwind CSS](https://tailwindcss.com/) - 原子化CSS框架
- [硅基流动](https://siliconflow.cn/) - LLM推理服务
