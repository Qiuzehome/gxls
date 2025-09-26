# -*- coding: utf-8 -*-

import gspread
import logging

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
        向指定的工作表追加数据，自动去重（基于href字段）
        :param worksheet: gspread 的 Worksheet 对象
        :param data: 一个二维列表，例如 [['href1', 'param1', '2025-09-26', '', '']]
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
                existing_hrefs = set()  # 空表，没有现有的href
            else:
                # 提取现有数据中的href列（假设href是第一列）
                existing_hrefs = set()
                for row in existing_data[1:]:  # 跳过表头
                    if row and len(row) > 0:  # 确保行不为空且有数据
                        existing_hrefs.add(row[0])  # 第一列是href
                logging.info(f"工作表中已存在 {len(existing_hrefs)} 个href记录")

            # 过滤重复数据
            new_data = []
            duplicate_count = 0
            for row in data:
                if row and len(row) > 0:  # 确保行不为空且有数据
                    href = row[0]  # 第一列是href
                    if href not in existing_hrefs:
                        new_data.append(row)
                        existing_hrefs.add(href)  # 添加到已存在集合中，避免本批次内重复
                    else:
                        duplicate_count += 1

            # 追加新数据
            if new_data:
                worksheet.append_rows(new_data)
                logging.info(
                    f"成功向 '{worksheet.title}' 追加 {len(new_data)} 行新数据"
                )

            if duplicate_count > 0:
                logging.info(f"跳过 {duplicate_count} 行重复数据（href已存在）")

            logging.info(
                f"数据处理完成：新增 {len(new_data)} 行，跳过重复 {duplicate_count} 行"
            )

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
