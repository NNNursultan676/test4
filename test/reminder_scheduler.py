
import asyncio
import logging
import pytz
from datetime import datetime
from booking_reminders import booking_reminder_system

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def reminder_scheduler():
    """Main scheduler loop that checks for booking reminders every minute"""
    logger.info("Starting booking reminder scheduler with UTC+5 timezone...")
    
    while True:
        try:
            # Get current time in UTC+5 (Kazakhstan timezone)
            almaty_tz = pytz.timezone('Asia/Almaty')
            current_time = datetime.now(almaty_tz)
            
            logger.info(f"Checking booking reminders at {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            
            # Check and send reminders
            await booking_reminder_system.check_and_send_reminders()
            
            # Wait for 60 seconds before next check
            await asyncio.sleep(60)
            
        except Exception as e:
            logger.error(f"Error in reminder scheduler: {e}")
            import traceback
            traceback.print_exc()
            # Wait a bit before retrying
            await asyncio.sleep(60)

if __name__ == "__main__":
    try:
        asyncio.run(reminder_scheduler())
    except KeyboardInterrupt:
        logger.info("Reminder scheduler stopped")
    except Exception as e:
        logger.error(f"Fatal error in reminder scheduler: {e}")
