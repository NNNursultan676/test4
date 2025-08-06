
import os

# Telegram Bot Configuration
BOT_TOKEN = "7836396334:AAEb8eqj56RHPZKwxNt_8G6RnBuJIdS7FCw"
GROUP_ID = -1002723413852
THREAD_ID = 4  # Thread ID for notifications (as integer)
NOTIFICATION_THREAD_ID = 4  # Thread ID for recurring notifications (as integer)

# Alternative way to load from environment variables:
# BOT_TOKEN = os.getenv("BOT_TOKEN")
# GROUP_ID = int(os.getenv("GROUP_ID"))

# JSON file paths
USERS_JSON_PATH = "data/users.json"
BOOKINGS_JSON_PATH = "data/bookings.json"
NOTIFICATIONS_JSON_PATH = "data/notifications.json"

# Database URL for future PostgreSQL migration
DATABASE_URL = "url://..."  # on future
