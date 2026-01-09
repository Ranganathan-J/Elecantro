# Build Base Docker Image Script (PowerShell)
# Usage: .\build-base.ps1 [tag]

param(
    [string]$Tag = "elecantro/base:latest"
)

Write-Host "🔨 Building base Docker image: $Tag" -ForegroundColor Green
Write-Host "📦 This will install all dependencies from requirements.txt" -ForegroundColor Yellow

docker build -f docker/base.Dockerfile -t $Tag .

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Base image built successfully!" -ForegroundColor Green
    Write-Host "🏷️  Tag: $Tag" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📋 Usage in other Dockerfiles:" -ForegroundColor Yellow
    Write-Host "FROM $Tag" -ForegroundColor White
    Write-Host ""
    Write-Host "🔄 To rebuild when requirements.txt changes:" -ForegroundColor Yellow
    Write-Host ".\build-base.ps1" -ForegroundColor White
} else {
    Write-Host "❌ Failed to build base image" -ForegroundColor Red
    exit 1
}
