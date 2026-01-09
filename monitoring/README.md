# Prometheus Monitoring Setup

This document explains the Prometheus monitoring configuration for the Elecantro application.

## Services and Ports

| Service | Port | Description |
|----------|-------|-------------|
| Prometheus | 9090 | Main monitoring server |
| Node Exporter | 9100 | System metrics (CPU, memory, disk) |
| Redis Exporter | 9121 | Redis database metrics |
| PostgreSQL Exporter | 9187 | PostgreSQL database metrics |
| Redis Commander | 8081 | Redis management interface |

## Access URLs

- **Prometheus Web UI**: http://localhost:9090
- **Redis Commander**: http://localhost:8081

## Configuration Files

### prometheus.yml
- Main Prometheus configuration
- Defines scrape targets and intervals
- Includes alerting rules

### prometheus-rules.yml
- Alerting rules for system monitoring
- Includes alerts for:
  - Backend downtime
  - High error rates
  - Database connectivity issues
  - Resource usage (CPU, memory, disk)
  - Application-specific metrics

## Key Metrics Monitored

### Backend Metrics
- HTTP request rates and response times
- Error rates by status code
- File upload success/failure rates
- Authentication failures

### System Metrics
- CPU usage
- Memory usage
- Disk space
- Network I/O

### Database Metrics
- Connection counts
- Query performance
- Database size

### Redis Metrics
- Memory usage
- Connection counts
- Operations per second

## Alerting

The system includes comprehensive alerting rules that will trigger when:
- Backend service is down
- Error rates exceed thresholds
- Database connections fail
- System resources are critically low
- Disk space is running out

## Usage

1. **Start monitoring**:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

2. **View metrics**: Open http://localhost:9090

3. **Check targets**: Go to Status → Targets in Prometheus UI

4. **View alerts**: Go to Alerts tab in Prometheus UI

## Log Monitoring

Prometheus collects logs through:
- Application metrics from `/metrics` endpoint
- Health check status from `/health` endpoint
- System logs via exporters

## Data Retention

- Metrics are retained for 200 hours (≈8 days)
- Data is stored in `prometheus_data` volume

## Troubleshooting

### Common Issues

1. **Targets not showing up**:
   - Check if exporters are running: `docker ps`
   - Verify network connectivity between containers

2. **No metrics from backend**:
   - Ensure backend is running and accessible
   - Check `/metrics` endpoint is responding

3. **High memory usage**:
   - Reduce retention time in prometheus.yml
   - Add more disk space for metrics storage

### Restart Services

```bash
# Restart all monitoring services
docker-compose -f docker-compose.prod.yml restart prometheus node-exporter redis-exporter postgres-exporter

# View logs
docker-compose -f docker-compose.prod.yml logs prometheus
```

## Scaling Considerations

- For production, consider:
  - Adding Alertmanager for alert routing
  - Implementing log aggregation with Loki
  - Adding Grafana for dashboards (if needed)
  - Setting up remote write for long-term storage
