# -*- coding: utf-8 -*-

import schedule
import time
import logging
import datetime
from get_url import get_url
from robot import Robot
from config import API_URL

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("log/scheduler.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
robot = Robot()


# API_URL = "http://127.0.0.1:56337/response.json"
def run_daily_task(config=None):
    """执行每日任务"""
    try:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.info(f"开始执行每日任务 - {current_time}")

        robot.send_text(f"开始执行每日任务 - {current_time}")
        # 调用主要的处理函数
        get_url(API_URL, config)

        logging.info(f"每日任务执行完成 - {current_time}")

    except Exception as e:
        logging.error(f"每日任务执行失败: {str(e)}", exc_info=True)


def setup_scheduler(run_time="07:00", config=None):
    """
    设置定时任务调度器
    :param run_time: 执行时间，格式为 "HH:MM"，默认上午9点
    :param config: 配置对象
    """
    logging.info(f"设置定时任务，每天 {run_time} 执行")

    # 设置每天在指定时间执行任务
    schedule.every().day.at(run_time).do(run_daily_task, config)  # 每30分钟


def run_scheduler():
    """运行调度器主循环"""
    logging.info("定时任务调度器启动")
    logging.info("按 Ctrl+C 停止调度器")

    try:
        while True:
            # 检查是否有待执行的任务
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次

    except KeyboardInterrupt:
        logging.info("收到停止信号，正在关闭调度器 ...")
    except Exception as e:
        logging.error(f"调度器运行出错: {str(e)}", exc_info=True)
    finally:
        logging.info("定时任务调度器已停止")


def run_once_now(config=None):
    """立即执行一次任务（用于测试）"""
    logging.info("立即执行一次任务（测试模式）")
    run_daily_task(config)


if __name__ == "__main__":
    from config import Config

    # 使用统一的配置管理
    config = Config()

    if config.run_now:
        # 立即执行一次
        run_once_now(config)
    else:
        # 设置定时任务
        setup_scheduler(config.schedule_time, config)

        if config.daemon_mode:
            logging.info("以守护进程模式运行")
            logging.info("注意：真正的守护进程需要配合 systemd、nohup 或 screen 等工具")
            logging.info(
                f"建议使用: nohup python scheduler.py --time {config.schedule_time} &"
            )

        # 运行调度器
        run_scheduler()
