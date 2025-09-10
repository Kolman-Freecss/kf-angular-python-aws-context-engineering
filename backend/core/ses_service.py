import boto3
from botocore.exceptions import ClientError
from typing import Dict, Any, Optional
from core.config import settings
import logging

logger = logging.getLogger(__name__)


class SESService:
    def __init__(self):
        self.ses_client = boto3.client(
            'ses',
            endpoint_url=settings.AWS_ENDPOINT,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.SES_REGION
        )
        self.from_email = settings.SES_FROM_EMAIL

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send an email using AWS SES
        """
        try:
            message = {
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': {
                    'Html': {'Data': html_content, 'Charset': 'UTF-8'}
                }
            }
            
            if text_content:
                message['Body']['Text'] = {'Data': text_content, 'Charset': 'UTF-8'}

            response = self.ses_client.send_email(
                Source=self.from_email,
                Destination={'ToAddresses': [to_email]},
                Message=message
            )
            
            logger.info(f"Email sent successfully to {to_email}. MessageId: {response['MessageId']}")
            return {
                'success': True,
                'message_id': response['MessageId'],
                'response': response
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"Failed to send email to {to_email}. Error: {error_code} - {error_message}")
            return {
                'success': False,
                'error_code': error_code,
                'error_message': error_message
            }
        except Exception as e:
            logger.error(f"Unexpected error sending email to {to_email}: {str(e)}")
            return {
                'success': False,
                'error_message': str(e)
            }

    async def send_templated_email(
        self,
        to_email: str,
        template_name: str,
        template_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send a templated email using AWS SES
        """
        try:
            response = self.ses_client.send_templated_email(
                Source=self.from_email,
                Destination={'ToAddresses': [to_email]},
                Template=template_name,
                TemplateData=str(template_data).replace("'", '"')
            )
            
            logger.info(f"Templated email sent successfully to {to_email}. MessageId: {response['MessageId']}")
            return {
                'success': True,
                'message_id': response['MessageId'],
                'response': response
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"Failed to send templated email to {to_email}. Error: {error_code} - {error_message}")
            return {
                'success': False,
                'error_code': error_code,
                'error_message': error_message
            }
        except Exception as e:
            logger.error(f"Unexpected error sending templated email to {to_email}: {str(e)}")
            return {
                'success': False,
                'error_message': str(e)
            }

    async def verify_email_address(self, email: str) -> Dict[str, Any]:
        """
        Verify an email address with SES
        """
        try:
            response = self.ses_client.verify_email_identity(EmailAddress=email)
            logger.info(f"Email verification request sent to {email}")
            return {
                'success': True,
                'response': response
            }
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"Failed to verify email {email}. Error: {error_code} - {error_message}")
            return {
                'success': False,
                'error_code': error_code,
                'error_message': error_message
            }

    async def get_send_quota(self) -> Dict[str, Any]:
        """
        Get the current sending quota and rate
        """
        try:
            response = self.ses_client.get_send_quota()
            return {
                'success': True,
                'quota': response
            }
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"Failed to get send quota. Error: {error_code} - {error_message}")
            return {
                'success': False,
                'error_code': error_code,
                'error_message': error_message
            }


# Create a singleton instance
ses_service = SESService()
