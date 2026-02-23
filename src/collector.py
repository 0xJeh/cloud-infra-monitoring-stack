#!/usr/bin/env python3
"""
Multi-cloud metrics collector for infrastructure monitoring.
Supports AWS, Azure, and GCP resource metrics collection.
"""

import argparse
import yaml
import logging
from datetime import datetime
from typing import Dict, List, Any
import json

try:
    import boto3
except ImportError:
    boto3 = None

from exporters import ElasticsearchExporter, DatadogExporter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CloudMetricsCollector:
    """Collect metrics from multiple cloud providers."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.es_exporter = ElasticsearchExporter(config.get('elasticsearch', {}))
        self.dd_exporter = DatadogExporter(config.get('datadog', {}))
    
    def collect_aws_metrics(self, regions: List[str]) -> List[Dict]:
        """Collect AWS EC2 and CloudWatch metrics."""
        if not boto3:
            logger.error("boto3 not installed. Install with: pip install boto3")
            return []
        
        metrics = []
        for region in regions:
            try:
                ec2 = boto3.client('ec2', region_name=region)
                cloudwatch = boto3.client('cloudwatch', region_name=region)
                
                instances = ec2.describe_instances()
                for reservation in instances['Reservations']:
                    for instance in reservation['Instances']:
                        instance_id = instance['InstanceId']
                        state = instance['State']['Name']
                        
                        metric = {
                            'timestamp': datetime.utcnow().isoformat(),
                            'cloud_provider': 'aws',
                            'region': region,
                            'resource_type': 'ec2_instance',
                            'resource_id': instance_id,
                            'state': state,
                            'instance_type': instance.get('InstanceType', 'unknown'),
                            'tags': {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                        }
                        
                        # Get CPU utilization from CloudWatch
                        try:
                            cpu_response = cloudwatch.get_metric_statistics(
                                Namespace='AWS/EC2',
                                MetricName='CPUUtilization',
                                Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                                StartTime=datetime.utcnow().replace(minute=0, second=0),
                                EndTime=datetime.utcnow(),
                                Period=3600,
                                Statistics=['Average']
                            )
                            if cpu_response['Datapoints']:
                                metric['cpu_utilization'] = cpu_response['Datapoints'][0]['Average']
                        except Exception as e:
                            logger.warning(f"Failed to get CPU metrics for {instance_id}: {e}")
                        
                        metrics.append(metric)
                        logger.info(f"Collected metrics for {instance_id} in {region}")
                
            except Exception as e:
                logger.error(f"Error collecting AWS metrics in {region}: {e}")
        
        return metrics
    
    def collect_azure_metrics(self) -> List[Dict]:
        """Placeholder for Azure metrics collection."""
        logger.info("Azure metrics collection not yet implemented")
        return []
    
    def collect_gcp_metrics(self) -> List[Dict]:
        """Placeholder for GCP metrics collection."""
        logger.info("GCP metrics collection not yet implemented")
        return []
    
    def collect_all(self) -> List[Dict]:
        """Collect metrics from all enabled cloud providers."""
        all_metrics = []
        
        providers = self.config.get('cloud_providers', {})
        
        if providers.get('aws', {}).get('enabled'):
            regions = providers['aws'].get('regions', ['us-east-1'])
            all_metrics.extend(self.collect_aws_metrics(regions))
        
        if providers.get('azure', {}).get('enabled'):
            all_metrics.extend(self.collect_azure_metrics())
        
        if providers.get('gcp', {}).get('enabled'):
            all_metrics.extend(self.collect_gcp_metrics())
        
        return all_metrics
    
    def export_metrics(self, metrics: List[Dict]):
        """Export collected metrics to configured destinations."""
        if metrics:
            self.es_exporter.export(metrics)
            self.dd_exporter.export(metrics)
            logger.info(f"Exported {len(metrics)} metrics")


def main():
    parser = argparse.ArgumentParser(description='Cloud Infrastructure Metrics Collector')
    parser.add_argument('--config', default='config/config.yaml', help='Config file path')
    parser.add_argument('--provider', choices=['aws', 'azure', 'gcp', 'all'], default='all')
    parser.add_argument('--region', help='Specific region to collect from')
    args = parser.parse_args()
    
    try:
        with open(args.config, 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        logger.error(f"Config file not found: {args.config}")
        return
    
    collector = CloudMetricsCollector(config)
    metrics = collector.collect_all()
    
    if metrics:
        collector.export_metrics(metrics)
        print(f"\nCollected {len(metrics)} metrics successfully")
    else:
        print("No metrics collected")


if __name__ == '__main__':
    main()