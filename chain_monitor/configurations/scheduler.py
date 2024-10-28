from chain_monitor.configurations.initialization import scheduler

from chain_monitor.configurations.logger import get_logger
from chain_monitor.service.monitor_eth_task import monitor_supplemented_eth
from chain_monitor.service.usdd_balance_monitor import monitor_balance

logger = get_logger(__name__)


@scheduler.scheduled_job('cron', hour='0, 4, 8, 12, 16, 20', minute=0)
def cron_eth_monitor():
    logger.info('Process eth monitor')
    monitor_supplemented_eth()


@scheduler.scheduled_job('cron', hour='11', minute=0)
def cron_usdd_balance():
    logger.info('Process usdd balance monitor')
    monitor_balance()


def run():
    logger.info("Starting scheduler")
    scheduler.start()
    logger.info("Scheduler started")
