# Rasa React Flow 可视化编辑系统 - 完整设计方案

## 一、系统架构概览

### 1.1 核心组件架构

```
┌──────────────────────────────────────────────────────────────────┐
│                        前端层 (Frontend)                          │
│                                                                    │
│  ┌──────────────────┐    ┌──────────────────┐                    │
│  │  React Flow UI   │    │  状态管理 (Zustand)│                   │
│  │  - 节点编辑器    │    │  - Flow State      │                   │
│  │  - 连接器        │    │  - UI State        │                   │
│  │  - 控制面板      │    └──────────────────┘                    │
│  └──────────────────┘                                             │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              自定义节点组件                                │   │
│  │  [Intent] [Action] [Condition] [Start] [End]             │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────┬───────────────────────────────────────────┘
                       │ HTTP/REST API
                       │ WebSocket (实时协作)
┌──────────────────────▼───────────────────────────────────────────┐
│                        后端层 (Backend)                           │
│                                                                    │
│  ┌──────────────────┐    ┌──────────────────┐                    │
│  │  Sanic REST API  │    │  Flow Manager     │                    │
│  │  - CRUD Endpoints│    │  - 流程管理       │                    │
│  │  - Validation    │    │  - 版本控制       │                    │
│  │  - Export/Import │    └──────────────────┘                    │
│  └──────────────────┘                                             │
│                                                                    │
│  ┌──────────────────┐    ┌──────────────────┐                    │
│  │  Flow Converter  │    │  Storage Layer    │                    │
│  │  - Flow → Story  │    │  - JSON Files     │                    │
│  │  - Story → Flow  │    │  - Database (可选) │                    │
│  └──────────────────┘    └──────────────────┘                    │
└──────────────────────┬───────────────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────────────┐
│                    Rasa 核心层 (Rasa Core)                        │
│                                                                    │
│  ┌──────────────────┐    ┌──────────────────┐                    │
│  │  Story Graph     │    │  Policy Ensemble  │                    │
│  │  Dialogue Manager│    │  NLU Pipeline     │                    │
│  └──────────────────┘    └──────────────────┘                    │
└────────────────────────────────────────────────────────────────────┘
```

## 二、数据模型设计

### 2.1 核心数据结构

#### FlowNode (节点)
```typescript
interface FlowNode {
  id: string;                    // 唯一标识
  type: NodeType;                // 节点类型
  position: { x: number; y: number }; // 位置
  data: NodeData;                // 节点数据
  style?: CSSProperties;         // 样式
}

type NodeType = 
  | 'start'       // 开始节点
  | 'end'         // 结束节点
  | 'intent'      // 意图节点
  | 'action'      // 动作节点
  | 'condition'   // 条件节点
  | 'slot'        // 槽位节点
  | 'form'        // 表单节点
  | 'rule';       // 规则节点

interface NodeData {
  label: string;               // 显示标签
  intent?: string;             // 意图名称
  action?: string;             // 动作名称
  condition?: ConditionData;   // 条件数据
  slot?: SlotData;             // 槽位数据
  entities?: EntityData[];     // 实体数据
  metadata?: Record<string, any>; // 元数据
}
```

#### FlowEdge (连接)
```typescript
interface FlowEdge {
  id: string;                    // 唯一标识
  source: string;                // 源节点ID
  target: string;                // 目标节点ID
  sourceHandle?: string;         // 源句柄
  targetHandle?: string;         // 目标句柄
  label?: string;                // 边标签
  type?: EdgeType;               // 边类型
  data?: EdgeData;               // 边数据
}

type EdgeType = 
  | 'default'    // 默认连接
  | 'conditional' // 条件连接
  | 'fallback';   // 回退连接

interface EdgeData {
  condition?: string;          // 条件表达式
  probability?: number;        // 概率权重
  metadata?: Record<string, any>;
}
```

#### ConversationFlow (会话流)
```typescript
interface ConversationFlow {
  id: string;                    // 流程ID
  name: string;                  // 流程名称
  description?: string;          // 流程描述
  nodes: FlowNode[];             // 节点列表
  edges: FlowEdge[];             // 连接列表
  metadata: FlowMetadata;        // 元数据
  version: string;               // 版本号
  tags?: string[];               // 标签
}

interface FlowMetadata {
  created_at: string;            // 创建时间
  updated_at: string;            // 更新时间
  created_by?: string;           // 创建者
  last_modified_by?: string;     // 最后修改者
  bot_id?: string;               // 机器人ID (多机器人支持)
  status: 'draft' | 'published' | 'archived'; // 状态
}
```

## 三、功能模块设计

### 3.1 前端功能模块

#### 1. 流程编辑器 (Flow Editor)
```typescript
- 可视化画布
  - 缩放 (Zoom)
  - 平移 (Pan)
  - 小地图 (MiniMap)
  - 网格背景 (Grid Background)
  
- 节点操作
  - 拖拽添加节点
  - 节点选择/删除
  - 节点属性编辑
  - 节点复制/粘贴
  
- 连接操作
  - 可视化连接
  - 连接验证
  - 连接删除
  - 条件分支
  
- 撤销/重做 (Undo/Redo)
- 自动布局 (Auto Layout)
- 导入/导出
```

#### 2. 节点类型库

**Intent Node (意图节点)**
```typescript
- 配置项:
  - 意图名称
  - 示例文本
  - 实体标注
  - 置信度阈值
  
- 视觉样式:
  - 蓝色主题
  - 圆角矩形
  - 意图图标
```

**Action Node (动作节点)**
```typescript
- 配置项:
  - 动作名称
  - 动作类型 (utter/custom)
  - 动作参数
  - 响应内容
  
- 视觉样式:
  - 绿色主题
  - 矩形
  - 动作图标
```

**Condition Node (条件节点)**
```typescript
- 配置项:
  - 条件表达式
  - 槽位检查
  - 分支路径 (True/False)
  
- 视觉样式:
  - 橙色主题
  - 菱形
  - 多输出端口
```

#### 3. 属性面板
```typescript
- 节点属性编辑
  - 基本信息
  - 详细配置
  - 验证规则
  
- 流程属性
  - 元数据编辑
  - 版本管理
  - 标签管理
```

#### 4. 工具栏
```typescript
- 文件操作
  - 新建流程
  - 打开流程
  - 保存流程
  - 另存为
  
- 编辑操作
  - 撤销/重做
  - 复制/粘贴
  - 删除
  
- 视图操作
  - 放大/缩小
  - 适应画布
  - 网格开关
  
- 辅助工具
  - 验证流程
  - 导出为Story
  - 测试流程
```

### 3.2 后端功能模块

#### 1. Flow API
```python
# 流程管理
GET    /api/flows              # 列出所有流程
POST   /api/flows              # 创建新流程
GET    /api/flows/{id}         # 获取流程详情
PUT    /api/flows/{id}         # 更新流程
DELETE /api/flows/{id}         # 删除流程
POST   /api/flows/{id}/clone   # 克隆流程

# 节点操作
POST   /api/flows/{id}/nodes            # 添加节点
PUT    /api/flows/{id}/nodes/{node_id}  # 更新节点
DELETE /api/flows/{id}/nodes/{node_id}  # 删除节点

# 连接操作
POST   /api/flows/{id}/edges            # 添加连接
DELETE /api/flows/{id}/edges/{edge_id}  # 删除连接

# 验证和转换
POST   /api/flows/{id}/validate         # 验证流程
GET    /api/flows/{id}/export/stories   # 导出为Stories
POST   /api/flows/import/stories        # 从Stories导入

# 版本控制
GET    /api/flows/{id}/versions         # 获取版本历史
POST   /api/flows/{id}/versions         # 创建新版本
GET    /api/flows/{id}/versions/{ver}   # 获取特定版本
POST   /api/flows/{id}/versions/{ver}/restore # 恢复版本
```

#### 2. Flow Converter (转换器)
```python
class FlowConverter:
    """流程与Story格式转换器"""
    
    @staticmethod
    def flow_to_stories(flow: ConversationFlow) -> List[StoryStep]:
        """将Flow转换为Rasa Story格式"""
        - 图遍历算法
        - 路径生成
        - 事件序列构建
        
    @staticmethod
    def stories_to_flow(stories: List[StoryStep]) -> ConversationFlow:
        """将Rasa Story转换为Flow格式"""
        - 事件解析
        - 节点生成
        - 连接推断
        
    @staticmethod
    def flow_to_rules(flow: ConversationFlow) -> List[RuleStep]:
        """将Flow转换为Rasa Rule格式"""
        
    @staticmethod
    def validate_flow(flow: ConversationFlow) -> ValidationResult:
        """验证流程的完整性和正确性"""
        - 检查孤立节点
        - 检查循环依赖
        - 验证必填字段
        - 检查逻辑错误
```

#### 3. Storage Layer (存储层)
```python
class FlowStorage:
    """流程存储管理"""
    
    def save_flow(self, flow: ConversationFlow) -> None:
        """保存流程到存储"""
        
    def load_flow(self, flow_id: str) -> ConversationFlow:
        """从存储加载流程"""
        
    def delete_flow(self, flow_id: str) -> bool:
        """删除流程"""
        
    def list_flows(self) -> List[FlowMetadata]:
        """列出所有流程"""
        
    def search_flows(self, query: str) -> List[FlowMetadata]:
        """搜索流程"""

# 支持多种存储后端
class FileSystemStorage(FlowStorage):
    """文件系统存储"""
    
class DatabaseStorage(FlowStorage):
    """数据库存储 (PostgreSQL/MongoDB)"""
    
class RedisStorage(FlowStorage):
    """Redis缓存存储"""
```

## 四、多机器人支持设计

### 4.1 多机器人架构
```
┌─────────────────────────────────────────────────────┐
│                  Flow Editor UI                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │  Bot A   │  │  Bot B   │  │  Bot C   │          │
│  │  Flows   │  │  Flows   │  │  Flows   │          │
│  └──────────┘  └──────────┘  └──────────┘          │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│              Bot Management Service                  │
│  - 机器人注册与管理                                  │
│  - Flow隔离                                          │
│  - 权限控制                                          │
│  - 资源分配                                          │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│              Individual Bot Instances                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │ Bot A    │  │ Bot B    │  │ Bot C    │          │
│  │ Instance │  │ Instance │  │ Instance │          │
│  └──────────┘  └──────────┘  └──────────┘          │
└─────────────────────────────────────────────────────┘
```

### 4.2 Bot 数据模型
```typescript
interface Bot {
  id: string;                    // 机器人ID
  name: string;                  // 机器人名称
  description?: string;          // 描述
  flows: string[];               // 关联的Flow IDs
  domain: Domain;                // Domain配置
  config: BotConfig;             // 配置
  metadata: BotMetadata;         // 元数据
}

interface BotConfig {
  language: string;              // 语言
  pipeline: string;              // NLU pipeline
  policies: Policy[];            // 对话策略
  endpoints: Endpoints;          // 端点配置
}
```

### 4.3 Bot Management API
```python
# Bot管理
GET    /api/bots                # 列出所有机器人
POST   /api/bots                # 创建新机器人
GET    /api/bots/{bot_id}       # 获取机器人详情
PUT    /api/bots/{bot_id}       # 更新机器人
DELETE /api/bots/{bot_id}       # 删除机器人

# Bot Flow关联
GET    /api/bots/{bot_id}/flows # 获取机器人的所有流程
POST   /api/bots/{bot_id}/flows # 为机器人创建流程
PUT    /api/bots/{bot_id}/flows/{flow_id} # 更新关联流程

# Bot训练和部署
POST   /api/bots/{bot_id}/train   # 训练机器人
GET    /api/bots/{bot_id}/status  # 获取训练状态
POST   /api/bots/{bot_id}/deploy  # 部署机器人
```

## 五、高级功能

### 5.1 实时协作
```typescript
- WebSocket连接
- 多用户同时编辑
- 光标位置同步
- 操作冲突检测
- 自动合并变更
```

### 5.2 版本控制
```typescript
- Git风格版本管理
- 版本比较 (Diff)
- 版本回滚
- 分支管理
- 合并请求
```

### 5.3 模板库
```typescript
- 预制流程模板
  - 问候流程
  - FAQ流程
  - 预约流程
  - 订单流程
  
- 自定义模板
- 模板分享
- 模板市场
```

### 5.4 测试与调试
```typescript
- 流程模拟器
  - 逐步执行
  - 断点调试
  - 变量查看
  
- 测试用例
  - 创建测试场景
  - 批量测试
  - 测试报告
```

### 5.5 分析与监控
```typescript
- 流程执行统计
- 节点访问热力图
- 转化率分析
- 错误追踪
- 性能监控
```

## 六、实施计划

### Phase 1: 基础架构 (2周)
- [x] 数据模型设计
- [x] 后端API框架
- [x] 前端项目搭建
- [x] 基础节点类型

### Phase 2: 核心功能 (3周)
- [ ] Flow编辑器完整实现
- [ ] CRUD API完整实现
- [ ] Flow-Story转换器
- [ ] 基础验证功能

### Phase 3: 高级功能 (3周)
- [ ] 多机器人支持
- [ ] 版本控制
- [ ] 导入导出
- [ ] 高级节点类型

### Phase 4: 用户体验 (2周)
- [ ] UI/UX优化
- [ ] 性能优化
- [ ] 错误处理
- [ ] 帮助文档

### Phase 5: 测试与部署 (2周)
- [ ] 单元测试
- [ ] 集成测试
- [ ] 端到端测试
- [ ] 部署文档

## 七、技术栈

### 前端
- React 18
- TypeScript
- React Flow
- Zustand (状态管理)
- Axios (HTTP客户端)
- Vite (构建工具)

### 后端
- Python 3.8+
- Sanic (异步Web框架)
- Rasa 3.x
- SQLAlchemy (可选数据库)
- Redis (可选缓存)

### 开发工具
- ESLint & Prettier
- Black & MyPy
- Jest (前端测试)
- Pytest (后端测试)

## 八、性能优化

### 前端优化
```typescript
- 虚拟滚动 (大型流程)
- 节点懒加载
- 连接路径缓存
- 防抖节流
- Web Worker (复杂计算)
```

### 后端优化
```python
- 异步IO
- 缓存策略
- 批量操作
- 索引优化
- 连接池
```

## 九、安全考虑

### 认证与授权
```typescript
- OAuth 2.0 / JWT
- RBAC权限模型
- API密钥管理
- 审计日志
```

### 数据安全
```typescript
- 输入验证
- SQL注入防护
- XSS防护
- CSRF防护
- 数据加密
```

## 十、总结

这个完整的设计方案提供了一个强大的、可扩展的Rasa可视化编辑系统。通过React Flow实现直观的拖拽式编辑体验，同时保持与Rasa核心功能的深度集成。系统支持多机器人管理、实时协作、版本控制等企业级功能，适合大规模对话系统的开发和维护。
