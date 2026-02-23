#!/usr/bin/env python3
"""
Exporters for sending metrics to various monitoring platforms.
"""

import logging
from typing import Dict, List, Any
from datetime import datetime
import json

try:
    from elasticsearch import Elasticsearch
except ImportError:
    Elasticsearch = None

try:
    from datadog import initialize, api
except ImportError:
    api = None

logger = logging.getLogger(__name__)


class ElasticsearchExporter:
    """Export metrics to Elasticsearch for log aggregation."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get('enabled', True)
        self.index_pattern = 'cloud-metrics'
        
        if self.enabled and Elasticsearch:
            try:
                self.client = Elasticsearch(
                    [f"{config.get('host', 'localhost')}:{config.get('port', 9200)}"]
                )
                logger.info("Elasticsearch exporter initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Elasticsearch: {e}")
                self.enabled = False
        else:
            self.enabled = False
            if not Elasticsearch:
                logger.warning("Elasticsearch not installed. Install with: pip install elasticsearch")
    
    def export(self, metrics: List[Dict]):
        """Export metrics to Elasticsearch."""
        if not self.enabled:
            logger.debug("Elasticsearch export disabled")
            return
        
        try:
            for metric in metrics:
                index_name = f"{self.index_pattern}-{datetime.utcnow().strftime('%Y.%m.%d')}"
                self.client.index(index=index_name, document=metric)
            
            logger.info(f"Exported {len(metrics)} metrics to Elasticsearch")
        except Exception as e:
            logger.error(f"Failed to export to Elasticsearch: {e}")


class DatadogExporter:
    """Export metrics to Datadog."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get('enabled', False)
        
        if self.enabled and api:
            try:
                initialize(
                    api_key=config.get('api_key'),
                    app_key=config.get('app_key')
                )
                logger.info("Datadog exporter initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Datadog: {e}")
                self.enabled = False
        else:
            self.enabled = False
            if not api:
                logger.warning("Datadog not installed. Install with: pip install datadog")
    
    def export(self, metrics: List[Dict]):
        """Export metrics to Datadog."""
        if not self.enabled:
            logger.debug("Datadog export disabled")
            return
        
        try:
            datadog_metrics = []
            
            for metric in metrics:
                if 'cpu_utilization' in metric:
                    datadog_metrics.append({
                        'metric': 'cloud.cpu.utilization',
                        'points': [(int(datetime.utcnow().timestamp()), metric['cpu_utilization'])],
                        'tags': [
                            f"provider:{metric['cloud_provider']}",
                            f"region:{metric['region']}",
                            f"resource:{metric['resource_id']}"
                        ]
                    })
            
            if datadog_metrics:
                api.Metric.send(datadog_metrics)
                logger.info(f"Exported {len(datadog_metrics)} metrics to Datadog")
        
        except Exception as e:
            logger.error(f"Failed to export to Datadog: {e}")


class GrafanaExporter:
    """Export metrics to Grafana (via Prometheus or direct API)."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get('enabled', False)
        logger.info("Grafana exporter initialized (placeholder)")
    
    def export(self, metrics: List[Dict]):
        """Export metrics to Grafana."""
        if not self.enabled:
            return
        
        # In production, this would push to Prometheus or use Grafana's API
        logger.debug(f"Would export {len(metrics)} metrics to Grafana")