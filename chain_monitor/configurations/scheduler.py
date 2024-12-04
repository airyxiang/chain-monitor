from chain_monitor.configurations.initialization import scheduler

from chain_monitor.configurations.logger import get_logger
from chain_monitor.service.monitor_eth_task import monitor_supplemented_eth, monitor_mint_eth
from chain_monitor.service.monitor_stu_balackelist import monitoring_blacklisted, monitoring_user_status
from chain_monitor.service.monitor_stusdt_balance import monitor_eth_balance, monitor_tron_balance, monitor_aave_balance
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


@scheduler.scheduled_job('interval', minutes=10)
def cron_eth_mint():
    logger.info('Process eth mint')
    monitor_mint_eth()


@scheduler.scheduled_job('interval', minutes=5)
def cron_monitoring_blacklisted():
    logger.info('Process stusdt blacklist')
    monitoring_blacklisted()


@scheduler.scheduled_job('cron', hour='0', minute=0)
def cron_monitoring_stusdt_status():
    logger.info('Process stusdt status')
    monitoring_user_status()


@scheduler.scheduled_job('cron', hour='2', minute=0)
def cron_monitoring_stusdt_eth_and_tron_balance():
    logger.info('Process eth and tron balance')
    monitor_eth_balance()
    monitor_tron_balance()


@scheduler.scheduled_job('cron', hour='0', minute=0)
def cron_monitoring_stusdt_aave_balance():
    logger.info('Process aave balance')
    monitor_aave_balance()


def run():
    logger.info("Starting scheduler")
    scheduler.start()
    logger.info("Scheduler started")
