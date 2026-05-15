#!/usr/bin/env pwsh
# ============================================================
# PrismaMate 棱镜 - 前端启动脚本 (Windows PowerShell)
# ============================================================
# 用法:
#   开发模式: .\start_frontend.ps1 -Mode dev
#   预览模式: .\start_frontend.ps1 -Mode preview
# ============================================================

param(
    [ValidateSet("dev", "preview")]
    [string]$Mode = "dev"
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PrismaMate 棱镜 - 前端启动" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 获取脚本目录
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# 检查 Node.js
try {
    $nodeVersion = node --version
    Write-Host "Node.js 版本: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "错误: 未安装 Node.js，请先安装 Node.js 24+" -ForegroundColor Red
    exit 1
}

# 检查依赖
if (-not (Test-Path "node_modules")) {
    Write-Host "正在安装依赖..." -ForegroundColor Yellow
    npm install
}

switch ($Mode) {
    "dev" {
        Write-Host ""
        Write-Host "启动开发服务器..." -ForegroundColor Green
        Write-Host "访问地址: http://localhost:3000" -ForegroundColor Cyan
        Write-Host "按 Ctrl+C 停止服务" -ForegroundColor Yellow
        Write-Host ""
        npm run dev
    }
    "preview" {
        Write-Host ""
        Write-Host "构建生产版本并预览..." -ForegroundColor Green
        npm run build
        npm run preview
    }
}
