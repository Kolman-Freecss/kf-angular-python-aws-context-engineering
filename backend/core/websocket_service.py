from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Set
import json
import logging
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        # Store active connections by user_id
        self.active_connections: Dict[int, List[WebSocket]] = {}
        # Store connection metadata
        self.connection_metadata: Dict[WebSocket, Dict] = {}

    async def connect(self, websocket: WebSocket, user_id: int, connection_type: str = "general"):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        
        self.active_connections[user_id].append(websocket)
        self.connection_metadata[websocket] = {
            'user_id': user_id,
            'connection_type': connection_type,
            'connected_at': datetime.now(),
            'last_ping': datetime.now()
        }
        
        logger.info(f"User {user_id} connected with {connection_type} connection")
        
        # Send welcome message
        await self.send_personal_message({
            "type": "connection_established",
            "message": "Connected to TaskFlow real-time updates",
            "timestamp": datetime.now().isoformat()
        }, websocket)

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.connection_metadata:
            metadata = self.connection_metadata[websocket]
            user_id = metadata['user_id']
            
            if user_id in self.active_connections:
                self.active_connections[user_id].remove(websocket)
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
            
            del self.connection_metadata[websocket]
            logger.info(f"User {user_id} disconnected")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific WebSocket connection"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)

    async def send_to_user(self, message: dict, user_id: int, connection_type: str = None):
        """Send a message to all connections for a specific user"""
        if user_id in self.active_connections:
            connections_to_send = self.active_connections[user_id]
            
            if connection_type:
                # Filter by connection type
                connections_to_send = [
                    ws for ws in connections_to_send
                    if self.connection_metadata.get(ws, {}).get('connection_type') == connection_type
                ]
            
            for websocket in connections_to_send:
                await self.send_personal_message(message, websocket)

    async def broadcast_to_all(self, message: dict, exclude_user: int = None):
        """Broadcast a message to all connected users"""
        for user_id, connections in self.active_connections.items():
            if exclude_user and user_id == exclude_user:
                continue
            await self.send_to_user(message, user_id)

    async def send_task_update(self, user_id: int, task_data: dict):
        """Send task update notification to user"""
        message = {
            "type": "task_update",
            "data": task_data,
            "timestamp": datetime.now().isoformat()
        }
        await self.send_to_user(message, user_id, "tasks")

    async def send_notification(self, user_id: int, notification_data: dict):
        """Send notification to user"""
        message = {
            "type": "notification",
            "data": notification_data,
            "timestamp": datetime.now().isoformat()
        }
        await self.send_to_user(message, user_id, "notifications")

    async def send_analytics_update(self, user_id: int, analytics_data: dict):
        """Send analytics update to user"""
        message = {
            "type": "analytics_update",
            "data": analytics_data,
            "timestamp": datetime.now().isoformat()
        }
        await self.send_to_user(message, user_id, "analytics")

    async def send_collaboration_update(self, task_id: int, collaboration_data: dict):
        """Send collaboration update to all users working on a task"""
        # This would need to be implemented based on your collaboration logic
        message = {
            "type": "collaboration_update",
            "task_id": task_id,
            "data": collaboration_data,
            "timestamp": datetime.now().isoformat()
        }
        # For now, broadcast to all users - in production you'd filter by collaborators
        await self.broadcast_to_all(message)

    async def ping_connections(self):
        """Send ping to all connections to check if they're alive"""
        ping_message = {
            "type": "ping",
            "timestamp": datetime.now().isoformat()
        }
        
        dead_connections = []
        for websocket, metadata in self.connection_metadata.items():
            try:
                await websocket.send_text(json.dumps(ping_message))
                metadata['last_ping'] = datetime.now()
            except Exception as e:
                logger.warning(f"Connection ping failed: {e}")
                dead_connections.append(websocket)
        
        # Remove dead connections
        for websocket in dead_connections:
            self.disconnect(websocket)

    def get_connection_stats(self) -> dict:
        """Get statistics about active connections"""
        total_connections = sum(len(connections) for connections in self.active_connections.values())
        unique_users = len(self.active_connections)
        
        connection_types = {}
        for metadata in self.connection_metadata.values():
            conn_type = metadata['connection_type']
            connection_types[conn_type] = connection_types.get(conn_type, 0) + 1
        
        return {
            "total_connections": total_connections,
            "unique_users": unique_users,
            "connection_types": connection_types,
            "active_users": list(self.active_connections.keys())
        }


# Global connection manager instance
manager = ConnectionManager()


class WebSocketService:
    def __init__(self):
        self.manager = manager

    async def handle_websocket(self, websocket: WebSocket, user_id: int, connection_type: str = "general"):
        """Handle WebSocket connection lifecycle"""
        await self.manager.connect(websocket, user_id, connection_type)
        
        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                await self.handle_message(websocket, user_id, message)
                
        except WebSocketDisconnect:
            self.manager.disconnect(websocket)
        except Exception as e:
            logger.error(f"WebSocket error for user {user_id}: {e}")
            self.manager.disconnect(websocket)

    async def handle_message(self, websocket: WebSocket, user_id: int, message: dict):
        """Handle incoming WebSocket messages"""
        message_type = message.get("type")
        
        if message_type == "pong":
            # Update last ping time
            if websocket in self.manager.connection_metadata:
                self.manager.connection_metadata[websocket]['last_ping'] = datetime.now()
        
        elif message_type == "subscribe":
            # Subscribe to specific updates
            subscription_type = message.get("subscription_type")
            if subscription_type:
                await self.subscribe_to_updates(websocket, user_id, subscription_type)
        
        elif message_type == "unsubscribe":
            # Unsubscribe from updates
            subscription_type = message.get("subscription_type")
            if subscription_type:
                await self.unsubscribe_from_updates(websocket, user_id, subscription_type)
        
        elif message_type == "task_update":
            # Handle task update from client
            task_data = message.get("data")
            if task_data:
                await self.broadcast_task_update(task_data)
        
        elif message_type == "collaboration":
            # Handle collaboration message
            collaboration_data = message.get("data")
            if collaboration_data:
                await self.handle_collaboration(user_id, collaboration_data)
        
        else:
            logger.warning(f"Unknown message type: {message_type}")

    async def subscribe_to_updates(self, websocket: WebSocket, user_id: int, subscription_type: str):
        """Subscribe to specific update types"""
        if websocket in self.manager.connection_metadata:
            self.manager.connection_metadata[websocket]['subscriptions'] = \
                self.manager.connection_metadata[websocket].get('subscriptions', set())
            self.manager.connection_metadata[websocket]['subscriptions'].add(subscription_type)
            
            await self.send_personal_message({
                "type": "subscription_confirmed",
                "subscription_type": subscription_type,
                "timestamp": datetime.now().isoformat()
            }, websocket)

    async def unsubscribe_from_updates(self, websocket: WebSocket, user_id: int, subscription_type: str):
        """Unsubscribe from specific update types"""
        if websocket in self.manager.connection_metadata:
            subscriptions = self.manager.connection_metadata[websocket].get('subscriptions', set())
            subscriptions.discard(subscription_type)
            
            await self.send_personal_message({
                "type": "unsubscription_confirmed",
                "subscription_type": subscription_type,
                "timestamp": datetime.now().isoformat()
            }, websocket)

    async def broadcast_task_update(self, task_data: dict):
        """Broadcast task update to relevant users"""
        # In a real implementation, you'd determine which users should receive this update
        # For now, broadcast to all users
        message = {
            "type": "task_update",
            "data": task_data,
            "timestamp": datetime.now().isoformat()
        }
        await self.manager.broadcast_to_all(message)

    async def handle_collaboration(self, user_id: int, collaboration_data: dict):
        """Handle collaboration messages"""
        task_id = collaboration_data.get("task_id")
        if task_id:
            # Send collaboration update to other users working on the same task
            await self.manager.send_collaboration_update(task_id, collaboration_data)

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a personal message to a WebSocket"""
        await self.manager.send_personal_message(message, websocket)

    async def start_ping_task(self):
        """Start the ping task to keep connections alive"""
        while True:
            await asyncio.sleep(30)  # Ping every 30 seconds
            await self.manager.ping_connections()


# Global WebSocket service instance
websocket_service = WebSocketService()
