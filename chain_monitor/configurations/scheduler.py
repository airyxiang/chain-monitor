from chain_monitor.configurations.initialization import scheduler

from chain_monitor.configurations.logger import get_logger
from chain_monitor.service.monitor_eth_service import monitor_supplemented_eth

logger = get_logger(__name__)


@scheduler.scheduled_job('cron', minute='*/30')
def cron_heartbeat_task():
    logger.info('Launching heartbeat task')


@scheduler.scheduled_job('cron', day='*')
def cron_eth_monitor():
    logger.info('Process eth monitor')
    monitor_supplemented_eth()


def run():
    logger.info("Starting scheduler")
    scheduler.start()
