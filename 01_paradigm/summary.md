## 本章小结

本章我们开启了 Agentic AI 的探索之旅，从发展范式、理论模型到核心组件，为您构建了智能体的宏观认知框架。

### 核心要点回顾

1.  **范式转移：从 LLM 到 Agent**
    *   **LLM (System 1)**：被动、无状态、依赖直觉的快速思考者。
    *   **Agent (System 2)**：主动、有目标、具备规划能力的慢思考者。它通过“感知-思考-行动”的循环，突破了 LLM 仅能生成文本的局限。

2.  **理论基石：理性智能体**
    *   **定义**：在现有信息和计算能力下，追求**性能度量（Performance Measure）**最大化的系统。
    *   **PEAS 框架**：设计 Agent 时必须明确其性能目标 (P)、环境 (E)、执行器 (A) 和传感器 (S)。
    *   **运行机制**：将智能体视为部分可观测马尔可夫决策过程 (**POMDP**) 的求解器，通过**状态-动作-奖励（State-Action-Reward）** 的闭环循环与环境交互。

3.  **解剖学结构：四大核心组件**
    *   **大脑 (Brain)**：由 LLM 驱动，负责角色扮演、逻辑推理、任务拆解与规划。
    *   **感知 (Perception)**：多模态输入处理（文本、视觉、音频）及环境状态感知。
    *   **行动 (Action/Tools)**：通过**函数调用（Function Calling）** 使用外部工具（搜索、代码执行、API），是 Agent 改变世界的手。
    *   **记忆 (Memory)**：克服**上下文窗口**限制，结合短期记忆（上下文）与长期记忆（向量数据库/检索增强生成 RAG），实现经验的积累。

### 下一步
理解了“Agent 是什么”和“由什么组成”之后，下一章我们将深入微观层面，详细讲解 Agent 如何像人类一样进行复杂的**规划**、构建**记忆**以及熟练地**使用工具**。

---

**下一节**: [第二章：认知架构详解 (Cognitive Architecture)](../02_reasoning/README.md)

### 本章核心参考文献

*   [**Language Models are Few-Shot Learners**](https://arxiv.org/abs/2005.14165) (GPT-3): 展示了 LLM 的通用潜力。
*   [**ReAct: Synergizing Reasoning and Acting in Language Models**](https://arxiv.org/abs/2210.03629): 奠定了现代 Agent "推理-再行动" 的基础模式。