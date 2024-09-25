import pytz

from apscheduler.schedulers.blocking import BlockingScheduler
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
    pacific_timezone = pytz.timezone('Asia/Shanghai')
    scheduler = BlockingScheduler(timezone=pacific_timezone)

    logger.debug('App initialized')

    _app_initialized = True


initialize()
