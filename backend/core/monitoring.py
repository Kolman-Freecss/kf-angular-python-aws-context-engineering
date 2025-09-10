import logging
import time
import psutil
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
from core.config import settings

logger = logging.getLogger(__name__)

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class Alert:
    id: str
    level: AlertLevel
    title: str
    message: str
    timestamp: datetime
    source: str
    metadata: Dict[str, Any]
    resolved: bool = False
    resolved_at: Optional[datetime] = None

@dataclass
class SystemMetrics:
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_available_mb: float
    disk_usage_percent: float
    disk_free_gb: float
    network_bytes_sent: int
    network_bytes_recv: int
    active_connections: int
    process_count: int

@dataclass
class ApplicationMetrics:
    timestamp: datetime
    request_count: int
    average_response_time: float
    error_rate: float
    active_users: int
    cache_hit_rate: float
    database_query_count: int
    database_avg_query_time: float

class MonitoringService:
    """Centralized monitoring and alerting service"""
    
    def __init__(self):
        self.alerts: List[Alert] = []
        self.system_metrics: List[SystemMetrics] = []
        self.application_metrics: List[ApplicationMetrics] = []
        self.alert_thresholds = self._get_default_thresholds()
        self.monitoring_active = False
        self.monitoring_task: Optional[asyncio.Task] = None
    
    def _get_default_thresholds(self) -> Dict[str, float]:
        """Get default monitoring thresholds"""
        return {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_usage_percent': 90.0,
            'response_time_ms': 1000.0,
            'error_rate_percent': 5.0,
            'cache_hit_rate_percent': 80.0,
            'database_query_time_ms': 500.0
        }
    
    async def start_monitoring(self, interval: int = 60):
        """Start continuous monitoring"""
        if self.monitoring_active:
            logger.warning("Monitoring is already active")
            return
        
        self.monitoring_active = True
        logger.info(f"Starting monitoring with {interval}s interval")
        
        self.monitoring_task = asyncio.create_task(
            self._monitoring_loop(interval)
        )
    
    async def stop_monitoring(self):
        """Stop continuous monitoring"""
        if not self.monitoring_active:
            return
        
        self.monitoring_active = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Monitoring stopped")
    
    async def _monitoring_loop(self, interval: int):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                await self._collect_metrics()
                await self._check_thresholds()
                await self._cleanup_old_data()
                
                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(interval)
    
    async def _collect_metrics(self):
        """Collect system and application metrics"""
        try:
            # Collect system metrics
            system_metrics = self._collect_system_metrics()
            self.system_metrics.append(system_metrics)
            
            # Collect application metrics
            app_metrics = self._collect_application_metrics()
            self.application_metrics.append(app_metrics)
            
            # Keep only last 1000 metrics to prevent memory issues
            if len(self.system_metrics) > 1000:
                self.system_metrics = self.system_metrics[-1000:]
            if len(self.application_metrics) > 1000:
                self.application_metrics = self.application_metrics[-1000:]
                
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
    
    def _collect_system_metrics(self) -> SystemMetrics:
        """Collect system-level metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_mb = memory.available / 1024 / 1024
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_usage_percent = (disk.used / disk.total) * 100
            disk_free_gb = disk.free / 1024 / 1024 / 1024
            
            # Network metrics
            network = psutil.net_io_counters()
            network_bytes_sent = network.bytes_sent
            network_bytes_recv = network.bytes_recv
            
            # Connection metrics
            connections = len(psutil.net_connections())
            process_count = len(psutil.pids())
            
            return SystemMetrics(
                timestamp=datetime.utcnow(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_available_mb=memory_available_mb,
                disk_usage_percent=disk_usage_percent,
                disk_free_gb=disk_free_gb,
                network_bytes_sent=network_bytes_sent,
                network_bytes_recv=network_bytes_recv,
                active_connections=connections,
                process_count=process_count
            )
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            # Return default metrics
            return SystemMetrics(
                timestamp=datetime.utcnow(),
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_available_mb=0.0,
                disk_usage_percent=0.0,
                disk_free_gb=0.0,
                network_bytes_sent=0,
                network_bytes_recv=0,
                active_connections=0,
                process_count=0
            )
    
    def _collect_application_metrics(self) -> ApplicationMetrics:
        """Collect application-level metrics"""
        try:
            # This would integrate with your performance middleware
            # For now, return default metrics
            return ApplicationMetrics(
                timestamp=datetime.utcnow(),
                request_count=0,
                average_response_time=0.0,
                error_rate=0.0,
                active_users=0,
                cache_hit_rate=0.0,
                database_query_count=0,
                database_avg_query_time=0.0
            )
        except Exception as e:
            logger.error(f"Error collecting application metrics: {e}")
            return ApplicationMetrics(
                timestamp=datetime.utcnow(),
                request_count=0,
                average_response_time=0.0,
                error_rate=0.0,
                active_users=0,
                cache_hit_rate=0.0,
                database_query_count=0,
                database_avg_query_time=0.0
            )
    
    async def _check_thresholds(self):
        """Check metrics against thresholds and create alerts"""
        if not self.system_metrics:
            return
        
        latest_system = self.system_metrics[-1]
        latest_app = self.application_metrics[-1] if self.application_metrics else None
        
        # Check CPU threshold
        if latest_system.cpu_percent > self.alert_thresholds['cpu_percent']:
            await self._create_alert(
                AlertLevel.WARNING,
                "High CPU Usage",
                f"CPU usage is {latest_system.cpu_percent:.1f}% (threshold: {self.alert_thresholds['cpu_percent']}%)",
                "system",
                {"cpu_percent": latest_system.cpu_percent}
            )
        
        # Check memory threshold
        if latest_system.memory_percent > self.alert_thresholds['memory_percent']:
            await self._create_alert(
                AlertLevel.WARNING,
                "High Memory Usage",
                f"Memory usage is {latest_system.memory_percent:.1f}% (threshold: {self.alert_thresholds['memory_percent']}%)",
                "system",
                {"memory_percent": latest_system.memory_percent}
            )
        
        # Check disk usage threshold
        if latest_system.disk_usage_percent > self.alert_thresholds['disk_usage_percent']:
            await self._create_alert(
                AlertLevel.CRITICAL,
                "High Disk Usage",
                f"Disk usage is {latest_system.disk_usage_percent:.1f}% (threshold: {self.alert_thresholds['disk_usage_percent']}%)",
                "system",
                {"disk_usage_percent": latest_system.disk_usage_percent}
            )
        
        # Check application metrics if available
        if latest_app:
            if latest_app.average_response_time > self.alert_thresholds['response_time_ms']:
                await self._create_alert(
                    AlertLevel.WARNING,
                    "Slow Response Time",
                    f"Average response time is {latest_app.average_response_time:.1f}ms (threshold: {self.alert_thresholds['response_time_ms']}ms)",
                    "application",
                    {"response_time": latest_app.average_response_time}
                )
            
            if latest_app.error_rate > self.alert_thresholds['error_rate_percent']:
                await self._create_alert(
                    AlertLevel.ERROR,
                    "High Error Rate",
                    f"Error rate is {latest_app.error_rate:.1f}% (threshold: {self.alert_thresholds['error_rate_percent']}%)",
                    "application",
                    {"error_rate": latest_app.error_rate}
                )
    
    async def _create_alert(
        self,
        level: AlertLevel,
        title: str,
        message: str,
        source: str,
        metadata: Dict[str, Any]
    ):
        """Create a new alert"""
        alert_id = f"alert_{int(time.time())}_{len(self.alerts)}"
        
        alert = Alert(
            id=alert_id,
            level=level,
            title=title,
            message=message,
            timestamp=datetime.utcnow(),
            source=source,
            metadata=metadata
        )
        
        self.alerts.append(alert)
        
        # Log the alert
        log_level = {
            AlertLevel.INFO: logging.INFO,
            AlertLevel.WARNING: logging.WARNING,
            AlertLevel.ERROR: logging.ERROR,
            AlertLevel.CRITICAL: logging.CRITICAL
        }[level]
        
        logger.log(log_level, f"ALERT [{level.value.upper()}] {title}: {message}")
        
        # Send to external monitoring service if configured
        await self._send_alert_to_external_service(alert)
    
    async def _send_alert_to_external_service(self, alert: Alert):
        """Send alert to external monitoring service"""
        # Implement integration with external services like:
        # - PagerDuty
        # - Slack
        # - Email
        # - Webhooks
        # - etc.
        
        if settings.DEBUG:
            logger.info(f"Would send alert to external service: {alert.title}")
    
    async def _cleanup_old_data(self):
        """Clean up old metrics and alerts"""
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        # Clean up old metrics
        self.system_metrics = [
            m for m in self.system_metrics 
            if m.timestamp > cutoff_time
        ]
        
        self.application_metrics = [
            m for m in self.application_metrics 
            if m.timestamp > cutoff_time
        ]
        
        # Clean up old resolved alerts
        self.alerts = [
            a for a in self.alerts 
            if not a.resolved or a.timestamp > cutoff_time
        ]
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current system and application metrics"""
        latest_system = self.system_metrics[-1] if self.system_metrics else None
        latest_app = self.application_metrics[-1] if self.application_metrics else None
        
        return {
            'system': asdict(latest_system) if latest_system else None,
            'application': asdict(latest_app) if latest_app else None,
            'monitoring_active': self.monitoring_active,
            'alert_count': len([a for a in self.alerts if not a.resolved])
        }
    
    def get_alerts(self, unresolved_only: bool = True) -> List[Dict[str, Any]]:
        """Get alerts"""
        alerts = self.alerts
        if unresolved_only:
            alerts = [a for a in alerts if not a.resolved]
        
        return [asdict(alert) for alert in alerts]
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.resolved = True
                alert.resolved_at = datetime.utcnow()
                logger.info(f"Alert resolved: {alert.title}")
                return True
        return False
    
    def update_thresholds(self, thresholds: Dict[str, float]):
        """Update monitoring thresholds"""
        self.alert_thresholds.update(thresholds)
        logger.info(f"Updated monitoring thresholds: {thresholds}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status"""
        if not self.system_metrics:
            return {
                'status': 'unknown',
                'message': 'No metrics available',
                'timestamp': datetime.utcnow().isoformat()
            }
        
        latest_system = self.system_metrics[-1]
        latest_app = self.application_metrics[-1] if self.application_metrics else None
        
        # Determine overall health
        health_issues = []
        
        if latest_system.cpu_percent > self.alert_thresholds['cpu_percent']:
            health_issues.append('high_cpu')
        
        if latest_system.memory_percent > self.alert_thresholds['memory_percent']:
            health_issues.append('high_memory')
        
        if latest_system.disk_usage_percent > self.alert_thresholds['disk_usage_percent']:
            health_issues.append('high_disk')
        
        if latest_app and latest_app.error_rate > self.alert_thresholds['error_rate_percent']:
            health_issues.append('high_error_rate')
        
        if not health_issues:
            status = 'healthy'
            message = 'All systems operational'
        elif len(health_issues) == 1:
            status = 'warning'
            message = f'Issue detected: {health_issues[0]}'
        else:
            status = 'critical'
            message = f'Multiple issues detected: {", ".join(health_issues)}'
        
        return {
            'status': status,
            'message': message,
            'issues': health_issues,
            'timestamp': datetime.utcnow().isoformat(),
            'metrics': {
                'system': asdict(latest_system),
                'application': asdict(latest_app) if latest_app else None
            }
        }

# Global monitoring service instance
monitoring_service = MonitoringService()

def get_monitoring_service() -> MonitoringService:
    """Get monitoring service instance"""
    return monitoring_service
