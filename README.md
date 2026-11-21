# hsck

海阔小程序离线数据源采集工具。

## 功能

- 自动采集视频数据并生成离线 JSON/TXT/M3U 文件
- 支持多种视频分类
- 缓存媒体文件避免重复下载
- 微信推送更新通知（HTML 富文本，含成功/失败明细）
- 生成独立单文件 HTML 视频站（all.html），可直接用浏览器打开

## 直播订阅

### m3u 格式
[https://raw.githubusercontent.com/fuxkjd/hsck/main/dist/all.m3u](https://raw.githubusercontent.com/fuxkjd/hsck/main/dist/all.m3u)
### m3u 格式(代理)
[https://fastly.jsdelivr.net/gh/fuxkjd/hsck@main/dist/all.m3u](https://fastly.jsdelivr.net/gh/fuxkjd/hsck@main/dist/all.m3u)
### txt 格式
[https://raw.githubusercontent.com/fuxkjd/hsck/main/dist/all.txt](https://raw.githubusercontent.com/fuxkjd/hsck/main/dist/all.txt)
### txt 格式(代理)
[https://fastly.jsdelivr.net/gh/fuxkjd/hsck@main/dist/all.txt](https://fastly.jsdelivr.net/gh/fuxkjd/hsck@main/dist/all.txt)

## HTML 视频站

单文件离线视频站，全部视频数据内置在 `dist/all.html` 中，可直接用浏览器打开（`file://`）。

- 视频分类、列表、搜索、翻页
- 自动 / 浅色 / 深色 三主题（默认跟随系统）
- 播放器支持网页全屏、系统全屏与倍速（0.5 / 0.75 / 1 / 1.25 / 1.5 / 2 / 3x）
- 卡片封面显示更新时间（uptime）徽标，分类模式下标题处显示 uptime
- 仅依赖 CDN 框架（Vue3 / hls.js），不含任何本地 js/css；视频与缩略图需联网加载

### 在线预览（GitHub Pages）
[https://fuxkjd.github.io/hsck/dist/all.html](https://fuxkjd.github.io/hsck/dist/all.html)

### 源码
- 源码：[https://raw.githubusercontent.com/fuxkjd/hsck/main/dist/all.html](https://raw.githubusercontent.com/fuxkjd/hsck/main/dist/all.html)
- jsDelivr 代理：[https://cdn.jsdelivr.net/gh/fuxkjd/hsck@main/dist/all.html](https://cdn.jsdelivr.net/gh/fuxkjd/hsck@main/dist/all.html)

## 快速开始

### 本地运行

```bash
# 安装依赖
uv sync

# 创建 .env 文件
echo "WXPUSHER_APPTOKEN=your_token" > .env

# 运行（三种方式等价）
uv run python -m hsck
uv run hsck
uv run python -c "from hsck.app import main; main()"
```

### GitHub Actions

推送后自动定时执行（每天 10:30 和 22:30），配置 `WXPUSHER_APPTOKEN` Secrets 即可接收推送通知。

## 目录结构

```
.
├── pyproject.toml          # 项目配置与依赖
├── src/
│   └── hsck/               # 主包
│       ├── __init__.py
│       ├── __main__.py     # python -m hsck 入口
│       ├── app.py          # App 入口类
│       ├── config.py       # 配置管理器（内存缓存）
│       ├── generator.py    # 分发文件生成器
│       ├── html_template.py # 独立 HTML 视频站模板
│       ├── http_client.py  # HTTP 客户端（httpx）
│       ├── logger.py       # 日志模块
│       ├── models.py       # 数据模型
│       ├── notifier.py     # 微信推送
│       ├── storage.py      # 视频数据持久化
│       ├── utils.py        # 工具函数
│       └── scraper/
│           ├── captcha.py       # 滑块验证解决器
│           ├── host_checker.py  # 主机检测
│           └── video_scraper.py # 视频采集器
├── media/                  # 视频数据缓存
├── dist/                   # 生成的发布文件
└── .github/workflows/      # GitHub Actions
```

## 环境变量

| 变量 | 说明 |
|------|------|
| `WXPUSHER_APPTOKEN` | 微信推送 Token |

## 开发

```bash
# 安装 ruff
uv sync --group dev

# 代码检查
ruff check src/

# 代码格式化
ruff format src/
```
