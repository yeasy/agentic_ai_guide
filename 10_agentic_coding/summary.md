# 本章小结

本章我们探讨了从 Vibe Coding 到 Agentic Coding 的范式转移，并深入剖析了智能体编程的核心——**Agent Loop**。

## 关键概念清单

*   **Vibe Coding**：自然语言驱动、沉浸式、忽略代码细节的编程风格。
*   **Agentic Coding**：AI 作为自主智能体，具备理解、规划、执行、验证的完整闭环能力。
*   **Agent Loop (智能体循环)**：`思考 -> 工具调用 -> 环境反馈 -> 思考` 的状态机循环。
*   **Stop Sequence (停止序列)**：强制模型中断生成、交还控制权给宿主的关键机制。
*   **Agent Harness**：由 Instructions, Tools, User Messages 构成的智能体驾驭系统。
*   **Context Engineering**：通过 Rules, Skills 和文件引用来管理上下文，是 Agentic Coding 的核心技能。
*   **Plan Mode**：规划先于执行，"回退优于修补"。

## 实践要点

*   **工具选择**：Cursor 适合全栈开发，Claude Code 适合 DevOps/后端，GitHub Copilot 适合集成工作流。
*   **工作流升级**：从关注语法和 API，转向关注需求拆解、上下文准备和验收审查。
*   **上下文管理**：不要一次性塞入所有文件，利用 `@` 精确引用或让智能体自主检索。
*   **自动化**：利用 Bugbot 和 CI/CD 集成，让 AI 参与代码审查。

## 常见误区

*   **误区 1：期望 AI 一次性生成完美代码**。事实：Agentic Coding 是一个迭代过程，第一版往往需要修改。
*   **误区 2：试图用对话修补烂代码**。事实：当上下文污染严重时，`git reset` 或开启新对话永远比修补更快。
*   **误区 3：认为 Prompt 不重要**。事实：越强大的模型越依赖高质量的 Prompt（清晰的目标、充足的上下文、明确的约束）。

通过刻意练习，你将建立起与 AI 协作的"肌肉记忆"，真正成为 Agentic 时代的超级个体。

**下一章**: [第十一章：安全、伦理与未来](../11_future/README.md)
