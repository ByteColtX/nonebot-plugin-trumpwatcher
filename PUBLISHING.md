# 发布到 NoneBot2 插件市场指南

## 📋 发布前检查清单

### ✅ 已完成项

- [x] 项目结构符合 NoneBot2 规范
- [x] `__plugin_meta__` 元数据完整（包含 homepage）
- [x] 使用 `require()` 声明插件依赖
- [x] 使用异步操作（httpx.AsyncClient）
- [x] README 包含 nb-cli 安装说明
- [x] pyproject.toml 配置完整
- [x] 依赖版本使用 `>=` 或 `^`（不使用 `==`）

### 📝 需要修改的内容

在发布前,请修改以下占位符:

1. **pyproject.toml** 中的邮箱地址（如果需要）:
   ```toml
   authors = ["StuGRua <stugd@example.com>"]
   ```
   将 `stugd@example.com` 替换为你的真实邮箱

## 🚀 发布步骤

### 1. 创建 GitHub 仓库

```bash
cd F:/py/zx2/nonebot-plugin-trumpwatcher
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/StuGRua/nonebot-plugin-trumpwatcher.git
git push -u origin master
```

### 2. 构建并发布到 PyPI

使用 Poetry 构建和发布:

```bash
# 安装 Poetry（如果还没有）
pip install poetry

# 构建包
poetry build

# 发布到 PyPI（需要先注册 PyPI 账号）
poetry publish
```

或使用 PDM:

```bash
# 安装 PDM
pip install pdm

# 构建包
pdm build

# 发布到 PyPI
pdm publish
```

### 3. 提交到 NoneBot2 插件市场

1. 访问 [NoneBot 商店](https://nonebot.dev/store)
2. 点击"发布插件"按钮
3. 填写插件信息:
   - **PyPI 包名**: `nonebot-plugin-trumpwatcher`
   - **模块名**: `nonebot_plugin_trumpwatcher`
   - **项目链接**: 你的 GitHub 仓库地址

4. 提交后,NoneFlow Bot 会自动验证:
   - 插件能否正确加载
   - 元数据是否正确定义
   - 依赖是否有效

5. 通过验证后,等待社区审核
6. 审核通过后自动合并到插件市场

## 🔍 验证规范

发布前可以本地验证:

```bash
# 安装插件到测试环境
pip install -e .

# 检查插件能否正确加载
nb plugin list

# 运行测试（如果有）
pytest
```

## 📚 参考文档

- [NoneBot2 插件发布指南](https://nonebot.dev/docs/next/developer/plugin-publishing)
- [Poetry 文档](https://python-poetry.org/docs/)
- [PyPI 发布指南](https://packaging.python.org/tutorials/packaging-projects/)

## ⚠️ 注意事项

1. **版本号管理**: 遵循语义化版本规范（SemVer）
2. **依赖版本**: 不要使用 `==` 锁定单一版本
3. **零配置加载**: 插件应该能在不配置的情况下加载（即使部分功能需要配置才能使用）
4. **异步操作**: 禁止使用同步阻塞操作（如 `requests.get()`）
5. **文档完整性**: README 必须包含功能说明、安装方式、配置选项和使用说明

## 🎯 发布后

发布成功后,插件将出现在:
- [NoneBot 商店](https://nonebot.dev/store)
- [PyPI](https://pypi.org/project/nonebot-plugin-trumpwatcher/)

用户可以通过以下方式安装:
```bash
nb plugin install nonebot-plugin-trumpwatcher
```
