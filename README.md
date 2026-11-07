# hsck

海阔小程序离线数据源采集工具。

## 功能

- 自动采集视频数据并生成离线 JSON/TXT/M3U 文件
- 支持多种视频分类
- 缓存媒体文件避免重复下载
- 微信推送更新通知

## 直播订阅

### m3u 格式
[https://raw.githubusercontent.com/fuxkjd/hsck/main/dist/all.m3u](https://raw.githubusercontent.com/fuxkjd/hsck/main/dist/all.m3u)
### m3u 格式(代理)
[https://fastly.jsdelivr.net/gh/fuxkjd/hsck@main/dist/all.m3u](https://fastly.jsdelivr.net/gh/fuxkjd/hsck@main/dist/all.m3u)
### txt 格式
[https://raw.githubusercontent.com/fuxkjd/hsck/main/dist/all.txt](https://raw.githubusercontent.com/fuxkjd/hsck/main/dist/all.txt)
### txt 格式(代理)
[https://fastly.jsdelivr.net/gh/fuxkjd/hsck@main/dist/all.txt](https://fastly.jsdelivr.net/gh/fuxkjd/hsck@main/dist/all.txt)

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
