from chain_monitor.configurations.initialization import scheduler

from chain_monitor.configurations.logger import get_logger

logger = get_logger(__name__)


@scheduler.scheduled_job('cron', minute='*/30')
def cron_heartbeat_task():
    logger.info('Launching heartbeat task')


def run():
    logger.info("Starting scheduler")
    scheduler.start()
