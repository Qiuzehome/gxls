# -*- coding: utf-8 -*-

import gspread
import logging
import argparse

# --- 配置日志 ---
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class GoogleSheetsManager:
    def __init__(self, credentials_path, sheet_name):
        """
        初始化 Google Sheets 管理器
        :param credentials_path: Google Service Account 的 JSON 凭证文件路径
        :param sheet_name: 要操作的 Google Sheet 文件名
        """
        try:
            # 使用服务账号凭证进行授权
            self.gc = gspread.service_account(filename=credentials_path)
            # 打开指定的 Google Sheet
            self.spreadsheet = self.gc.open(sheet_name)
            logging.info(f"成功连接到 Google Sheet: '{sheet_name}'")
        except gspread.exceptions.SpreadsheetNotFound:
            logging.error(f"错误：找不到名为 '{sheet_name}' 的 Google Sheet。")
            logging.warning("请确保您已经将该 Sheet 分享给了您的服务账号邮箱。")
            self.spreadsheet = None
        except Exception as e:
            logging.error(f"连接 Google Sheets 时发生错误: {e}", exc_info=True)
            self.spreadsheet = None

    def get_or_create_worksheet(self, worksheet_name):
        """获取或创建一个工作表(worksheet)"""
        if not self.spreadsheet:
            return None
        try:
            # 尝试获取工作表
            worksheet = self.spreadsheet.worksheet(worksheet_name)
            logging.info(f"找到现有的工作表: '{worksheet_name}'")
            return worksheet
        except gspread.exceptions.WorksheetNotFound:
            # 如果找不到，则创建一个新的
            logging.info(f"工作表 '{worksheet_name}' 不存在，正在创建... ")
            worksheet = self.spreadsheet.add_worksheet(
                title=worksheet_name, rows="100", cols="20"
            )
            return worksheet

    def write_data(self, worksheet, data):
        """
        向工作表写入数据。这会覆盖所有现有数据。
        :param worksheet: gspread 的 Worksheet 对象
        :param data: 一个二维列表，例如 [['姓名', '年龄'], ['张三', 30]]
        """
        if not worksheet:
            logging.warning("Worksheet 对象无效，无法写入数据。")
            return
        try:
            worksheet.clear()  # 清空工作表
            worksheet.update(data)  # 写入所有数据
            logging.info(f"成功向 '{worksheet.title}' 写入 {len(data)} 行数据。")
        except Exception as e:
            logging.error(f"写入数据失败: {e}", exc_info=True)

    def append_data(self, worksheet, data):
        """
        向工作表追加数据，不会覆盖现有数据。
        :param worksheet: gspread 的 Worksheet 对象
        :param data: 一个二维列表，例如 [['张三', 30], ['李四', 25]]
        """
        if not worksheet:
            logging.warning("Worksheet 对象无效，无法追加数据。")
            return
        try:
            # 检查是否需要添加表头
            existing_data = worksheet.get_all_values()
            if not existing_data:
                # 如果工作表为空，先添加表头
                header = ["href", "param", "日期", "负责人", "状态"]
                worksheet.append_row(header)
                logging.info("添加表头到空工作表")

            # 追加数据行
            worksheet.append_rows(data)
            logging.info(f"成功向 '{worksheet.title}' 追加 {len(data)} 行数据。")
        except Exception as e:
            logging.error(f"追加数据失败: {e}", exc_info=True)

    def read_data(self, worksheet):
        """从工作表读取所有数据"""
        if not worksheet:
            logging.warning("Worksheet 对象无效，无法读取数据。")
            return None
        try:
            records = worksheet.get_all_records()  # 以字典列表形式获取数据
            logging.info(f"从 '{worksheet.title}' 读取到 {len(records)} 条记录。")
            return records
        except Exception as e:
            logging.error(f"读取数据失败: {e}", exc_info=True)
            return None


def write_google_sheets(
    data_list,
    credentials_path="credentials.json",
    sheet_name="TSTASK",
    worksheet_name="worksheet",
):
    """主执行函数"""
    # --- 2. 初始化管理器 ---
    manager = GoogleSheetsManager(credentials_path, sheet_name)

    if manager.spreadsheet:
        # --- 3. 获取或创建工作表 ---
        worksheet = manager.get_or_create_worksheet(worksheet_name)

        # --- 4. 追加数据 ---
        logging.info("使用追加模式写入数据...")
        manager.append_data(worksheet, data_list)

        # --- 5. 读取数据 ---
        logging.info("\n--- 读取表格数据 ---")
        read_records = manager.read_data(worksheet)
        if read_records:
            for record in read_records:
                print(record)


def main():
    """命令行入口函数"""
    from config import Config

    # 使用统一的配置管理
    config = Config()
    sheets_config = config.get_sheets_config()

    # 调用主函数
    write_google_sheets(
        [],
        sheets_config["credentials_path"],
        sheets_config["sheet_name"],
        sheets_config["worksheet_name"],
    )


if __name__ == "__main__":
    main()
