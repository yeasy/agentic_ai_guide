## 本章小结

本章通过代码实战，对比了当前最主流的三大 Agent 开发框架。工具没有绝对的优劣，只有适不适合。

### 核心要点回顾

1.  **框架生态概览**
    *   **LangGraph**：**Agent as a Graph**。强调深度控制与状态管理，适合构建复杂的、生产级的业务流。
    *   **AutoGen**：**Calibration through Conversation**。强调多智能体对话与代码执行，是 Coding Agent 和科研探索的首选。
    *   **CrewAI**：**Role-Playing Squad**。强调角色扮演与易用性，适合内容创作和快速原型开发。

2.  **LangGraph 实战：深度控制**
    *   利用 **StateGraph** 构建状态机，清晰定义 Node（行动）与 Edge（流转）。
    *   通过 **Checkpointer** 实现状态持久化，天然支持 **Human-in-the-loop**（人工审批/断点续传），为企业级应用提供了必要的确定性。

3.  **AutoGen 与 CrewAI 实战：多体协作**
    *   **AutoGen**：展示了强大的 UserProxy与 Assistant 闭环，通过代码解释器自动修复错误，实现“自我纠错”。
    *   **CrewAI**：展示了如何像写剧本一样定义 Researcher 和 Writer，自动处理任务间的上下文传递，极大简化了开发体验。

| 场景 | 推荐框架 | 核心理由 |
| :--- | :--- | :--- |
| **企业核心业务流** | LangGraph | 状态可控、支持人工介入、容错强 |
| **代码生成/数据分析** | AutoGen | 内置代码解释器、Docker 沙箱支持 |
| **内容创作/快速 Demo** | CrewAI | 上手快、角色定义清晰、心智负担小 |

### 下一步
写出代码只是第一步，让 Agent 在生产环境中稳定运行才是真正的挑战。下一章我们将探讨**系统架构与工程化**，解决鲁棒性、成本与性能问题。

---

**下一节**: [第九章：AgentOps 与生产化落地](../09_agentops/README.md)