import pytz

from apscheduler.schedulers.asyncio import AsyncIOScheduler
# from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.schedulers.blocking import BlockingScheduler
from chain_monitor.configurations.logging import setup_logging
from chain_monitor.configurations.redis import setup_redis
from chain_monitor.configurations.logger import get_logger

logger = get_logger(__name__)

_app_initialized = False
scheduler = None


def initialize(force=False, force_logging_stdout=False):
    """
    Configure stuff on configurations startup
    """
    global _app_initialized
    if _app_initialized and not force:
        return

    setup_logging(force_logging_stdout)
    setup_redis()

    global scheduler
    time_zone = pytz.timezone('Asia/Shanghai')
    scheduler = AsyncIOScheduler(timezone=time_zone)

    logger.debug('App initialized')

    _app_initialized = True


initialize()
