from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from api.auth import get_current_user
from core.websocket_service import websocket_service
from models.user import User
from models.task import Task
from models.notification import Notification
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/tasks/{user_id}")
async def websocket_tasks_endpoint(
    websocket: WebSocket,
    user_id: int,
    token: str = None
):
    """
    WebSocket endpoint for real-time task updates
    """
    try:
        # In a real implementation, you'd validate the token here
        # For now, we'll accept the connection directly
        
        await websocket_service.handle_websocket(
            websocket, user_id, "tasks"
        )
    except WebSocketDisconnect:
        logger.info(f"User {user_id} disconnected from tasks WebSocket")
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")


@router.websocket("/ws/notifications/{user_id}")
async def websocket_notifications_endpoint(
    websocket: WebSocket,
    user_id: int,
    token: str = None
):
    """
    WebSocket endpoint for real-time notifications
    """
    try:
        await websocket_service.handle_websocket(
            websocket, user_id, "notifications"
        )
    except WebSocketDisconnect:
        logger.info(f"User {user_id} disconnected from notifications WebSocket")
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")


@router.websocket("/ws/analytics/{user_id}")
async def websocket_analytics_endpoint(
    websocket: WebSocket,
    user_id: int,
    token: str = None
):
    """
    WebSocket endpoint for real-time analytics updates
    """
    try:
        await websocket_service.handle_websocket(
            websocket, user_id, "analytics"
        )
    except WebSocketDisconnect:
        logger.info(f"User {user_id} disconnected from analytics WebSocket")
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")


@router.websocket("/ws/collaboration/{task_id}")
async def websocket_collaboration_endpoint(
    websocket: WebSocket,
    task_id: int,
    user_id: int,
    token: str = None
):
    """
    WebSocket endpoint for task collaboration
    """
    try:
        await websocket_service.handle_websocket(
            websocket, user_id, f"collaboration_{task_id}"
        )
    except WebSocketDisconnect:
        logger.info(f"User {user_id} disconnected from collaboration WebSocket for task {task_id}")
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id} on task {task_id}: {e}")


@router.get("/ws/stats")
async def get_websocket_stats(
    current_user: User = Depends(get_current_user)
):
    """
    Get WebSocket connection statistics
    """
    try:
        stats = websocket_service.manager.get_connection_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Error getting WebSocket stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get WebSocket statistics"
        )


@router.post("/ws/broadcast")
async def broadcast_message(
    message: dict,
    current_user: User = Depends(get_current_user)
):
    """
    Broadcast a message to all connected users (admin only)
    """
    try:
        # Check if user has admin privileges (implement your own logic)
        if not current_user.is_active:  # Simple check for now
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        broadcast_message = {
            "type": "admin_broadcast",
            "data": message,
            "timestamp": websocket_service.manager.connection_metadata.get('timestamp', ''),
            "from_admin": current_user.email
        }
        
        await websocket_service.manager.broadcast_to_all(broadcast_message)
        
        return {
            "success": True,
            "message": "Message broadcasted successfully"
        }
        
    except Exception as e:
        logger.error(f"Error broadcasting message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to broadcast message"
        )


@router.post("/ws/send-to-user/{target_user_id}")
async def send_message_to_user(
    target_user_id: int,
    message: dict,
    current_user: User = Depends(get_current_user)
):
    """
    Send a message to a specific user
    """
    try:
        user_message = {
            "type": "user_message",
            "data": message,
            "timestamp": websocket_service.manager.connection_metadata.get('timestamp', ''),
            "from_user": current_user.email
        }
        
        await websocket_service.manager.send_to_user(user_message, target_user_id)
        
        return {
            "success": True,
            "message": f"Message sent to user {target_user_id}"
        }
        
    except Exception as e:
        logger.error(f"Error sending message to user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message"
        )


# Helper functions for triggering WebSocket updates from other parts of the application

async def notify_task_update(task_id: int, user_id: int, update_type: str, task_data: dict):
    """
    Notify WebSocket clients about task updates
    """
    try:
        message = {
            "type": "task_update",
            "task_id": task_id,
            "update_type": update_type,
            "data": task_data,
            "timestamp": websocket_service.manager.connection_metadata.get('timestamp', '')
        }
        
        await websocket_service.manager.send_task_update(user_id, message)
        logger.info(f"Task update notification sent to user {user_id}")
        
    except Exception as e:
        logger.error(f"Error sending task update notification: {e}")


async def notify_new_notification(user_id: int, notification_data: dict):
    """
    Notify WebSocket clients about new notifications
    """
    try:
        message = {
            "type": "new_notification",
            "data": notification_data,
            "timestamp": websocket_service.manager.connection_metadata.get('timestamp', '')
        }
        
        await websocket_service.manager.send_notification(user_id, message)
        logger.info(f"Notification sent to user {user_id}")
        
    except Exception as e:
        logger.error(f"Error sending notification: {e}")


async def notify_analytics_update(user_id: int, analytics_data: dict):
    """
    Notify WebSocket clients about analytics updates
    """
    try:
        message = {
            "type": "analytics_update",
            "data": analytics_data,
            "timestamp": websocket_service.manager.connection_metadata.get('timestamp', '')
        }
        
        await websocket_service.manager.send_analytics_update(user_id, message)
        logger.info(f"Analytics update sent to user {user_id}")
        
    except Exception as e:
        logger.error(f"Error sending analytics update: {e}")


async def notify_collaboration_update(task_id: int, collaboration_data: dict):
    """
    Notify WebSocket clients about collaboration updates
    """
    try:
        await websocket_service.manager.send_collaboration_update(task_id, collaboration_data)
        logger.info(f"Collaboration update sent for task {task_id}")
        
    except Exception as e:
        logger.error(f"Error sending collaboration update: {e}")
