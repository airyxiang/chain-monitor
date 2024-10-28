import asyncio

from chain_monitor.configurations.initialization import scheduler

from chain_monitor.configurations.logger import get_logger
from chain_monitor.service.monitor_eth_task import monitor_supplemented_eth

logger = get_logger(__name__)


# @scheduler.scheduled_job('interval', minutes=1)
# def cron_eth_monitor():
#     logger.info('Process eth monitor')
#     monitor_supplemented_eth()


def run():
    logger.info("Starting scheduler")
    scheduler.add_job(monitor_supplemented_eth, 'interval', minutes=1)
    scheduler.start()
    asyncio.get_event_loop().run_forever()
    logger.info("Scheduler started")
