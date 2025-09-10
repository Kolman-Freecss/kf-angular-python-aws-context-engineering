import json
import boto3
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')
ses = boto3.client('ses')

# Environment variables
ANALYTICS_TABLE = os.environ.get('ANALYTICS_TABLE', 'taskflow-analytics')
S3_BUCKET = os.environ.get('S3_BUCKET', 'taskflow-analytics-exports')
SES_FROM_EMAIL = os.environ.get('SES_FROM_EMAIL', 'noreply@taskflow.com')


def lambda_handler(event, context):
    """
    Lambda function to process analytics data
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Determine the type of processing needed
        event_type = event.get('type', 'analytics_generation')
        
        if event_type == 'analytics_generation':
            return process_analytics_generation(event)
        elif event_type == 'data_export':
            return process_data_export(event)
        elif event_type == 'cleanup':
            return process_cleanup(event)
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Unknown event type'})
            }
            
    except Exception as e:
        logger.error(f"Error processing event: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def process_analytics_generation(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process analytics data generation
    """
    try:
        user_id = event.get('user_id')
        analytics_type = event.get('analytics_type', 'overview')
        days = event.get('days', 30)
        
        if not user_id:
            raise ValueError("user_id is required")
        
        # Generate analytics data (this would typically call your database)
        analytics_data = generate_analytics_data(user_id, analytics_type, days)
        
        # Store in DynamoDB
        table = dynamodb.Table(ANALYTICS_TABLE)
        ttl = int((datetime.now() + timedelta(hours=24)).timestamp())
        
        item = {
            'pk': f"USER#{user_id}",
            'sk': f"ANALYTICS#{analytics_type}#{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'data': json.dumps(analytics_data),
            'ttl': ttl,
            'created_at': datetime.now().isoformat(),
            'analytics_type': analytics_type
        }
        
        table.put_item(Item=item)
        
        logger.info(f"Analytics data generated and stored for user {user_id}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Analytics data generated successfully',
                'user_id': user_id,
                'analytics_type': analytics_type
            })
        }
        
    except Exception as e:
        logger.error(f"Error in analytics generation: {str(e)}")
        raise


def process_data_export(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process data export to S3
    """
    try:
        user_id = event.get('user_id')
        export_format = event.get('format', 'json')
        days = event.get('days', 30)
        
        if not user_id:
            raise ValueError("user_id is required")
        
        # Generate export data
        export_data = generate_export_data(user_id, days)
        
        # Create filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"user_{user_id}_export_{timestamp}.{export_format}"
        
        # Convert to appropriate format
        if export_format == 'json':
            file_content = json.dumps(export_data, indent=2)
            content_type = 'application/json'
        elif export_format == 'csv':
            file_content = convert_to_csv(export_data)
            content_type = 'text/csv'
        else:
            raise ValueError(f"Unsupported export format: {export_format}")
        
        # Upload to S3
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=f"exports/{filename}",
            Body=file_content,
            ContentType=content_type
        )
        
        # Generate presigned URL for download
        presigned_url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': f"exports/{filename}"},
            ExpiresIn=3600  # 1 hour
        )
        
        logger.info(f"Data export completed for user {user_id}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Data export completed successfully',
                'user_id': user_id,
                'filename': filename,
                'download_url': presigned_url
            })
        }
        
    except Exception as e:
        logger.error(f"Error in data export: {str(e)}")
        raise


def process_cleanup(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process cleanup of old data
    """
    try:
        cleanup_type = event.get('cleanup_type', 'all')
        days_old = event.get('days_old', 30)
        
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        if cleanup_type == 'analytics' or cleanup_type == 'all':
            # Cleanup old analytics data
            table = dynamodb.Table(ANALYTICS_TABLE)
            
            # Scan for old analytics data
            response = table.scan(
                FilterExpression='created_at < :cutoff_date',
                ExpressionAttributeValues={
                    ':cutoff_date': cutoff_date.isoformat()
                }
            )
            
            deleted_count = 0
            for item in response['Items']:
                table.delete_item(
                    Key={
                        'pk': item['pk'],
                        'sk': item['sk']
                    }
                )
                deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} old analytics records")
        
        if cleanup_type == 'exports' or cleanup_type == 'all':
            # Cleanup old export files from S3
            response = s3.list_objects_v2(
                Bucket=S3_BUCKET,
                Prefix='exports/'
            )
            
            deleted_count = 0
            if 'Contents' in response:
                for obj in response['Contents']:
                    if obj['LastModified'].replace(tzinfo=None) < cutoff_date:
                        s3.delete_object(
                            Bucket=S3_BUCKET,
                            Key=obj['Key']
                        )
                        deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} old export files")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Cleanup completed successfully',
                'cleanup_type': cleanup_type,
                'days_old': days_old
            })
        }
        
    except Exception as e:
        logger.error(f"Error in cleanup: {str(e)}")
        raise


def generate_analytics_data(user_id: int, analytics_type: str, days: int) -> Dict[str, Any]:
    """
    Generate analytics data (placeholder - would connect to your database)
    """
    # This is a placeholder function
    # In a real implementation, you would connect to your database
    # and generate actual analytics data
    
    return {
        'user_id': user_id,
        'analytics_type': analytics_type,
        'period_days': days,
        'generated_at': datetime.now().isoformat(),
        'data': {
            'total_tasks': 0,
            'completed_tasks': 0,
            'completion_rate': 0.0
        }
    }


def generate_export_data(user_id: int, days: int) -> Dict[str, Any]:
    """
    Generate export data (placeholder - would connect to your database)
    """
    # This is a placeholder function
    # In a real implementation, you would connect to your database
    # and generate actual export data
    
    return {
        'user_id': user_id,
        'export_date': datetime.now().isoformat(),
        'period_days': days,
        'tasks': [],
        'notifications': [],
        'summary': {
            'total_tasks': 0,
            'total_notifications': 0
        }
    }


def convert_to_csv(data: Dict[str, Any]) -> str:
    """
    Convert data to CSV format
    """
    import csv
    import io
    
    output = io.StringIO()
    
    # Write summary
    writer = csv.writer(output)
    writer.writerow(['Summary'])
    writer.writerow(['Total Tasks', data['summary']['total_tasks']])
    writer.writerow(['Total Notifications', data['summary']['total_notifications']])
    writer.writerow([])
    
    # Write tasks
    writer.writerow(['Tasks'])
    if data['tasks']:
        writer.writerow(data['tasks'][0].keys())  # Header
        for task in data['tasks']:
            writer.writerow(task.values())
    
    writer.writerow([])
    
    # Write notifications
    writer.writerow(['Notifications'])
    if data['notifications']:
        writer.writerow(data['notifications'][0].keys())  # Header
        for notification in data['notifications']:
            writer.writerow(notification.values())
    
    return output.getvalue()
