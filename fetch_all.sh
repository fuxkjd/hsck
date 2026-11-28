#!/bin/bash
echo "正在获取所有远程分支信息..."
git fetch --all
if [ $? -ne 0 ]; then
    echo "获取远程分支信息时出错。"
    exit 1
fi
echo "正在强制重置本地 main 分支到远程 main 分支..."
git reset --hard origin/main
if [ $? -ne 0 ]; then
    echo "重置本地分支时出错。"
    exit 1
fi
echo "本地 main 分支已成功更新为远程 main 分支的状态。"    
