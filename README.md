# Cloud Infrastructure Monitoring Stack

A comprehensive infrastructure monitoring and log aggregation solution showcasing integrations with Elasticsearch, Kibana, Grafana, and Datadog across multi-cloud environments (AWS/Azure/GCP).

## Features

- **Multi-cloud Support**: Monitor resources across AWS, Azure, and GCP
- **Log Aggregation**: Centralized logging with Elasticsearch
- **Custom Dashboards**: Automated dashboard creation for Grafana and Kibana
- **Alert Management**: Configurable alerting rules with multiple notification channels
- **Docker & Kubernetes**: Production-ready deployment configurations
- **Metrics Export**: Export cloud metrics to monitoring platforms

## Architecture

```
Cloud Providers (AWS/Azure/GCP)
        |
        v
  Metrics Collector
        |
        +---> Elasticsearch (Logs)
        +---> Grafana (Visualizations)
        +---> Datadog (APM)
```

## Prerequisites

- Python 3.8+
- Docker & Docker Compose
- Cloud provider credentials (AWS/Azure/GCP)
- Datadog API key (optional)

## Quick Start

1. **Clone and install dependencies:**
```bash
git clone https://github.com/yourusername/cloud-infra-monitoring-stack.git
cd cloud-infra-monitoring-stack
pip install -r requirements.txt
```

2. **Configure credentials:**
```bash
cp config/config.example.yaml config/config.yaml
# Edit config.yaml with your credentials
```

3. **Start monitoring stack with Docker:**
```bash
docker-compose up -d
```

4. **Run metrics collector:**
```bash
python src/collector.py --config config/config.yaml
```

5. **Access dashboards:**
- Kibana: http://localhost:5601
- Grafana: http://localhost:3000 (admin/admin)

## Configuration

Edit `config/config.yaml`:

```yaml
cloud_providers:
  aws:
    enabled: true
    regions: [us-east-1, us-west-2]
  azure:
    enabled: false
  gcp:
    enabled: false

elasticsearch:
  host: localhost
  port: 9200

grafana:
  host: localhost
  port: 3000
  api_key: your-api-key

alerts:
  cpu_threshold: 80
  memory_threshold: 85
  disk_threshold: 90
```

## Usage Examples

**Collect metrics manually:**
```bash
python src/collector.py --provider aws --region us-east-1
```

**Setup alerts:**
```bash
python src/alerting.py --create-rules
```

**Export dashboards:**
```bash
python src/dashboard_manager.py --export grafana
```

## Project Structure

```
├── src/
│   ├── collector.py          # Multi-cloud metrics collector
│   ├── dashboard_manager.py  # Dashboard creation/management
│   ├── alerting.py          # Alert rule management
│   └── exporters.py         # Export to monitoring platforms
├── config/
│   └── config.example.yaml  # Configuration template
├── dashboards/              # Pre-built dashboard definitions
├── docker-compose.yml       # Container orchestration
└── kubernetes/              # K8s deployment manifests
```

## License

MIT License