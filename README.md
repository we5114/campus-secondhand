# 校园二手交易智能分析与推荐平台

## 项目简介

校园二手交易智能分析与推荐平台是一个面向高校学生的二手交易平台，集成了大数据分析、智能推荐和大模型应用等功能。平台提供商品发布、搜索、交易、聊天等核心功能，并通过大数据分析和机器学习算法为用户提供个性化推荐服务。

## 技术栈

### 后端技术
- **框架**: FastAPI (Python 3.12+)
- **数据库**: MySQL 8.0+
- **缓存**: Redis 7+
- **搜索引擎**: Elasticsearch 8+
- **消息队列**: Kafka 3.6+
- **ORM**: SQLAlchemy 2.0+
- **认证**: JWT

### 大数据技术
- **计算引擎**: Spark 3.5+
- **数据仓库**: Hive 4.0+
- **分布式存储**: Hadoop 3.3+
- **数据同步**: Sqoop / DataX

### 前端技术
- **框架**: Vue 3 + Vite
- **UI组件**: Element Plus
- **图表**: ECharts 5+
- **状态管理**: Pinia
- **路由**: Vue Router 4

### 大模型应用
- **智能客服**: RAG + 知识库
- **内容生成**: 商品描述自动生成
- **内容审核**: 敏感词检测 + 大模型审核
- **情感分析**: 评论情感分析

### 部署技术
- **容器化**: Docker + Docker Compose
- **反向代理**: Nginx
- **CI/CD**: GitHub Actions (可选)

## 项目结构

```
campus-secondhand/
├── collector/          # 数据采集模块
│   ├── src/           # 采集器源码
│   └── config/        # 配置文件
├── spark/             # Spark大数据计算
│   ├── jobs/          # Spark任务
│   ├── utils/         # 工具类
│   └── config/        # 配置文件
├── sql/               # SQL脚本
│   ├── mysql/         # MySQL建表脚本
│   └── hive/          # Hive建表脚本
├── api/               # FastAPI后端API
│   ├── app/
│   │   ├── config/    # 配置
│   │   ├── api/v1/    # API路由
│   │   ├── service/   # 业务服务层
│   │   ├── dao/       # 数据访问层
│   │   ├── models/    # 数据模型
│   │   ├── schemas/   # Pydantic模型
│   │   ├── middleware/ # 中间件
│   │   └── utils/     # 工具类
│   └── tests/         # 测试
├── model/             # 推荐模型
│   ├── recommendation/ # 推荐算法
│   ├── features/      # 特征工程
│   └── utils/         # 工具类
├── llm/               # 大模型应用
│   ├── chat/          # 智能客服
│   ├── generation/    # 内容生成
│   ├── moderation/    # 内容审核
│   └── utils/         # 工具类
├── web/               # Vue前端
│   ├── public/        # 静态资源
│   └── src/
│       ├── api/       # API请求
│       ├── assets/    # 资源文件
│       ├── components/ # 组件
│       ├── views/     # 页面
│       ├── router/    # 路由
│       ├── store/     # 状态管理
│       ├── utils/     # 工具类
│       ├── hooks/     # 组合式函数
│       ├── directives/ # 指令
│       └── layouts/   # 布局
├── docker/            # Docker配置
│   ├── nginx/         # Nginx配置
│   ├── backend/       # 后端Dockerfile
│   ├── frontend/      # 前端Dockerfile
│   ├── mysql/init/    # MySQL初始化
│   ├── redis/         # Redis配置
│   ├── elasticsearch/ # ES配置
│   └── kafka/         # Kafka配置
└── README.md          # 项目说明
```

## 核心功能模块

### 1. 用户系统
- 用户注册、登录
- 个人信息管理
- 实名认证
- 用户等级体系

### 2. 商品系统
- 商品发布、编辑、下架
- 商品详情展示
- 商品收藏
- 智能定价建议
- 商品分类管理

### 3. 订单系统
- 购物车功能
- 下单流程
- 支付集成
- 订单管理
- 退款处理
- 评价系统

### 4. 搜索系统
- 关键词搜索
- 分类筛选
- 价格区间筛选
- Elasticsearch全文检索

### 5. 推荐系统
- 首页个性化推荐
- 相似商品推荐
- 热门商品推荐
- 新品推荐
- 基于用户行为的协同过滤

### 6. 消息系统
- 站内消息通知
- 即时聊天功能
- 消息已读/未读状态

### 7. 管理系统
- 用户管理
- 商品审核
- 订单管理
- 数据统计仪表盘
- 操作日志

### 8. 数据分析
- 交易数据分析
- 用户行为分析
- 商品销售分析
- 大屏可视化展示

### 9. 大模型应用
- 智能客服（RAG + 知识库）
- 商品描述自动生成
- 内容安全审核
- 评论情感分析

## 数仓架构

### 数仓分层
- **ODS层**：操作数据层，保持与源系统数据结构一致
- **DWD层**：明细数据层，数据清洗与规范化
- **DWS层**：数据服务层，按主题域聚合
- **ADS层**：应用数据层，推荐结果、用户画像、报表等

### 核心表
- 用户表、商品表、订单表、用户行为表
- 用户画像宽表、商品画像宽表
- 销售报表、热门商品榜、用户留存分析

## 推荐系统架构

### 召回层
- 基于用户的协同过滤（UserCF）
- 基于物品的协同过滤（ItemCF）
- 标签召回
- 热门召回
- 新品召回

### 排序层
- 逻辑回归（LR）
- GBDT
- DeepFM
- 多目标排序

### 特征工程
- 用户特征（基础属性、行为特征、偏好特征）
- 商品特征（基础属性、统计特征、内容特征）
- 上下文特征（时间、地点、设备）
- 交叉特征

## 快速开始

### 环境要求
- Docker & Docker Compose
- Python 3.12+
- Node.js 18+
- MySQL 8.0+
- Redis 7+

### 一键部署（Docker）

```bash
# 克隆项目
git clone <repository-url>
cd campus-secondhand

# 启动所有服务
cd docker
docker-compose up -d

# 查看服务状态
docker-compose ps
```

### 本地开发

#### 后端开发

```bash
# 进入后端目录
cd api

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 修改 .env 中的配置

# 启动服务
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端开发

```bash
# 进入前端目录
cd web

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 数据库初始化

```bash
# 导入MySQL初始化脚本
mysql -u root -p < sql/mysql/init.sql

# 导入Hive建表脚本（需在Hive环境中执行）
hive -f sql/hive/create_tables.sql
```

## API文档

启动后端服务后，访问以下地址查看API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 默认账号

### 管理员账号
- 用户名: admin
- 密码: admin123

### 测试用户
- 用户名: test001
- 密码: test123456

## 配置说明

### 后端配置（api/.env）
```env
# 数据库配置
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/campus_secondhand?charset=utf8mb4

# Redis配置
REDIS_URL=redis://:password@localhost:6379/0

# Elasticsearch配置
ELASTICSEARCH_URL=http://localhost:9200

# JWT配置
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 大模型配置
LLM_API_KEY=your-api-key
LLM_API_BASE=https://api.openai.com/v1
LLM_MODEL_NAME=DeepSeek-v4-flash
```

### 前端配置（web/.env）
```env
# API地址
VITE_API_BASE_URL=http://localhost:8000/api/v1

# 上传地址
VITE_UPLOAD_URL=http://localhost:8000/uploads
```

## 开发规范

### 代码规范
- 后端：遵循 PEP 8 规范
- 前端：遵循 ESLint + Prettier 规范
- 提交：遵循 Conventional Commits 规范

### 分支管理
- `main`：主分支，生产环境
- `develop`：开发分支
- `feature/*`：功能分支
- `bugfix/*`：修复分支
- `hotfix/*`：紧急修复分支

## 性能优化

### 后端优化
- Redis缓存热点数据
- 数据库索引优化
- 异步任务处理
- 连接池管理

### 前端优化
- 路由懒加载
- 组件按需引入
- 图片懒加载
- Gzip压缩

### 大数据优化
- 数据分区
- 列式存储
- 内存计算
- 增量计算

## 安全措施

- 用户密码加密存储（bcrypt）
- JWT令牌认证
- SQL注入防护（ORM）
- XSS攻击防护
- CSRF防护
- 接口限流
- 敏感数据脱敏
- 内容安全审核

## 监控与运维

- 应用健康检查
- 日志收集与分析
- 性能监控
- 告警通知
- 数据备份


