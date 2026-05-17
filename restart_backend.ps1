# 关闭占用8000端口的进程
$connections = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($connections) {
    $pids = $connections | Select-Object -ExpandProperty OwningProcess -Unique
    foreach ($pid in $pids) {
        try {
            Stop-Process -Id $pid -Force -ErrorAction Stop
            Write-Host "已终止进程 PID: $pid"
        } catch {
            Write-Host "无法终止进程 PID: $pid"
        }
    }
}

Start-Sleep -Seconds 2

# 设置环境变量并启动后端
$env:DEEPSEEK_API_KEY = "sk-682d222860a24ef1a66e95b1c51c8362"
$env:PYTHONPATH = "D:\PrismaMate专用文件夹\prismamate-backend"

cd D:\PrismaMate专用文件夹\prismamate-backend

# 启动后端（后台运行）
Start-Process -FilePath ".\venv\Scripts\python.exe" -ArgumentList "-m", "uvicorn", "app.main:app", "--reload", "--port", "8000" -WindowStyle Hidden

Write-Host "后端已重启在端口 8000"
