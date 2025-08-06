
import asyncio
import logging
import pytz
from datetime import datetime
from notifications import notification_system

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def notification_scheduler():
    """Main scheduler loop that checks for notifications every minute"""
    logger.info("Starting notification scheduler with UTC+5 timezone (Asia/Almaty)...")
    
    while True:
        try:
            # Get current time in UTC+5 (Kazakhstan timezone)
            almaty_tz = pytz.timezone('Asia/Almaty')
            current_time = datetime.now(almaty_tz)
            current_weekday = current_time.weekday() + 1  # Monday = 1, Sunday = 7
            
            logger.info(f"Checking notifications at {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')} (weekday: {current_weekday})")
            
            # Check and send notifications
            await notification_system.check_and_send_notifications()
            
            # Wait for 60 seconds before next check
            await asyncio.sleep(60)
            
        except Exception as e:
            logger.error(f"Error in notification scheduler: {e}")
            import traceback
            traceback.print_exc()
            # Wait a bit before retrying
            await asyncio.sleep(60)

if __name__ == "__main__":
    try:
        asyncio.run(notification_scheduler())
    except KeyboardInterrupt:
        logger.info("Notification scheduler stopped")
    except Exception as e:
        logger.error(f"Fatal error in notification scheduler: {e}")
