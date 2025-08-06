
import os
import json
import logging
import asyncio
import requests
import pytz
from datetime import datetime, timedelta
from config import BOT_TOKEN

logger = logging.getLogger(__name__)

class BookingReminderSystem:
    def __init__(self):
        self.reminders_path = "data/booking_reminders.json"
        
    def load_bookings(self):
        """Load bookings from JSON file"""
        try:
            with open("data/bookings.json", 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def load_reminders(self):
        """Load sent reminders from JSON file"""
        try:
            with open(self.reminders_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_reminders(self, reminders):
        """Save sent reminders to JSON file"""
        try:
            os.makedirs(os.path.dirname(self.reminders_path), exist_ok=True)
            with open(self.reminders_path, 'w') as f:
                json.dump(reminders, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error saving reminders: {e}")
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
                logger.info(f"Reminder sent to user {user_id}")
                return result['result']['message_id']
            else:
                logger.error(f"Failed to send reminder: {result}")
            return None
        except Exception as e:
            logger.error(f"Error sending reminder message: {e}")
            return None

    def should_send_reminder(self, booking, reminders):
        """Check if reminder should be sent for this booking"""
        # Get current time in UTC+5
        almaty_tz = pytz.timezone('Asia/Almaty')
        now = datetime.now(almaty_tz)
        
        # Parse booking date and time
        try:
            booking_date = datetime.strptime(booking['date'], '%Y-%m-%d').date()
            booking_time = datetime.strptime(booking['start_time'], '%H:%M').time()
            
            # Create full booking datetime in UTC+5
            booking_datetime = almaty_tz.localize(
                datetime.combine(booking_date, booking_time)
            )
            
            # Calculate 15 minutes before booking
            reminder_time = booking_datetime - timedelta(minutes=15)
            
            # Check if we should send reminder now (within 1 minute window)
            time_diff = abs((now - reminder_time).total_seconds())
            
            if time_diff > 60:  # Not within 1-minute window
                return False
                
            # Check if booking is confirmed and in the future
            if booking['status'] != 'confirmed':
                return False
                
            if booking_datetime <= now:
                return False
                
            # Check if reminder already sent
            booking_id = booking.get('id', f"{booking['telegram_id']}_{booking['date']}_{booking['start_time']}")
            
            for reminder in reminders:
                if reminder.get('booking_id') == booking_id:
                    return False
                    
            logger.info(f"Should send reminder for booking {booking_id} at {now}")
            return True
            
        except Exception as e:
            logger.error(f"Error checking reminder for booking {booking}: {e}")
            return False

    def mark_reminder_sent(self, booking):
        """Mark reminder as sent for this booking"""
        reminders = self.load_reminders()
        
        # Get current time in UTC+5
        almaty_tz = pytz.timezone('Asia/Almaty')
        now = datetime.now(almaty_tz)
        
        booking_id = booking.get('id', f"{booking['telegram_id']}_{booking['date']}_{booking['start_time']}")
        
        reminder_record = {
            'booking_id': booking_id,
            'user_id': booking['telegram_id'],
            'sent_at': now.isoformat(),
            'booking_date': booking['date'],
            'booking_time': booking['start_time'],
            'room_name': booking['room_name']
        }
        
        reminders.append(reminder_record)
        self.save_reminders(reminders)
        logger.info(f"Marked reminder as sent for booking {booking_id}")

    async def check_and_send_reminders(self):
        """Check for bookings that need reminders and send them"""
        bookings = self.load_bookings()
        reminders = self.load_reminders()
        
        for booking in bookings:
            if self.should_send_reminder(booking, reminders):
                user_name = booking.get('user_name', 'Пользователь')
                room_name = booking.get('room_name', 'Переговорная')
                
                message = (
                    f"🔔 <b>Напоминание о бронировании</b>\n\n"
                    f"👋 Здравствуйте, {user_name}!\n\n"
                    f"⏰ Через 15 минут начинается ваша бронь:\n"
                    f"🏢 Комната: <b>{room_name}</b>\n"
                    f"📅 Дата: <b>{booking['date']}</b>\n"
                    f"🕐 Время: <b>{booking['start_time']} - {booking['end_time']}</b>\n"
                )
                
                if booking.get('purpose'):
                    message += f"📝 Цель: <b>{booking['purpose']}</b>\n"
                
                message += f"\n💡 Не забудьте подготовиться к встрече!"
                
                # Send reminder
                sent = await self.send_telegram_message(booking['telegram_id'], message)
                
                if sent:
                    self.mark_reminder_sent(booking)

# Global reminder system instance
booking_reminder_system = BookingReminderSystem()
