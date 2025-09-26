import datetime
import json
import requests
import asyncio
from google_sheets import write_google_sheets
from form_checker import load_url
from config import URL_GROUPS, API_URL
from robot import Robot

robot = Robot()

# 全局统计收集器
WORKSHEET_STATS = {}


def send_summary_report():
    """发送工作表汇总报告"""
    if not WORKSHEET_STATS:
        robot.send_text("📊 任务执行完成，但没有统计数据")
        return

    # 构建汇总报告
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_lines = [
        f"📊 任务执行汇总报告",
        f"🕐 完成时间: {current_time}",
        f"━━━━━━━━━━━━━━━━━━━━━━━━",
    ]

    total_target = 0
    total_actual = 0

    # 按照执行顺序显示统计
    sequence = ["p0", "00", "p1"]
    for ws_name in sequence:
        if ws_name in WORKSHEET_STATS:
            stats = WORKSHEET_STATS[ws_name]
            total_target += stats["target_results"]
            total_actual += stats["actual_results"]

            report_lines.append(f"📋 工作表 {ws_name}:")
            report_lines.append(
                f"   目标: {stats['target_results']} | 实际: {stats['actual_results']}"
            )
            report_lines.append(
                f"   完成度: {stats['completion_rate']}% | {stats['status']}"
            )
            report_lines.append(f"   批次数: {stats['total_batches']}")
            report_lines.append("")

    # 总体统计
    overall_rate = (
        round((total_actual / total_target) * 100, 1) if total_target > 0 else 0
    )
    report_lines.extend(
        [
            f"📈 总体统计:",
            f"   总目标: {total_target} | 总实际: {total_actual}",
            f"   总完成度: {overall_rate}%",
            f"━━━━━━━━━━━━━━━━━━━━━━━━",
            f"✅ 所有工作表处理完成，请查看 https://docs.google.com/spreadsheets/d/1-WdCcC3JA2cyk6Q1gem7a2gkyDJ5RJM_esFJr724OPI/edit?gid=2015433169#gid=2015433169",
        ]
    )

    # 发送报告
    report_text = "\n".join(report_lines)
    robot.send_text(report_text)

    # 清空统计数据，为下次运行做准备
    WORKSHEET_STATS.clear()


def parse_data(urls_data):
    """
    解析URL数据，支持字符串URL或包含href和param的字典
    :param urls_data: URL列表，可以是字符串列表或字典列表
    :return: 格式化的行数据，匹配Google Sheets表头 ["href", "param", "日期", "负责人", "状态"]
    """
    print(f"解析数据: {urls_data}")
    rows = []
    today = datetime.datetime.now().strftime("%Y-%m-%d")

    for item in urls_data:
        if isinstance(item, str):
            # 兼容旧格式：纯URL字符串
            rows.append([item, "", today, "", ""])
        elif isinstance(item, dict):
            # 新格式：包含href和param的字典
            href = item.get("href", "")
            param = item.get("param", "")
            # 截取param的第一部分（逗号分隔）
            param_first = param.split(",")[0] if param else ""
            # 格式：[href, param, 日期, 负责人, 状态]
            rows.append([href, param_first, today, "", ""])
        else:
            # 未知格式，跳过
            print(f"⚠️ 跳过未知格式的数据: {item}")
            continue

    return rows


def write_batch_to_sheets_with_retry(batch_results, batch_id, config, max_retries=3):
    """
    带重试机制的批次结果写入Google Sheets
    """
    if not batch_results or not config:
        if batch_results:
            print(
                f"⚠️  第 {batch_id} 批次有 {len(batch_results)} 个结果，但配置缺失，跳过写入"
            )
        return False

    print(
        f"📝 立即写入第 {batch_id} 批次的 {len(batch_results)} 个结果到Google Sheets..."
    )

    retry_count = 0
    while retry_count < max_retries:
        try:
            sheets_config = config.get_sheets_config()
            write_google_sheets(
                parse_data(batch_results),
                sheets_config["credentials_path"],
                sheets_config["sheet_name"],
                sheets_config["worksheet_name"],
            )
            print(f"✅ 第 {batch_id} 批次结果已成功写入Google Sheets")
            return True

        except Exception as e:
            retry_count += 1
            if retry_count < max_retries:
                print(
                    f"⚠️  第 {batch_id} 批次写入失败，第 {retry_count} 次重试: {str(e)}"
                )
                import time

                time.sleep(2**retry_count)  # 指数退避：2秒、4秒、8秒
            else:
                print(
                    f"❌ 第 {batch_id} 批次写入Google Sheets失败，已重试 {max_retries} 次: {str(e)}"
                )
                return False

    return False


def fetch_urls_batch(api_url, batch_size=50, skip=0, config=None):
    """
    获取一批URL
    :param api_url: API URL
    :param batch_size: 批次大小
    :param skip: 跳过的数量
    :return: URL列表
    """
    print(f"🔗 调用API: {api_url}")
    end_date = f"{datetime.datetime.now().strftime('%Y-%m-%d')} 23:59:59"
    print(f"结束日期: {end_date}")
    data = {
        "type": "json",
        "author": "admin",
        "begin_date": f"{(datetime.datetime.now() - datetime.timedelta(days=config.cache_date_len)).strftime('%Y-%m-%d')} 00:00:00",
        "end_date": f"{datetime.datetime.now().strftime('%Y-%m-%d')} 23:59:59",
        "top_n": batch_size,
        "meet_template": 1,
        "meet_fz": 1,
        "repeat_sent": 1,
        "filter_collect": 1,
        "urls": config.req_urls,
    }

    response = requests.post(api_url, json=data)
    try:
        res_data = response.json()
    except ValueError:
        return []
    # 追加写入到res_data.json文件
    file_name = f"log/res_data_{config.worksheet_name}_{datetime.datetime.now().strftime('%Y%m%d')}.json"
    try:
        # 尝试读取现有数据
        with open(file_name, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # 如果文件不存在或格式错误，创建空列表
        existing_data = []

    # 确保existing_data是列表
    if not isinstance(existing_data, list):
        existing_data = []

    # 将新数据追加到现有数据
    if isinstance(res_data, list):
        existing_data.extend(res_data)
    else:
        existing_data.append(res_data)

    # 写回文件
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(json.dumps(existing_data, ensure_ascii=False, indent=4))
    res = [
        {
            "href": x.get("href"),
            "param": x.get("param", "").split(",")[0] if x.get("param") else "",
        }
        for x in res_data
        if isinstance(x, dict) and x.get("href")
    ]
    print(f"批次 {skip//batch_size + 1}: 获取到 {len(res)} 个URL")
    return res


def get_url(api_url, config=None):
    """
    获取URL并处理表单检查，支持循环获取直到满足最小结果数量
    :param api_url: API URL
    :param config: 配置对象，如果为None则使用默认配置
    """
    print(f"开始处理worksheet_name: {config.worksheet_name}")
    # 设置默认配置
    min_results = URL_GROUPS.get(config.worksheet_name, {}).get(
        "min_results", config.min_results
    )
    batch_size = config.batch_size if config else 50
    max_batches = config.max_batches if config else 5
    max_urls = config.max_urls if config else None

    print(f"目标：获取至少 {min_results} 个有效结果")
    print(f"配置：批次大小={batch_size}, 最大批次数={max_batches}")

    all_valid_results = []  # 存储所有有效结果（包含完整数据）
    processed_urls = set()  # 避免重复处理相同URL
    current_batch = 0
    skip = 0

    while len(all_valid_results) < min_results and current_batch < max_batches:
        current_batch += 1
        print(f"\n{'='*60}")
        print(f"第 {current_batch} 批次开始...")
        res_datas = fetch_urls_batch(api_url, batch_size, skip, config)

        if not res_datas:
            print(f"第 {current_batch} 批次没有获取到数据，停止")
            continue

        # 创建URL到完整数据的映射
        url_to_data = {item.get("href"): item for item in res_datas if item.get("href")}
        batch_urls = list(url_to_data.keys())

        if not batch_urls:
            print(f"第 {current_batch} 批次没有获取到新URL，停止")
            continue

        # 过滤掉已处理的URL
        new_urls = [u for u in batch_urls if u not in processed_urls]
        if not new_urls:
            print(f"第 {current_batch} 批次没有新URL，停止")
            continue

        # 限制URL数量（如果设置了max_urls）
        if max_urls and len(processed_urls) + len(new_urls) > max_urls:
            new_urls = new_urls[: max_urls - len(processed_urls)]

        print(f"新URL数量: {len(new_urls)}")

        # 标记为已处理
        processed_urls.update(new_urls)

        # 检查这批URL中的表单（使用多页面并行处理）
        print(f"开始检查第 {current_batch} 批次的 {len(new_urls)} 个URL...")
        # 根据URL数量动态调整并发数和页面数
        max_concurrent = min(4, max(2, len(new_urls) // 15))
        pages_per_context = min(6, max(3, len(new_urls) // max_concurrent // 3))

        print(
            f"🔧 并行配置: {max_concurrent} 上下文 × {pages_per_context} 页面 = {max_concurrent * pages_per_context} 并行度"
        )
        batch_results = asyncio.run(
            load_url(new_urls, max_concurrent, pages_per_context)
        )

        # 将找到表单的URL转换为完整数据（包含param）
        batch_results_with_data = []
        for result_url in batch_results:
            if result_url in url_to_data:
                batch_results_with_data.append(url_to_data[result_url])
            else:
                # 如果没找到对应数据，创建一个基本结构
                batch_results_with_data.append({"href": result_url, "param": ""})

        # 实时写入本批次的结果到Google Sheets（如果启用）
        write_success = True  # 默认成功，如果没有启用实时写入
        if config and config.realtime_write:
            write_success = write_batch_to_sheets_with_retry(
                batch_results_with_data, current_batch, config, config.write_retry
            )
        elif batch_results_with_data:
            print(
                f"📋 第 {current_batch} 批次找到 {len(batch_results_with_data)} 个结果（实时写入已禁用）"
            )

        # 添加到总结果中（用于统计）
        all_valid_results.extend(batch_results_with_data)

        print(f"第 {current_batch} 批次完成:")
        print(f"  - 检查URL数: {len(new_urls)}")
        print(f"  - 有效结果: {len(batch_results)}")
        print(f"  - 累计有效结果: {len(all_valid_results)}")
        print(f"  - 目标进度: {len(all_valid_results)}/{min_results}")

        if config and config.realtime_write:
            if batch_results and write_success:
                print(f"  - ✅ 本批次结果已实时写入Google Sheets")
            elif batch_results and not write_success:
                print(f"  - ❌ 本批次结果写入Google Sheets失败，已保存本地备份")
        elif batch_results:
            print(f"  - 📋 本批次结果已缓存，将在最后统一写入")

        # 如果已达到目标，提前结束
        if len(all_valid_results) >= min_results:
            print(f"✅ 已达到目标数量 {min_results}，停止获取")
            break

        # 如果设置了max_urls限制且已达到，停止
        if max_urls and len(processed_urls) >= max_urls:
            print(f"✅ 已达到最大URL限制 {max_urls}，停止获取")
            break

        # 准备下一批次
        skip += batch_size

        # 添加短暂延迟避免请求过快
        import time

        time.sleep(1)

    print(f"\n{'='*60}")
    print(f"🎯 最终结果:")
    print(f"  - 总批次数: {current_batch}")
    print(f"  - 检查URL总数: {len(processed_urls)}")
    print(f"  - 有效结果数: {len(all_valid_results)}")
    print(
        f"  - 目标完成度: {len(all_valid_results)}/{min_results} ({len(all_valid_results)/min_results*100:.1f}%)"
    )

    # 根据配置决定是否需要最终写入
    if config and config.realtime_write:
        # 实时写入模式：结果已经在每批次完成后写入
        if all_valid_results:
            print(f"✅ 所有 {len(all_valid_results)} 个结果已实时写入Google Sheets")
        else:
            print("⚠️  没有找到任何有效结果")
    else:
        # 批量写入模式：在最后统一写入所有结果
        if all_valid_results:
            print(f"📝 开始写入所有 {len(all_valid_results)} 个结果到Google Sheets...")
            try:
                if config:
                    sheets_config = config.get_sheets_config()
                    write_google_sheets(
                        parse_data(all_valid_results),
                        sheets_config["credentials_path"],
                        sheets_config["sheet_name"],
                        sheets_config["worksheet_name"],
                    )
                else:
                    write_google_sheets(parse_data(all_valid_results))
                print(f"✅ 所有 {len(all_valid_results)} 个结果已成功写入Google Sheets")
            except Exception as e:
                print(f"❌ 批量写入Google Sheets失败: {str(e)}")

        else:
            print("⚠️  没有找到任何有效结果")

    # 收集当前工作表的统计信息
    if config and hasattr(config, "worksheet_name"):
        current_ws = config.worksheet_name
        WORKSHEET_STATS[current_ws] = {
            "worksheet_name": current_ws,
            "target_results": min_results,
            "actual_results": len(all_valid_results),
            "total_batches": current_batch,
            "completion_rate": (
                round((len(all_valid_results) / min_results) * 100, 1)
                if min_results > 0
                else 0
            ),
            "status": (
                "✅ 完成" if len(all_valid_results) >= min_results else "⚠️ 未达标"
            ),
        }

    # 检查是否是手动指定的单个工作表执行
    if (
        config
        and hasattr(config, "run_single_worksheet")
        and config.run_single_worksheet
    ):
        # 手动指定单个工作表，直接结束，不进行序列处理
        print(f"✅ 手动执行工作表 '{config.worksheet_name}' 完成")
        return all_valid_results

    # 按顺序依次执行 [00, p0, p1]
    if config:
        sequence = ["00", "p0", "p1"]
        current_ws = getattr(config, "worksheet_name", None)
        if current_ws in sequence:
            if current_ws == sequence[-1]:
                # 最后一个工作表完成，发送汇总报告
                send_summary_report()
                return all_valid_results
            # 切换到下一个 worksheet
            next_index = sequence.index(current_ws) + 1
            next_ws = sequence[next_index]
            # 更新配置中的目标 worksheet 及其相关参数
            config.worksheet_name = next_ws
            config.req_urls = URL_GROUPS.get(next_ws, {}).get("urls", "")
            # 若有为不同表定义的最小结果阈值，则同步更新
            config.min_results = URL_GROUPS.get(next_ws, {}).get(
                "min_results", config.min_results
            )
            # 递归调用处理下一个工作表
            get_url(API_URL, config)
        else:
            # 未识别的 worksheet，直接结束
            return all_valid_results
    else:
        # 无配置对象，无法串行调度，直接结束
        return all_valid_results


if __name__ == "__main__":
    from config import Config

    # 使用统一的配置管理
    config = Config()

    api_url = "http://testing-novabid-dsp.testing.svc.gzk8s.zhizh.com/api/admin/script/export/filter"
    get_url(api_url, config)
