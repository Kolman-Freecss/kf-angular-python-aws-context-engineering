import boto3
from botocore.exceptions import ClientError
from typing import Dict, Any, Optional, List
from core.config import settings
import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DynamoDBService:
    def __init__(self):
        self.dynamodb = boto3.resource(
            'dynamodb',
            endpoint_url=settings.AWS_ENDPOINT,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_DEFAULT_REGION
        )
        self.table_name = 'taskflow-analytics'
        self.table = self.dynamodb.Table(self.table_name)

    async def create_table_if_not_exists(self):
        """
        Create the analytics table if it doesn't exist
        """
        try:
            # Check if table exists
            self.table.load()
            logger.info(f"Table {self.table_name} already exists")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                # Create table
                table = self.dynamodb.create_table(
                    TableName=self.table_name,
                    KeySchema=[
                        {
                            'AttributeName': 'pk',
                            'KeyType': 'HASH'  # Partition key
                        },
                        {
                            'AttributeName': 'sk',
                            'KeyType': 'RANGE'  # Sort key
                        }
                    ],
                    AttributeDefinitions=[
                        {
                            'AttributeName': 'pk',
                            'AttributeType': 'S'
                        },
                        {
                            'AttributeName': 'sk',
                            'AttributeType': 'S'
                        }
                    ],
                    BillingMode='PAY_PER_REQUEST'
                )
                
                # Wait for table to be created
                table.wait_until_exists()
                logger.info(f"Table {self.table_name} created successfully")
            else:
                logger.error(f"Error checking table existence: {e}")
                raise

    async def store_analytics_data(
        self,
        user_id: int,
        analytics_type: str,
        data: Dict[str, Any],
        ttl_hours: int = 24
    ) -> bool:
        """
        Store analytics data in DynamoDB
        """
        try:
            # Calculate TTL (Time To Live)
            ttl = int((datetime.now() + timedelta(hours=ttl_hours)).timestamp())
            
            item = {
                'pk': f"USER#{user_id}",
                'sk': f"ANALYTICS#{analytics_type}#{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'data': json.dumps(data),
                'ttl': ttl,
                'created_at': datetime.now().isoformat(),
                'analytics_type': analytics_type
            }
            
            self.table.put_item(Item=item)
            logger.info(f"Analytics data stored for user {user_id}, type {analytics_type}")
            return True
            
        except ClientError as e:
            logger.error(f"Error storing analytics data: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error storing analytics data: {e}")
            return False

    async def get_analytics_data(
        self,
        user_id: int,
        analytics_type: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get analytics data from DynamoDB
        """
        try:
            response = self.table.query(
                KeyConditionExpression='pk = :pk AND begins_with(sk, :sk)',
                ExpressionAttributeValues={
                    ':pk': f"USER#{user_id}",
                    ':sk': f"ANALYTICS#{analytics_type}#"
                },
                ScanIndexForward=False,  # Sort by sort key descending
                Limit=limit
            )
            
            results = []
            for item in response['Items']:
                try:
                    data = json.loads(item['data'])
                    results.append({
                        'data': data,
                        'created_at': item['created_at'],
                        'analytics_type': item['analytics_type']
                    })
                except json.JSONDecodeError:
                    logger.error(f"Error parsing analytics data for item {item['sk']}")
                    continue
            
            logger.info(f"Retrieved {len(results)} analytics records for user {user_id}, type {analytics_type}")
            return results
            
        except ClientError as e:
            logger.error(f"Error retrieving analytics data: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error retrieving analytics data: {e}")
            return []

    async def store_user_preferences(
        self,
        user_id: int,
        preferences: Dict[str, Any]
    ) -> bool:
        """
        Store user preferences in DynamoDB
        """
        try:
            item = {
                'pk': f"USER#{user_id}",
                'sk': "PREFERENCES",
                'preferences': json.dumps(preferences),
                'updated_at': datetime.now().isoformat()
            }
            
            self.table.put_item(Item=item)
            logger.info(f"User preferences stored for user {user_id}")
            return True
            
        except ClientError as e:
            logger.error(f"Error storing user preferences: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error storing user preferences: {e}")
            return False

    async def get_user_preferences(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user preferences from DynamoDB
        """
        try:
            response = self.table.get_item(
                Key={
                    'pk': f"USER#{user_id}",
                    'sk': "PREFERENCES"
                }
            )
            
            if 'Item' in response:
                preferences = json.loads(response['Item']['preferences'])
                logger.info(f"User preferences retrieved for user {user_id}")
                return preferences
            else:
                logger.info(f"No preferences found for user {user_id}")
                return None
                
        except ClientError as e:
            logger.error(f"Error retrieving user preferences: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error retrieving user preferences: {e}")
            return None

    async def store_session_data(
        self,
        user_id: int,
        session_id: str,
        session_data: Dict[str, Any],
        ttl_hours: int = 24
    ) -> bool:
        """
        Store session data in DynamoDB
        """
        try:
            ttl = int((datetime.now() + timedelta(hours=ttl_hours)).timestamp())
            
            item = {
                'pk': f"USER#{user_id}",
                'sk': f"SESSION#{session_id}",
                'session_data': json.dumps(session_data),
                'ttl': ttl,
                'created_at': datetime.now().isoformat()
            }
            
            self.table.put_item(Item=item)
            logger.info(f"Session data stored for user {user_id}, session {session_id}")
            return True
            
        except ClientError as e:
            logger.error(f"Error storing session data: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error storing session data: {e}")
            return False

    async def get_session_data(self, user_id: int, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session data from DynamoDB
        """
        try:
            response = self.table.get_item(
                Key={
                    'pk': f"USER#{user_id}",
                    'sk': f"SESSION#{session_id}"
                }
            )
            
            if 'Item' in response:
                session_data = json.loads(response['Item']['session_data'])
                logger.info(f"Session data retrieved for user {user_id}, session {session_id}")
                return session_data
            else:
                logger.info(f"No session data found for user {user_id}, session {session_id}")
                return None
                
        except ClientError as e:
            logger.error(f"Error retrieving session data: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error retrieving session data: {e}")
            return None

    async def delete_session_data(self, user_id: int, session_id: str) -> bool:
        """
        Delete session data from DynamoDB
        """
        try:
            self.table.delete_item(
                Key={
                    'pk': f"USER#{user_id}",
                    'sk': f"SESSION#{session_id}"
                }
            )
            logger.info(f"Session data deleted for user {user_id}, session {session_id}")
            return True
            
        except ClientError as e:
            logger.error(f"Error deleting session data: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting session data: {e}")
            return False

    async def cleanup_expired_data(self) -> int:
        """
        Clean up expired data (DynamoDB TTL handles this automatically, but we can track it)
        """
        try:
            # DynamoDB automatically deletes items when TTL expires
            # This method is here for monitoring purposes
            logger.info("DynamoDB TTL cleanup is handled automatically")
            return 0
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            return 0


# Create a singleton instance
dynamodb_service = DynamoDBService()
