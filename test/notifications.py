
import os
import json
import logging
import asyncio
import requests
from datetime import datetime, timedelta, time
from config import BOT_TOKEN, NOTIFICATIONS_JSON_PATH

logger = logging.getLogger(__name__)

class NotificationSystem:
    def __init__(self):
        self.active_notifications = {}
        self.message_tasks = {}

    def load_notifications(self):
        """Load notifications from JSON file"""
        try:
            with open(NOTIFICATIONS_JSON_PATH, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_notifications(self, notifications):
        """Save notifications to JSON file"""
        try:
            os.makedirs(os.path.dirname(NOTIFICATIONS_JSON_PATH), exist_ok=True)
            with open(NOTIFICATIONS_JSON_PATH, 'w') as f:
                json.dump(notifications, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error saving notifications: {e}")
            return False

    def create_notification(self, user_id, message_text, send_time, days_of_week, weeks_count):
        """Create a new notification"""
        notifications = self.load_notifications()
        
        notification = {
            'id': len(notifications) + 1,
            'user_id': user_id,
            'message_text': message_text,
            'send_time': send_time,  # Format: "HH:MM"
            'days_of_week': days_of_week,  # List like [1, 2, 3, 4, 5] for Mon-Fri
            'weeks_count': weeks_count,
            'created_at': datetime.now().isoformat(),
            'is_active': True,
            'executions': []
        }
        
        notifications.append(notification)
        
        if self.save_notifications(notifications):
            return notification
        return None

    def get_user_notifications(self, user_id):
        """Get all notifications for a user"""
        notifications = self.load_notifications()
        return [n for n in notifications if n['user_id'] == user_id and n['is_active']]

    def delete_notification(self, notification_id, user_id):
        """Delete a notification"""
        notifications = self.load_notifications()
        
        for i, notification in enumerate(notifications):
            if notification['id'] == notification_id and notification['user_id'] == user_id:
                notifications[i]['is_active'] = False
                return self.save_notifications(notifications)
        
        return False

    async def send_telegram_message(self, user_id, message):
        """Send message to user via Telegram"""
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            data = {
                'chat_id': user_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, json=data, timeout=10)
            result = response.json()
            
            if result.get('ok'):
                return result['result']['message_id']
            return None
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return None

    async def delete_telegram_message(self, user_id, message_id):
        """Delete message from Telegram"""
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteMessage"
            data = {
                'chat_id': user_id,
                'message_id': message_id
            }
            response = requests.post(url, json=data, timeout=10)
            return response.json().get('ok', False)
        except Exception as e:
            logger.error(f"Error deleting message: {e}")
            return False

    async def send_notification_sequence(self, user_id, message_text):
        """Send the three-message sequence with timing"""
        try:
            # First message - disappears after 9 minutes
            first_msg_id = await self.send_telegram_message(user_id, f"🔔 {message_text}")
            if first_msg_id:
                # Schedule deletion after 9 minutes
                asyncio.create_task(self.schedule_message_deletion(user_id, first_msg_id, 9 * 60))
            
            # Wait 10 minutes before second message
            await asyncio.sleep(10 * 60)
            
            # Second message - disappears after 9 minutes
            second_msg_id = await self.send_telegram_message(user_id, f"🔔 {message_text}\n\n⚠️ Повторное напоминание")
            if second_msg_id:
                # Schedule deletion after 9 minutes
                asyncio.create_task(self.schedule_message_deletion(user_id, second_msg_id, 9 * 60))
            
            # Wait 10 minutes before third message
            await asyncio.sleep(10 * 60)
            
            # Third message - permanent
            await self.send_telegram_message(user_id, f"🔔 {message_text}\n\n🚨 Финальное напоминание")
            
        except Exception as e:
            logger.error(f"Error in notification sequence: {e}")

    async def schedule_message_deletion(self, user_id, message_id, delay_seconds):
        """Schedule message deletion after delay"""
        try:
            await asyncio.sleep(delay_seconds)
            await self.delete_telegram_message(user_id, message_id)
        except Exception as e:
            logger.error(f"Error scheduling message deletion: {e}")

    def should_send_notification(self, notification):
        """Check if notification should be sent today"""
        now = datetime.now()
        current_weekday = now.weekday() + 1  # Monday = 1, Sunday = 7
        current_time = now.time()
        send_time = datetime.strptime(notification['send_time'], '%H:%M').time()
        
        # Check if today is in the selected days
        if current_weekday not in notification['days_of_week']:
            return False
        
        # Check if it's the right time (within 1 minute window)
        time_diff = abs((current_time.hour * 60 + current_time.minute) - 
                       (send_time.hour * 60 + send_time.minute))
        
        if time_diff > 1:  # Not within 1-minute window
            return False
        
        # Check if notification has expired (weeks_count)
        created_date = datetime.fromisoformat(notification['created_at']).date()
        weeks_passed = (now.date() - created_date).days // 7
        
        if weeks_passed >= notification['weeks_count']:
            return False
        
        # Check if already sent today
        today_str = now.strftime('%Y-%m-%d')
        if any(exec_date.startswith(today_str) for exec_date in notification.get('executions', [])):
            return False
        
        return True

    def mark_notification_executed(self, notification_id):
        """Mark notification as executed for today"""
        notifications = self.load_notifications()
        
        for notification in notifications:
            if notification['id'] == notification_id:
                if 'executions' not in notification:
                    notification['executions'] = []
                notification['executions'].append(datetime.now().isoformat())
                break
        
        self.save_notifications(notifications)

    async def check_and_send_notifications(self):
        """Check for notifications to send and send them"""
        notifications = self.load_notifications()
        
        for notification in notifications:
            if not notification.get('is_active', True):
                continue
                
            if self.should_send_notification(notification):
                logger.info(f"Sending notification {notification['id']} to user {notification['user_id']}")
                
                # Start the notification sequence
                asyncio.create_task(self.send_notification_sequence(
                    notification['user_id'], 
                    notification['message_text']
                ))
                
                # Mark as executed
                self.mark_notification_executed(notification['id'])

# Global notification system instance
notification_system = NotificationSystem()
