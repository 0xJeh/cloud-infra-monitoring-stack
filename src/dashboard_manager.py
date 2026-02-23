#!/usr/bin/env python3
"""
Dashboard management for Grafana and Kibana.
Automatically creates and updates monitoring dashboards.
"""

import argparse
import yaml
import logging
import json
from typing import Dict, Any
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class GrafanaDashboardManager:
    """Manage Grafana dashboards via API."""
    
    def __init__(self, config: Dict[str, Any]):
        self.host = config.get('host', 'localhost')
        self.port = config.get('port', 3000)
        self.api_key = config.get('api_key', '')
        self.base_url = f"http://{self.host}:{self.port}/api"
        self.headers = {'Authorization': f'Bearer {self.api_key}', 'Content-Type': 'application/json'}
    
    def create_cloud_monitoring_dashboard(self) -> Dict:
        """Create a comprehensive cloud monitoring dashboard."""
        dashboard = {
            "dashboard": {
                "title": "Cloud Infrastructure Monitoring",
                "tags": ["cloud", "infrastructure", "multi-cloud"],
                "timezone": "browser",
                "panels": [
                    {
                        "id": 1,
                        "title": "CPU Utilization by Region",
                        "type": "graph",
                        "gridPos": {"x": 0, "y": 0, "w": 12, "h": 8},
                        "targets": [{
                            "expr": "avg(cloud_cpu_utilization) by (region)",
                            "legendFormat": "{{region}}"
                        }]
                    },
                    {
                        "id": 2,
                        "title": "Active Instances by Provider",
                        "type": "stat",
                        "gridPos": {"x": 12, "y": 0, "w": 6, "h": 4},
                        "targets": [{
                            "expr": "count(cloud_instance_state{state='running'}) by (cloud_provider)"
                        }]
                    },
                    {
                        "id": 3,
                        "title": "Memory Usage",
                        "type": "graph",
                        "gridPos": {"x": 0, "y": 8, "w": 12, "h": 8},
                        "targets": [{
                            "expr": "cloud_memory_utilization"
                        }]
                    },
                    {
                        "id": 4,
                        "title": "Alert Status",
                        "type": "table",
                        "gridPos": {"x": 12, "y": 4, "w": 12, "h": 8},
                        "targets": [{
                            "expr": "ALERTS{alertstate='firing'}"
                        }]
                    }
                ],
                "refresh": "30s"
            },
            "overwrite": True
        }
        
        return dashboard
    
    def create_dashboard(self) -> bool:
        """Create the dashboard in Grafana."""
        try:
            dashboard_data = self.create_cloud_monitoring_dashboard()
            response = requests.post(
                f"{self.base_url}/dashboards/db",
                headers=self.headers,
                json=dashboard_data
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Dashboard created: {result.get('url')}")
                return True
            else:
                logger.error(f"Failed to create dashboard: {response.text}")
                return False
        
        except Exception as e:
            logger.error(f"Error creating Grafana dashboard: {e}")
            return False
    
    def export_dashboard(self, uid: str, output_path: str):
        """Export dashboard to JSON file."""
        try:
            response = requests.get(
                f"{self.base_url}/dashboards/uid/{uid}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                with open(output_path, 'w') as f:
                    json.dump(response.json(), f, indent=2)
                logger.info(f"Dashboard exported to {output_path}")
            else:
                logger.error(f"Failed to export dashboard: {response.text}")
        
        except Exception as e:
            logger.error(f"Error exporting dashboard: {e}")


class KibanaDashboardManager:
    """Manage Kibana dashboards and visualizations."""
    
    def __init__(self, config: Dict[str, Any]):
        self.host = config.get('host', 'localhost')
        self.port = config.get('port', 5601)
        self.base_url = f"http://{self.host}:{self.port}/api"
    
    def create_index_pattern(self):
        """Create index pattern for cloud metrics."""
        index_pattern = {
            "attributes": {
                "title": "cloud-metrics-*",
                "timeFieldName": "timestamp"
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/saved_objects/index-pattern/cloud-metrics",
                headers={'kbn-xsrf': 'true', 'Content-Type': 'application/json'},
                json=index_pattern
            )
            
            if response.status_code == 200:
                logger.info("Kibana index pattern created")
                return True
            else:
                logger.warning(f"Index pattern creation response: {response.text}")
                return False
        
        except Exception as e:
            logger.error(f"Error creating Kibana index pattern: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description='Dashboard Manager')
    parser.add_argument('--config', default='config/config.yaml', help='Config file path')
    parser.add_argument('--create', action='store_true', help='Create dashboards')
    parser.add_argument('--export', help='Export dashboard (grafana/kibana)')
    args = parser.parse_args()
    
    try:
        with open(args.config, 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        logger.error(f"Config file not found: {args.config}")
        return
    
    if args.create:
        grafana_mgr = GrafanaDashboardManager(config.get('grafana', {}))
        grafana_mgr.create_dashboard()
        
        kibana_mgr = KibanaDashboardManager(config.get('kibana', {}))
        kibana_mgr.create_index_pattern()
    
    if args.export:
        grafana_mgr = GrafanaDashboardManager(config.get('grafana', {}))
        grafana_mgr.export_dashboard('cloud-monitoring', f'dashboards/{args.export}.json')


if __name__ == '__main__':
    main()