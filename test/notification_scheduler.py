
import asyncio
import logging
from datetime import datetime
from notifications import notification_system

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def notification_scheduler():
    """Main scheduler loop that checks for notifications every minute"""
    logger.info("Starting notification scheduler...")
    
    while True:
        try:
            current_time = datetime.now()
            logger.info(f"Checking notifications at {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Check and send notifications
            await notification_system.check_and_send_notifications()
            
            # Wait for 60 seconds before next check
            await asyncio.sleep(60)
            
        except Exception as e:
            logger.error(f"Error in notification scheduler: {e}")
            # Wait a bit before retrying
            await asyncio.sleep(60)

if __name__ == "__main__":
    try:
        asyncio.run(notification_scheduler())
    except KeyboardInterrupt:
        logger.info("Notification scheduler stopped")
    except Exception as e:
        logger.error(f"Fatal error in notification scheduler: {e}")
