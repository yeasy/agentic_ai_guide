# 第四章：工具使用与环境交互

工具使用是智能体从"纯语言模型"进化为"行动者"的关键能力。通过工具，智能体 (Agent) 可以突破知识边界、执行实际操作、与外部世界交互。本章将全面探讨智能体的工具使用能力。

## 本章概览

### 为什么工具使用如此重要

大语言模型虽然强大，但存在固有局限：

| 局限 | 示例 | 工具解决方案 |
|------|------|--------------|
| 知识截止日期 | 不知道最新新闻 | 网页搜索工具 |
| 无法计算 | 复杂数学容易出错 | 计算器/代码执行 |
| 无法访问私有数据 | 不知道用户文件 | 文件系统工具 |
| 无法执行操作 | 不能发送邮件 | API 调用工具 |
| 无法感知环境 | 不知道当前时间 | 系统信息工具 |

### 工具的分类

```
工具类型
│
├── 信息获取类
│   ├── 搜索引擎
│   ├── 数据库查询
│   └── API 调用
│
├── 计算执行类
│   ├── 代码解释器
│   ├── 数学计算器
│   └── 数据处理
│
├── 环境交互类
│   ├── 文件系统
│   ├── 浏览器控制
│   └── 命令行操作
│
└── 通信类
    ├── 发送消息
    ├── 调用其他 Agent
    └── 人机交互
```

### 本章结构

```
第四章：工具使用与环境交互
│
├── 4.1 工具使用概述与分类
│   └── 工具的定义、分类和设计原则
│
├── 4.2 函数调用 (Function Calling) 详解
│   └── OpenAI/Claude 等平台的实现机制
│
├── 4.3 MCP：模型上下文协议
│   └── Anthropic 的标准化工具协议
│
├── 4.4 Agent Skills：能力扩展规范
│   └── 轻量级技能封装与渐进式加载
│
├── 4.5 环境交互：代码解释器与浏览器操作
│   └── 代码执行沙箱与计算机操作 (Computer Use)
│
└── 4.6 多模态感知与行动
    └── 图像、音频等多模态工具
```

## 工具使用的核心流程

### 基本循环

```python
while not task_completed:
    # 1. 理解当前状态和目标
    analysis = llm.analyze(context, goal)
    
    # 2. 决定是否需要使用工具
    if needs_tool(analysis):
        # 3. 选择合适的工具
        tool = select_tool(analysis, available_tools)
        
        # 4. 生成工具参数
        params = generate_params(analysis, tool)
        
        # 5. 执行工具
        result = execute_tool(tool, params)
        
        # 6. 将结果反馈给模型
        context.add(f"工具返回：{result}")
    else:
        # 直接生成回答
        response = llm.generate(context)
        return response
```

### 工具选择的决策过程

```
用户请求："现在北京天气怎么样？"
     │
     ▼
┌─────────────────────────────────────────────┐
│ 分析需求：                                   │
│ - 需要实时天气数据                           │
│ - 这不是我的训练数据能回答的                  │
│ - 需要使用外部工具                           │
└─────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────┐
│ 可用工具：                                   │
│ - search_web: 通用搜索 ❌ (不够精确)         │
│ - get_weather: 获取天气 ✅ (最合适)          │
│ - calculator: 计算器 ❌ (不相关)             │
└─────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────┐
│ 工具调用：                                   │
│ get_weather(location="北京")                 │
└─────────────────────────────────────────────┘
     │
     ▼
结果处理 → 生成回答
```

## 工具定义的最佳实践

### 好的工具定义

```python
tools = [
    {
        "name": "search_web",
        "description": "搜索互联网获取信息。适用于查询新闻、事实、最新数据等。不适用于需要推理或创作的任务。",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索查询词，应该简洁明确"
                },
                "num_results": {
                    "type": "integer",
                    "description": "返回结果数量，默认 5",
                    "default": 5
                }
            },
            "required": ["query"]
        },
        "examples": [
            {"query": "2024年诺贝尔物理学奖获得者"},
            {"query": "Python 3.12 新特性", "num_results": 3}
        ]
    }
]
```

### 工具定义要素

| 要素 | 说明 | 重要性 |
|------|------|--------|
| name | 简洁、有意义的名称 | 必须 |
| description | 详细说明用途和限制 | 关键 |
| parameters | 清晰的参数定义 | 必须 |
| examples | 示例调用 | 推荐 |
| use_when | 何时应该使用 | 推荐 |
| avoid_when | 何时不应使用 | 推荐 |

## 错误处理

### 工具执行可能的失败

```python
class ToolExecutor:
    def execute(self, tool: Tool, params: dict) -> ToolResult:
        try:
            result = tool.run(**params)
            return ToolResult(success=True, data=result)
        
        except InvalidParameterError as e:
            return ToolResult(
                success=False,
                error=f"参数错误：{e}",
                suggestion="请检查参数格式"
            )
        
        except ToolNotAvailableError as e:
            return ToolResult(
                success=False,
                error=f"工具暂时不可用：{e}",
                suggestion="稍后重试或使用替代方案"
            )
        
        except RateLimitError as e:
            return ToolResult(
                success=False,
                error=f"调用频率超限：{e}",
                suggestion="等待后重试"
            )
        
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"未知错误：{e}",
                suggestion="请联系管理员"
            )
```

### 让模型处理错误

```python
def handle_tool_error(error: ToolResult, context: str) -> str:
    prompt = f"""工具调用失败。

错误信息：{error.error}
建议：{error.suggestion}

请根据错误信息决定下一步操作：
1. 修正参数重试
2. 使用替代工具
3. 告知用户无法完成

当前上下文：{context}

你的决定："""
    
    return llm.generate(prompt)
```

## 安全考虑

### 工具的风险级别

| 风险级别 | 示例工具 | 安全措施 |
|----------|----------|----------|
| 低 | 天气查询、计算器 | 无需特殊措施 |
| 中 | 网页搜索、文件读取 | 输入验证 |
| 高 | 代码执行、API 调用 | 沙箱 + 审批 |
| 极高 | 文件删除、系统命令 | 人工确认 |

### 安全防护措施

```python
class SecureToolExecutor:
    def execute(self, tool: Tool, params: dict, user: User) -> ToolResult:
        # 1. 权限检查
        if not user.has_permission(tool.required_permission):
            raise PermissionDenied(f"用户无权使用工具：{tool.name}")
        
        # 2. 输入验证
        validated_params = self.validate_params(tool, params)
        
        # 3. 高风险操作确认
        if tool.risk_level >= RiskLevel.HIGH:
            if not self.get_user_confirmation(tool, validated_params):
                return ToolResult(success=False, error="用户取消操作")
        
        # 4. 沙箱执行
        if tool.requires_sandbox:
            return self.execute_in_sandbox(tool, validated_params)
        
        # 5. 记录审计日志
        self.log_execution(tool, validated_params, user)
        
        return tool.run(**validated_params)
```

## 本章你将学到

完成本章后，你将能够：

1. **理解**工具使用的核心机制和设计原则
2. **实现**基于 Function Calling 的工具集成
3. **使用** MCP 协议构建标准化工具接口
4. **搭建**安全的代码执行环境
5. **集成**多模态和浏览器自动化能力

## 下一步

接下来，我们首先深入了解工具使用的基础——工具的分类和设计原则。

---

**下一节**: [工具使用概述与分类](4.1_overview.md)