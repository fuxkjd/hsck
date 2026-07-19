# AGENTS.md

## 项目

`hsck` — 从远程 API 采集视频数据，缓存 JSON 到 `media/`，生成离线 M3U/TXT 播放列表到 `dist/`。通过 GitHub Actions 每天运行两次，也支持本地运行。

## 命令

```bash
# 安装依赖（使用 uv，Python 3.12）
uv sync

# 运行
uv run python -m hsck

# 代码检查 + 格式化 + 类型检查（通过 check 入口一起运行）
uv run check
# 或单独运行：
ruff check src/
ruff format src/
ty check --error all src/hsck
```

没有测试。CI 只运行 `uv run python -m hsck`，然后提交变更的 `dist/`、`config.json`、`media/`。

## 关键注意事项

- `config.json` 和 `media/` 已被提交到仓库——它们作为持久化状态。爬虫根据已保存的计数计算增量来决定抓取内容。不要删除它们。
- `app.py:112` 中的 `main()` 将 `base_dir` 解析为 `Path(__file__).parent.parent.parent`（仓库根目录）。所有路径都相对于仓库根目录。
- `WXPUSHER_APPTOKEN` 环境变量在本地是可选的；token 为空时推送器不会发送任何内容。
- `dist/` 中的文件是公开的订阅地址；CI 会 force-push 到 `main` 分支。
- 开发依赖（`ruff`、`ty`）需要 `uv sync --group dev`。
- `uv.lock` 已被提交——请遵守它以保证可复现的安装。
