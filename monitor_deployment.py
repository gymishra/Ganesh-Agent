#!/usr/bin/env python3

import boto3
import json
import time
from datetime import datetime, timedelta
import sys

class DeploymentMonitor:
    """Monitor OData deployment progress via CloudWatch"""
    
    def __init__(self, region='us-east-1'):
        self.region = region
        self.cloudwatch_logs = boto3.client('logs', region_name=region)
        self.cloudwatch_metrics = boto3.client('cloudwatch', region_name=region)
        self.sagemaker = boto3.client('sagemaker', region_name=region)
        
    def get_recent_log_streams(self, log_group_name='/aws/sagemaker/odata-deployment', limit=5):
        """Get recent deployment log streams"""
        try:
            response = self.cloudwatch_logs.describe_log_streams(
                logGroupName=log_group_name,
                orderBy='LastEventTime',
                descending=True,
                limit=limit
            )
            return response.get('logStreams', [])
        except Exception as e:
            print(f"⚠️ Could not get log streams: {str(e)}")
            return []
    
    def get_log_events(self, log_group_name, log_stream_name, limit=50):
        """Get recent log events from a stream"""
        try:
            response = self.cloudwatch_logs.get_log_events(
                logGroupName=log_group_name,
                logStreamName=log_stream_name,
                limit=limit,
                startFromHead=False
            )
            return response.get('events', [])
        except Exception as e:
            print(f"⚠️ Could not get log events: {str(e)}")
            return []
    
    def get_deployment_metrics(self, hours_back=1):
        """Get deployment metrics from CloudWatch"""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=hours_back)
            
            response = self.cloudwatch_metrics.get_metric_statistics(
                Namespace='SageMaker/ODataDeployment',
                MetricName='DeploymentStarted',
                Dimensions=[],
                StartTime=start_time,
                EndTime=end_time,
                Period=300,  # 5 minutes
                Statistics=['Sum']
            )
            return response.get('Datapoints', [])
        except Exception as e:
            print(f"⚠️ Could not get metrics: {str(e)}")
            return []
    
    def get_sagemaker_jobs(self, limit=5):
        """Get recent SageMaker training jobs"""
        try:
            response = self.sagemaker.list_training_jobs(
                SortBy='CreationTime',
                SortOrder='Descending',
                MaxResults=limit
            )
            return response.get('TrainingJobSummaries', [])
        except Exception as e:
            print(f"⚠️ Could not get training jobs: {str(e)}")
            return []
    
    def get_sagemaker_endpoints(self, limit=5):
        """Get recent SageMaker endpoints"""
        try:
            response = self.sagemaker.list_endpoints(
                SortBy='CreationTime',
                SortOrder='Descending',
                MaxResults=limit
            )
            return response.get('Endpoints', [])
        except Exception as e:
            print(f"⚠️ Could not get endpoints: {str(e)}")
            return []
    
    def display_status(self):
        """Display current deployment status"""
        print("🔍 OData Deployment Monitor")
        print("=" * 60)
        print(f"📅 Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Recent log streams
        print("📋 Recent Deployment Log Streams:")
        log_streams = self.get_recent_log_streams()
        if log_streams:
            for i, stream in enumerate(log_streams[:3], 1):
                last_event = datetime.fromtimestamp(stream['lastEventTimestamp']/1000)
                print(f"   {i}. {stream['logStreamName']}")
                print(f"      Last Activity: {last_event.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print("   ❌ No deployment log streams found")
        print()
        
        # Recent log events from latest stream
        if log_streams:
            latest_stream = log_streams[0]
            print(f"📝 Latest Log Events from: {latest_stream['logStreamName']}")
            events = self.get_log_events('/aws/sagemaker/odata-deployment', latest_stream['logStreamName'], 10)
            
            if events:
                for event in events[-10:]:  # Show last 10 events
                    timestamp = datetime.fromtimestamp(event['timestamp']/1000)
                    try:
                        # Try to parse JSON log message
                        log_data = json.loads(event['message'])
                        level = log_data.get('level', 'INFO')
                        message = log_data.get('message', event['message'])
                        phase = log_data.get('phase', '')
                        
                        # Format based on level
                        if level == 'SUCCESS':
                            icon = "✅"
                        elif level == 'ERROR':
                            icon = "❌"
                        elif level == 'WARNING':
                            icon = "⚠️"
                        elif level == 'PROGRESS':
                            icon = "🔄"
                        else:
                            icon = "ℹ️"
                        
                        print(f"   {timestamp.strftime('%H:%M:%S')} {icon} [{phase}] {message}")
                    except:
                        # Fallback for non-JSON messages
                        print(f"   {timestamp.strftime('%H:%M:%S')} ℹ️  {event['message']}")
            else:
                print("   ❌ No recent log events found")
        print()
        
        # SageMaker Training Jobs
        print("🏋️ Recent SageMaker Training Jobs:")
        training_jobs = self.get_sagemaker_jobs()
        if training_jobs:
            for job in training_jobs:
                status = job['TrainingJobStatus']
                created = job['CreationTime'].strftime('%Y-%m-%d %H:%M:%S')
                
                if status == 'Completed':
                    icon = "✅"
                elif status == 'InProgress':
                    icon = "🔄"
                elif status == 'Failed':
                    icon = "❌"
                else:
                    icon = "⏸️"
                
                print(f"   {icon} {job['TrainingJobName']}")
                print(f"      Status: {status} | Created: {created}")
        else:
            print("   ❌ No training jobs found")
        print()
        
        # SageMaker Endpoints
        print("🚀 Recent SageMaker Endpoints:")
        endpoints = self.get_sagemaker_endpoints()
        if endpoints:
            for endpoint in endpoints:
                status = endpoint['EndpointStatus']
                created = endpoint['CreationTime'].strftime('%Y-%m-%d %H:%M:%S')
                
                if status == 'InService':
                    icon = "✅"
                elif status == 'Creating':
                    icon = "🔄"
                elif status == 'Failed':
                    icon = "❌"
                else:
                    icon = "⏸️"
                
                print(f"   {icon} {endpoint['EndpointName']}")
                print(f"      Status: {status} | Created: {created}")
        else:
            print("   ❌ No endpoints found")
        print()
        
        # CloudWatch Console Links
        print("🔗 CloudWatch Console Links:")
        log_group_encoded = '%2Faws%2Fsagemaker%2Fodata-deployment'
        print(f"   Logs: https://console.aws.amazon.com/cloudwatch/home?region={self.region}#logsV2:log-groups/log-group/{log_group_encoded}")
        print(f"   Metrics: https://console.aws.amazon.com/cloudwatch/home?region={self.region}#metricsV2:graph=~();namespace=SageMaker/ODataDeployment")
        print(f"   SageMaker: https://console.aws.amazon.com/sagemaker/home?region={self.region}#/jobs")
        print()
    
    def monitor_continuously(self, interval=30):
        """Monitor deployment continuously"""
        print("🔄 Starting continuous monitoring (Ctrl+C to stop)")
        print(f"   Refresh interval: {interval} seconds")
        print()
        
        try:
            while True:
                self.display_status()
                print(f"⏰ Next refresh in {interval} seconds...")
                print("=" * 60)
                time.sleep(interval)
                
                # Clear screen (works on most terminals)
                print("\033[2J\033[H", end="")
                
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped by user")

def main():
    monitor = DeploymentMonitor()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--continuous':
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        monitor.monitor_continuously(interval)
    else:
        monitor.display_status()
        print("💡 Tip: Use '--continuous [seconds]' for continuous monitoring")
        print("   Example: python monitor_deployment.py --continuous 30")

if __name__ == "__main__":
    main()
