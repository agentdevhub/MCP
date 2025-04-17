# 参与 Model Context Protocol 贡献指南

感谢您有意为 Model Context Protocol 规范贡献力量！
本文档将说明如何参与本项目贡献。

## 环境准备

开发本规范需要以下软件环境：

- Node.js 20 或更高版本
- TypeScript
- TypeScript JSON Schema（用于生成 JSON 模式）
- [Mintlify](https://mintlify.com/)（可选，文档工具）
- nvm（可选，Node 版本管理工具）

## 快速开始

1. Fork 代码仓库
2. 克隆你的 Fork 仓库：

```bash
git clone https://github.com/YOUR-USERNAME/specification.git
cd specification
```

3. 安装依赖项：

```bash
nvm install  # install correct Node version
npm install  # install dependencies
```

## 修改规范

请注意所有模式变更都应修改 `schema.ts`。`schema.json` 是通过 `npm run validate:schema` 从 `schema.ts` 自动生成的。

1. 创建新分支：

```bash
git checkout -b feature/your-feature-name
```

2. 进行修改
3. 验证修改内容：

```bash
npm run validate:schema    # validate schema
npm run generate:json     # generate JSON schema
```

4. 本地运行文档（可选）：

```bash
npm run serve:docs
```

### 文档编写规范

贡献文档时请遵循：

- 保持内容清晰、简洁且技术准确
- 遵循现有文件结构和命名约定
- 适当位置包含代码示例
- 使用标准 MDX 格式和组件
- 测试所有链接和代码示例
- 教程类文档使用标准标题结构："使用场景"、"操作步骤"和"技巧提示"
- 新文档页需放入对应分类（概念、教程等）
- 新增页面时更新 docs.json
- 遵循文件命名规范（kebab-case.mdx）
- MDX 文件中需包含完整 frontmatter 元数据

## 提交修改

1. 将修改推送到你的 Fork 仓库
2. 向主仓库提交 Pull Request
3. 按照 PR 模板填写信息
4. 等待代码审查

## 行为准则

本项目遵循贡献者行为准则，请查阅
[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) 文件。

## 问题咨询

如有疑问，请在仓库中创建 Issue。

## 许可协议

参与贡献即表示您同意按照 MIT 许可协议授权您的贡献内容。

## 安全政策

报告安全问题请参阅我们的[安全政策](SECURITY.md)。