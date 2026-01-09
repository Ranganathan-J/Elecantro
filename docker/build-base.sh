#!/bin/bash

# Build Base Docker Image Script
# Usage: ./build-base.sh [tag]

TAG=${1:-"elecantro/base:latest"}

echo "🔨 Building base Docker image: $TAG"
echo "📦 This will install all dependencies from requirements.txt"

docker build -f docker/base.Dockerfile -t $TAG .

if [ $? -eq 0 ]; then
    echo "✅ Base image built successfully!"
    echo "🏷️  Tag: $TAG"
    echo ""
    echo "📋 Usage in other Dockerfiles:"
    echo "FROM $TAG"
    echo ""
    echo "🔄 To rebuild when requirements.txt changes:"
    echo "./build-base.sh"
else
    echo "❌ Failed to build base image"
    exit 1
fi
