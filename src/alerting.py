#!/usr/bin/env python3
"""
Alert management system for infrastructure monitoring.
Creates and manages alert rules across monitoring platforms.
"""

import argparse
import yaml
import logging
from typing import Dict, List, Any
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AlertManager:
    """Manage monitoring alerts and notifications."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.alert_config = config.get('alerts', {})
        self.notification_channels = config.get('notification_channels', {})
    
    def create_alert_rules(self) -> List[Dict]:
        """Create alert rules based on configuration."""
        rules = []
        
        # CPU utilization alert
        rules.append({
            'name': 'high_cpu_utilization',
            'condition': f"cpu_utilization > {self.alert_config.get('cpu_threshold', 80)}",
            'duration': '5m',
            'severity': 'warning',
            'message': 'CPU utilization is above threshold',
            'annotations': {
                'description': 'Instance {{$labels.resource_id}} has CPU > {{$value}}%'
            }
        })
        
        # Memory utilization alert
        rules.append({
            'name': 'high_memory_utilization',
            'condition': f"memory_utilization > {self.alert_config.get('memory_threshold', 85)}",
            'duration': '5m',
            'severity': 'warning',
            'message': 'Memory utilization is above threshold'
        })
        
        # Disk utilization alert
        rules.append({
            'name': 'high_disk_utilization',
            'condition': f"disk_utilization > {self.alert_config.get('disk_threshold', 90)}",
            'duration': '10m',
            'severity': 'critical',
            'message': 'Disk space is critically low'
        })
        
        # Instance state change alert
        rules.append({
            'name': 'instance_state_change',
            'condition': 'changes(instance_state[5m]) > 0',
            'duration': '1m',
            'severity': 'info',
            'message': 'Instance state has changed'
        })
        
        # Cost anomaly alert
        rules.append({
            'name': 'cost_anomaly',
            'condition': 'rate(cloud_cost[1h]) > 1.5 * rate(cloud_cost[24h] offset 1d)',
            'duration': '1h',
            'severity': 'warning',
            'message': 'Cloud costs are increasing abnormally'
        })
        
        return rules
    
    def generate_prometheus_rules(self) -> Dict:
        """Generate Prometheus alert rules format."""
        rules = self.create_alert_rules()
        
        prometheus_rules = {
            'groups': [{
                'name': 'cloud_infrastructure_alerts',
                'interval': '30s',
                'rules': []
            }]
        }
        
        for rule in rules:
            prom_rule = {
                'alert': rule['name'],
                'expr': rule['condition'],
                'for': rule['duration'],
                'labels': {
                    'severity': rule['severity']
                },
                'annotations': {
                    'summary': rule['message'],
                    **rule.get('annotations', {})
                }
            }
            prometheus_rules['groups'][0]['rules'].append(prom_rule)
        
        return prometheus_rules
    
    def generate_grafana_alerts(self) -> List[Dict]:
        """Generate Grafana alert definitions."""
        rules = self.create_alert_rules()
        grafana_alerts = []
        
        for rule in rules:
            alert = {
                'name': rule['name'],
                'message': rule['message'],
                'conditions': [{
                    'type': 'query',
                    'query': {'query': rule['condition']}
                }],
                'frequency': '1m',
                'handler': 1,
                'notifications': self._get_notification_ids()
            }
            grafana_alerts.append(alert)
        
        return grafana_alerts
    
    def _get_notification_ids(self) -> List[int]:
        """Get notification channel IDs."""
        # In production, this would fetch actual channel IDs
        return [1]  # Default channel
    
    def export_rules(self, format: str, output_path: str):
        """Export alert rules to file."""
        if format == 'prometheus':
            rules = self.generate_prometheus_rules()
        elif format == 'grafana':
            rules = self.generate_grafana_alerts()
        else:
            rules = self.create_alert_rules()
        
        try:
            with open(output_path, 'w') as f:
                yaml.dump(rules, f, default_flow_style=False)
            logger.info(f"Alert rules exported to {output_path}")
        except Exception as e:
            logger.error(f"Failed to export rules: {e}")
    
    def check_thresholds(self, metrics: List[Dict]) -> List[Dict]:
        """Check metrics against alert thresholds."""
        alerts = []
        
        for metric in metrics:
            if 'cpu_utilization' in metric:
                if metric['cpu_utilization'] > self.alert_config.get('cpu_threshold', 80):
                    alerts.append({
                        'alert': 'high_cpu_utilization',
                        'resource': metric['resource_id'],
                        'value': metric['cpu_utilization'],
                        'severity': 'warning'
                    })
        
        return alerts


def main():
    parser = argparse.ArgumentParser(description='Alert Management')
    parser.add_argument('--config', default='config/config.yaml', help='Config file path')
    parser.add_argument('--create-rules', action='store_true', help='Create alert rules')
    parser.add_argument('--export', choices=['prometheus', 'grafana'], help='Export format')
    parser.add_argument('--output', default='alerts/rules.yaml', help='Output file path')
    args = parser.parse_args()
    
    try:
        with open(args.config, 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        logger.error(f"Config file not found: {args.config}")
        return
    
    alert_mgr = AlertManager(config)
    
    if args.create_rules:
        rules = alert_mgr.create_alert_rules()
        print(f"\nCreated {len(rules)} alert rules:")
        for rule in rules:
            print(f"  - {rule['name']}: {rule['message']}")
    
    if args.export:
        alert_mgr.export_rules(args.export, args.output)


if __name__ == '__main__':
    main()