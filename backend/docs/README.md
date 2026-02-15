# 文档目录

本目录包含Smart Payment Checkout后端项目的所有文档。

## 📚 文档列表

### [DEEPSEEK_LLM_GUIDE.md](DEEPSEEK_LLM_GUIDE.md)
**DeepSeek LLM集成完整指南**

**内容：**
- LLM集成概述
- 配置说明
- API密钥设置
- 功能特点
- 使用示例
- 错误处理
- 生产环境考虑
- 故障排查

**适用人群：** 开发者、运维人员

### [LLM_WITHOUT_3DS_GUIDE.md](LLM_WITHOUT_3DS_GUIDE.md)
**如何触发LLM分析但不触发3DS验证**

**内容：**
- 核心原理和阈值配置
- 风险规则评分详解
- 成功和失败示例
- 测试方法
- 风险分数组合表
- 实际应用场景
- 最佳实践
- 故障排查

**适用人群：** 开发者、测试人员

### [SETUP.md](SETUP.md)
**项目设置和配置指南**

**内容：**
- 环境要求
- 依赖安装
- 配置步骤
- 启动服务器
- 验证安装

**适用人群：** 新用户、开发者

## 🎯 快速导航

### 我想了解...
- **如何集成LLM？** → [DEEPSEEK_LLM_GUIDE.md](DEEPSEEK_LLM_GUIDE.md)
- **如何控制风险评分？** → [LLM_WITHOUT_3DS_GUIDE.md](LLM_WITHOUT_3DS_GUIDE.md)
- **如何设置项目？** → [SETUP.md](SETUP.md)

### 我遇到问题...
- **LLM API调用失败？** → [DEEPSEEK_LLM_GUIDE.md#故障排查](DEEPSEEK_LLM_GUIDE.md#故障排查)
- **3DS验证问题？** → [LLM_WITHOUT_3DS_GUIDE.md#故障排查](LLM_WITHOUT_3DS_GUIDE.md#故障排查)
- **配置错误？** → [SETUP.md](SETUP.md)

### 我想学习...
- **LLM工作原理？** → [DEEPSEEK_LLM_GUIDE.md#工作原理](DEEPSEEK_LLM_GUIDE.md#工作原理)
- **风险评分机制？** → [LLM_WITHOUT_3DS_GUIDE.md#核心原理](LLM_WITHOUT_3DS_GUIDE.md#核心原理)
- **最佳实践？** → [DEEPSEEK_LLM_GUIDE.md#最佳实践](DEEPSEEK_LLM_GUIDE.md#最佳实践)

## 📊 文档结构

```
docs/
├── DEEPSEEK_LLM_GUIDE.md       # LLM集成技术指南
├── LLM_WITHOUT_3DS_GUIDE.md    # 风险控制使用指南
└── SETUP.md                    # 项目设置指南
```

## 🔍 按主题分类

### 技术实现
- [DEEPSEEK_LLM_GUIDE.md](DEEPSEEK_LLM_GUIDE.md)
  - OpenAI API集成
  - DeepSeek模型配置
  - 错误处理机制
  - 降级策略

### 功能使用
- [LLM_WITHOUT_3DS_GUIDE.md](LLM_WITHOUT_3DS_GUIDE.md)
  - 风险评分计算
  - 阈值配置
  - 交易组合示例
  - 测试方法

### 环境配置
- [SETUP.md](SETUP.md)
  - 环境要求
  - 依赖安装
  - 配置文件
  - 启动步骤

## 📝 文档维护

### 更新文档
当功能更新时，请相应更新相关文档：
1. 更新代码示例
2. 添加新功能说明
3. 更新配置说明
4. 添加故障排查条目

### 文档规范
- 使用清晰的标题结构
- 提供代码示例
- 包含实际输出示例
- 添加故障排查部分
- 保持语言一致性

## 🔗 相关资源

### 项目文档
- [../README.md](../README.md) - 项目主文档
- [../tests/README.md](../tests/README.md) - 测试文档

### 外部资源
- [FastAPI文档](https://fastapi.tiangolo.com/)
- [OpenAI API文档](https://platform.openai.com/docs)
- [DeepSeek平台](https://platform.deepseek.com/)

## 📈 文档改进

### 计划改进
- [ ] 添加API端点详细文档
- [ ] 创建架构图
- [ ] 添加性能调优指南
- [ ] 编写部署指南
- [ ] 创建故障排查手册

### 贡献指南
欢迎改进文档！请：
1. Fork项目
2. 创建文档改进分支
3. 更新相关文档
4. 提交Pull Request

## 📞 获取帮助

如果文档不清晰或需要更多信息：
1. 查看相关文档的故障排查部分
2. 检查项目主文档 [../README.md](../README.md)
3. 查看测试示例 [../tests/](../tests/)
4. 创建Issue提出问题

## 📋 文档检查清单

- [ ] 所有链接有效
- [ ] 代码示例可运行
- [ ] 配置说明准确
- [ ] 故障排查实用
- [ ] 语言清晰易懂
- [ ] 结构逻辑合理

---

**最后更新：** 2026-02-15  
**维护者：** Smart Payment Checkout Team