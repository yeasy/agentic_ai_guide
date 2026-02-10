# 第八章：开发框架全景

纸上得来终觉浅，绝知此事要躬行。前几章我们讨论了理论，本章我们将深入当前最热门的智能体开发框架生态。从 LangChain 到 AutoGen，从 CrewAI 到企业级方案，我们将分析它们的设计哲学、优缺点，并帮助你在不同场景下做出正确的技术选型。

## 章节导读

- **[8.1 框架生态概览与选型指南](8.1_ecosystem.md)**
  - 横向对比主流框架的设计哲学。LangGraph 强调图控制 (Graph Control)，AutoGen 强调对话流 (Dialogue Flow)，CrewAI 强调角色扮演 (Role-playing) 与易用性。一张表帮你快速选型。

- **[8.2 LangChain 与 LangGraph：从链到图](8.2_langchain.md)**
  - 从早期的 Chain 到现代的 Graph，LangChain 生态如何演进？实战：使用 LangGraph 构建一个带有 Human-in-the-loop 功能的客服智能体。

- **[8.3 LlamaIndex：数据驱动的 RAG 专家](8.3_llamaindex.md)**
  - 虽然 LlamaIndex 以 RAG 闻名，但它在智能体领域也构建了独特的生态。学习如何用作为工具的查询引擎 (Query Engine as Tool) 构建数据驱动的智能体。

- **[8.4 多智能体框架：AutoGen 与 CrewAI](8.4_multi_agent.md)**
  - 实战：用 CrewAI 组建一个"市场调研团队"；用 AutoGen 构建一个可以自动写代码并执行的"工程师+产品经理"对话组。

- **[8.5 企业级方案：Semantic Kernel 与 Dify](8.5_enterprise.md)**
  - 探讨企业级智能体开发需求。Semantic Kernel 的跨语言支持，Dify 的低代码平台，以及如何与现有企业系统集成。

- **[8.6 平台级产品：OpenAI Assistants 与 Claude Artifacts](8.6_platforms.md)**
  - 主流 AI 厂商的智能体产品解析。OpenAI 的 Assistants API、Anthropic 的 Claude 工具使用，以及它们与开源框架的对比。

- **[8.7 框架性能基准评测](8.7_performance.md)**
  - 哪个框架最快？哪个最省钱？对比 LangChain, AutoGen, CrewAI 等框架在延迟、吞吐量和 Token 消耗方面的性能表现。

- **[本章小结](summary.md)**

## 框架选型速查表

| 目标场景 | 推荐框架 | 核心优势 |
|:---------|:---------|:---------|
| 快速原型开发 | CrewAI | 简单易用，角色扮演范式 |
| RAG/知识智能体 | LlamaIndex | 数据处理和索引能力强 |
| 精细控制流程 | LangGraph | 状态机级别的控制粒度 |
| 多智能体协作 | AutoGen | 对话驱动，代码执行能力强 |
| 企业级集成 | Semantic Kernel | 跨语言，与微软生态集成 |
| 低代码平台 | Dify | 可视化编排，快速上线 |

下一章我们将探讨如何将智能体系统工程化落地，实现生产级别的稳定运行。

---

**下一节**: [框架生态概览与选型指南](8.1_ecosystem.md)
