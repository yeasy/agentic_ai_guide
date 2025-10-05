# 第三章：记忆系统架构

记忆是智能体持续学习和个性化响应的基础。一个设计良好的记忆系统能让 Agent 从经验中学习、维护长期上下文、并提供个性化服务。本章将深入探讨智能体记忆系统的设计与实现。

## 本章概览

### 为什么记忆很重要

人类的智能很大程度上依赖于记忆系统。同样，智能体要实现真正的"智能"，也需要具备记忆能力：

| 记忆能力 | Agent 中的应用 |
|----------|----------------|
| 短期记忆 | 维护当前对话上下文 |
| 长期记忆 | 记住用户偏好、历史交互 |
| 情景记忆 | 回忆特定事件的细节 |
| 语义记忆 | 存储和检索知识 |
| 程序性记忆 | 学习如何使用工具 |

### 本章结构

```
第三章：记忆系统架构
│
├── 3.1 记忆的认知模型：工作记忆 vs 长期记忆
│   └── 模拟人类记忆系统的设计思路
│
├── 3.2 向量数据库选型：Pinecone、Weaviate、Chroma
│   └── 长期记忆的持久化存储方案
│
├── 3.3 RAG 进阶：检索增强生成的最佳实践
│   └── 如何高效检索和利用记忆
│
└── 3.4 上下文窗口管理与压缩策略
    └── 在有限窗口中最大化信息利用
```

## 记忆系统的架构设计

### 典型的三层记忆架构

```
┌─────────────────────────────────────────────────────────┐
│                    Sensory Memory                        │
│            (当前输入的即时处理缓冲)                        │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                   Working Memory                         │
│    (工作记忆：当前对话上下文、活跃的思考内容)               │
│    实现：Context Window / Conversation History           │
│    特点：容量有限、访问快速                               │
└─────────────────────────────────────────────────────────┘
                           │
                    ┌──────┴──────┐
                    ▼             ▼
┌─────────────────────────┐  ┌─────────────────────────────┐
│    Episodic Memory      │  │      Semantic Memory        │
│    (情景记忆)            │  │      (语义记忆)              │
│                         │  │                             │
│ - 具体交互事件           │  │ - 结构化知识                 │
│ - 任务执行轨迹           │  │ - 用户偏好                   │
│ - 成功/失败经验          │  │ - 领域概念                   │
│                         │  │                             │
│ 实现：向量数据库         │  │ 实现：知识图谱 / 结构化存储   │
└─────────────────────────┘  └─────────────────────────────┘
```

### 代码示例：记忆系统骨架

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class Memory(ABC):
    @abstractmethod
    def store(self, content: str, metadata: Dict[str, Any]) -> str:
        """存储记忆，返回记忆ID"""
        pass
    
    @abstractmethod
    def retrieve(self, query: str, k: int = 5) -> List[Dict]:
        """检索相关记忆"""
        pass
    
    @abstractmethod
    def forget(self, memory_id: str) -> bool:
        """删除记忆"""
        pass


class WorkingMemory:
    """工作记忆：维护当前对话上下文"""
    
    def __init__(self, max_tokens: int = 4000):
        self.messages: List[Dict] = []
        self.max_tokens = max_tokens
    
    def add(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
        self._trim_if_needed()
    
    def _trim_if_needed(self):
        """当超出容量时，移除最早的消息"""
        while self._count_tokens() > self.max_tokens:
            self.messages.pop(0)
    
    def get_context(self) -> List[Dict]:
        return self.messages.copy()


class LongTermMemory(Memory):
    """长期记忆：基于向量数据库"""
    
    def __init__(self, vector_store, embeddings):
        self.vector_store = vector_store
        self.embeddings = embeddings
    
    def store(self, content: str, metadata: Dict[str, Any]) -> str:
        embedding = self.embeddings.embed(content)
        return self.vector_store.add(embedding, content, metadata)
    
    def retrieve(self, query: str, k: int = 5) -> List[Dict]:
        query_embedding = self.embeddings.embed(query)
        return self.vector_store.search(query_embedding, k)
```

## 关键设计决策

### 1. 记忆的粒度

| 粒度 | 示例 | 优点 | 缺点 |
|------|------|------|------|
| 消息级 | 每条用户消息 | 精细、可追溯 | 存储量大 |
| 对话级 | 整个对话摘要 | 存储效率高 | 丢失细节 |
| 事件级 | 关键事件/决策 | 平衡 | 需要定义"关键" |
| 知识级 | 提取的知识点 | 复用性强 | 抽象过程复杂 |

### 2. 存储与检索策略

**存储时机**：
- 实时存储：每次交互后立即存储
- 批量存储：会话结束后统一处理
- 选择性存储：只存储重要/关键内容

**检索时机**：
- 预加载：每次对话开始时加载相关记忆
- 按需检索：遇到相关话题时动态检索
- 混合策略：核心记忆预加载 + 细节按需检索

### 3. 记忆的更新与遗忘

```python
class MemoryManager:
    def update_memory(self, memory_id: str, new_content: str):
        """更新已有记忆，而非创建新的"""
        old_memory = self.get(memory_id)
        merged = self.merge(old_memory, new_content)
        self.store(memory_id, merged)
    
    def decay_old_memories(self, threshold_days: int = 30):
        """模拟遗忘：降低旧记忆的权重"""
        for memory in self.all_memories():
            age_days = (now() - memory.timestamp).days
            if age_days > threshold_days:
                memory.weight *= 0.9  # 衰减权重
```

## 本章你将学到

完成本章后，你将能够：

1. **理解**智能体记忆系统的认知模型和设计原则
2. **选择**适合项目需求的向量数据库
3. **实现**高效的 RAG 检索增强生成系统
4. **优化**有限上下文窗口的信息利用率
5. **设计**可扩展的长期记忆存储方案

## 下一步

接下来，我们首先深入探讨记忆的认知模型，理解工作记忆与长期记忆的区别，以及如何在智能体系统中模拟这些机制。

---

**下一节**: [3.1 Memory Models](3.1_memory_models.md)