# -*- coding: utf-8 -*-

import argparse
import logging

# ===== 默认配置参数 =====
# 接口地址
API_URL = "http://testing-novabid-dsp.testing.svc.gzk8s.zhizh.com/api/admin/script/export/filter"

# 调度器默认配置
DEFAULT_SCHEDULE_TIME = "08:00"
# 查询n天前至今的数据（默认2天）
DEFAULT_CACHE_DATE_LEN = 2

DEFAULT_ROBOT = False

# Google Sheets默认配置
DEFAULT_CREDENTIALS_PATH = "credentials.json"
DEFAULT_SHEET_NAME = "TSTASK"
DEFAULT_WORKSHEET_NAME = "00"

# 表单检查默认配置
DEFAULT_MAX_URLS = None
DEFAULT_MIN_RESULTS = 10
DEFAULT_BATCH_SIZE = 50
DEFAULT_MAX_BATCHES = 5
DEFAULT_TIMEOUT = 15000
DEFAULT_HEADLESS = True
DEFAULT_REALTIME_WRITE = True
DEFAULT_WRITE_RETRY = 2

# 日志默认配置
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_FILE = "log/app.log"

# URL映射表
URL_GROUPS = {
    "00": {
        "urls": "good.realtimesinfo.com,bj1.puzzgo41.lol/?portal=1777,office.puzzlegamey.com,little.puzzlegamey.com,bj6.puzzgo41.lol/?portal=1809",
        "min_results": 90,
    },
    "p0": {
        "urls": "edge.sassostyle.com,bj1.szgame1.lol/?portal=1964,bj17.puzzgo41.lol/?portal=1909,bj18.puzzgo41.lol/?portal=1910,bj2.puzzgo41.lol/?portal=1848,ate.dayheadlines.com,believe.puzzlegamey.com,ent.dayheadlines.com,hall.puzzlegamey.com,puzzle.pbfhp.com,nova.puzzlegamey.com,flynix.top,buzz.dayheadlines.com,date.dayheadlines.com,mdfp.ventoroa.com,pure.sassostyle.com,fancy.puzzlegamey.com,top.vwbvapxxx9l.com,trend.sassostyle.com,dave.puzzlegamey.com,glow.joysfull.com,go.pbfhp.com,hiap.ventoroa.com,voice.karationews.com,cosa.ventoroa.com,book.karationews.com,bj2.puzzgo12.lol/?portal=1804,hear.karationews.com,wine.karationews.com",
        "min_results": 90,
    },
    "p1": {
        "urls": "bj3.puzzgo12.lol/?portal=1978,bj5.puzzgo12.lol/?portal=1980,dazzle.joysfull.com,fast.kwbvapxxx7w.com,hyntra.top,match.pbfhp.com,serene.joysfull.com,snap.kwbvapxxx7w.com,blue.weixiangltd.net,pfht.miranovaq.com,pink.wiuir.top,sdef.miranovaq.com,wen.realtimesinfo.com,white.fkiuz.top,goplay.pbfhp.co,strategy.pbfhp.com,light.dayheadlines.com,spot.dayheadlines.com,well.gamepean.top,good.gamepean.top,win.pcllwoscoddl.com,zen.sassostyle.com,add.joysfull.com,go.pcllwoscoddl.com,link.bdasdvsdadsx8w.com,easy.bdasdvsdadsx8w.com,mellow.joysfull.com,dream.pcllwoscoddl.com,bit.vwbvapxxx9l.com",
        "min_results": 60,
    },
}


def create_common_parser():
    """创建通用的参数解析器"""
    parser = argparse.ArgumentParser(description="Form Checker & Google Sheets Manager")

    # 调度器相关参数
    scheduler_group = parser.add_argument_group("调度器参数")
    scheduler_group.add_argument(
        "--time",
        type=str,
        default=DEFAULT_SCHEDULE_TIME,
        help=f"每天执行的时间，格式：HH:MM （默认: {DEFAULT_SCHEDULE_TIME}）",
    )
    scheduler_group.add_argument(
        "--run-now", action="store_true", help="立即执行一次任务（测试用）"
    )
    scheduler_group.add_argument(
        "--daemon", action="store_true", help="以守护进程模式运行"
    )

    # Google Sheets相关参数
    sheets_group = parser.add_argument_group("Google Sheets参数")
    sheets_group.add_argument(
        "--credentials",
        type=str,
        default=DEFAULT_CREDENTIALS_PATH,
        help=f"Google Service Account凭证文件路径（默认: {DEFAULT_CREDENTIALS_PATH}）",
    )
    sheets_group.add_argument(
        "--sheet-name",
        type=str,
        default=DEFAULT_SHEET_NAME,
        help=f"Google Sheet文件名（默认: {DEFAULT_SHEET_NAME}）",
    )
    sheets_group.add_argument(
        "--worksheet-name",
        type=str,
        default=DEFAULT_WORKSHEET_NAME,
        help=f"工作表名称（默认: {DEFAULT_WORKSHEET_NAME}）",
    )

    sheets_group.add_argument(
        "--cache-date-len",
        type=int,
        default=DEFAULT_CACHE_DATE_LEN,
        help=f"缓存日期长度（默认: {DEFAULT_CACHE_DATE_LEN}）",
    )
    # 表单检查相关参数
    checker_group = parser.add_argument_group("表单检查参数")
    checker_group.add_argument(
        "--max-urls",
        type=int,
        default=DEFAULT_MAX_URLS,
        help="最大检查URL数量（用于测试）",
    )
    checker_group.add_argument(
        "--min-results",
        type=int,
        default=DEFAULT_MIN_RESULTS,
        help=f"最少需要的有效结果数量（默认: {DEFAULT_MIN_RESULTS}）",
    )
    checker_group.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        help=f"每次获取的URL批次大小（默认: {DEFAULT_BATCH_SIZE}）",
    )
    checker_group.add_argument(
        "--max-batches",
        type=int,
        default=DEFAULT_MAX_BATCHES,
        help=f"最大批次数量，防止无限循环（默认: {DEFAULT_MAX_BATCHES}）",
    )
    checker_group.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f"页面加载超时时间（毫秒，默认: {DEFAULT_TIMEOUT}）",
    )
    checker_group.add_argument(
        "--headless",
        action="store_true",
        default=DEFAULT_HEADLESS,
        help=f"使用无头浏览器模式（默认: {'启用' if DEFAULT_HEADLESS else '禁用'}）",
    )
    checker_group.add_argument(
        "--realtime-write",
        action="store_true",
        default=DEFAULT_REALTIME_WRITE,
        help=f"实时写入Google Sheets，每批次完成后立即写入（默认: {'启用' if DEFAULT_REALTIME_WRITE else '禁用'}）",
    )
    checker_group.add_argument(
        "--write-retry",
        type=int,
        default=DEFAULT_WRITE_RETRY,
        help=f"Google Sheets写入失败重试次数（默认: {DEFAULT_WRITE_RETRY}）",
    )

    # 日志相关参数
    log_group = parser.add_argument_group("日志参数")
    log_group.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default=DEFAULT_LOG_LEVEL,
        help=f"日志级别（默认: {DEFAULT_LOG_LEVEL}）",
    )
    log_group.add_argument(
        "--log-file",
        type=str,
        default=DEFAULT_LOG_FILE,
        help=f"日志文件路径（默认: {DEFAULT_LOG_FILE}）",
    )

    return parser


def setup_logging(args):
    """根据参数设置日志"""
    log_level = getattr(logging, args.log_level.upper())

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(args.log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


class Config:
    """配置管理类"""

    def __init__(self, args=None):
        if args is None:
            parser = create_common_parser()
            args = parser.parse_args()

        self.args = args

        # 调度器配置
        self.schedule_time = args.time
        self.run_now = args.run_now
        self.daemon_mode = args.daemon

        self.cache_date_len = args.cache_date_len

        # Google Sheets配置
        self.credentials_path = args.credentials
        self.sheet_name = args.sheet_name
        self.worksheet_name = args.worksheet_name
        self.req_urls = URL_GROUPS.get(args.worksheet_name, {}).get("urls", "")

        # 表单检查配置
        self.max_urls = args.max_urls
        self.min_results = args.min_results
        self.batch_size = args.batch_size
        self.max_batches = args.max_batches
        self.timeout = args.timeout
        self.headless = args.headless
        self.realtime_write = args.realtime_write
        self.write_retry = args.write_retry

        # 日志配置
        self.log_level = args.log_level
        self.log_file = args.log_file

        # 设置日志
        setup_logging(args)

    def get_sheets_config(self):
        """获取Google Sheets配置"""
        return {
            "credentials_path": self.credentials_path,
            "sheet_name": self.sheet_name,
            "worksheet_name": self.worksheet_name,
        }

    def get_checker_config(self):
        """获取表单检查配置"""
        return {
            "max_urls": self.max_urls,
            "min_results": self.min_results,
            "batch_size": self.batch_size,
            "max_batches": self.max_batches,
            "timeout": self.timeout,
            "headless": self.headless,
            "realtime_write": self.realtime_write,
            "write_retry": self.write_retry,
        }


if __name__ == "__main__":
    # 测试配置模块
    config = Config()
    print("调度时间:", config.schedule_time)
    print("Google Sheets配置:", config.get_sheets_config())
    print("表单检查配置:", config.get_checker_config())
