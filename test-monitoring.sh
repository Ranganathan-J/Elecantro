#!/bin/bash

echo "🔍 Testing Prometheus Monitoring Setup..."
echo

# Check if all services are running
echo "📊 Checking service status..."
docker-compose -f docker-compose.prod.yml ps

echo
echo "🌐 Testing endpoints..."
echo

# Test Prometheus
echo "Testing Prometheus (http://localhost:9090)..."
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {name: .labels.job, health: .health}' 2>/dev/null || echo "❌ Prometheus not accessible"

# Test Backend Metrics
echo "Testing Backend Metrics (http://localhost:8000/metrics)..."
curl -s http://localhost:8000/metrics | head -5 2>/dev/null || echo "❌ Backend metrics not accessible"

# Test Node Exporter
echo "Testing Node Exporter (http://localhost:9100/metrics)..."
curl -s http://localhost:9100/metrics | head -5 2>/dev/null || echo "❌ Node exporter not accessible"

# Test Redis Exporter  
echo "Testing Redis Exporter (http://localhost:9121/metrics)..."
curl -s http://localhost:9121/metrics | head -5 2>/dev/null || echo "❌ Redis exporter not accessible"

# Test PostgreSQL Exporter
echo "Testing PostgreSQL Exporter (http://localhost:9187/metrics)..."
curl -s http://localhost:9187/metrics | head -5 2>/dev/null || echo "❌ PostgreSQL exporter not accessible"

echo
echo "🎯 If all services show ✅, monitoring is working!"
echo "📈 Access Prometheus UI: http://localhost:9090"
echo "🔴 Access Redis Commander: http://localhost:8081"
