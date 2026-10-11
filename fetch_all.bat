:: 设置 UTF-8 编码
chcp 65001
@echo off
echo 正在获取所有远程分支信息...
git fetch --all
if %errorlevel% neq 0 (
    echo 获取远程分支信息时出错。
    pause
    exit /b %errorlevel%
)
echo 正在强制重置本地 main 分支到远程 main 分支...
git reset --hard origin/main
if %errorlevel% neq 0 (
    echo 重置本地分支时出错。
    pause
    exit /b %errorlevel%
)
echo 本地 main 分支已成功更新为远程 main 分支的状态。
