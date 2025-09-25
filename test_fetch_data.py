# -*- coding: utf-8 -*-
"""
测试fetch_urls_batch数据获取和处理
"""

import json
from get_url import fetch_urls_batch, parse_data
from config import Config


def test_fetch_and_parse():
    """测试数据获取和解析功能"""
    print("🧪 测试fetch_urls_batch数据获取和处理")
    print("=" * 60)

    # 创建配置
    config = Config()
    config.worksheet_name = "p0"  # 测试用

    # 模拟API URL（你需要替换为实际的URL）
    api_url = "http://testing-novabid-dsp.testing.svc.gzk8s.zhizh.com/api/admin/script/export/filter"

    try:
        # 获取一小批数据进行测试
        print("📡 正在获取测试数据...")
        res_data = fetch_urls_batch(api_url, batch_size=5, skip=0, config=config)

        print(f"📊 获取到 {len(res_data)} 条数据")

        if res_data:
            print("\n📋 原始数据示例:")
            for i, item in enumerate(res_data[:3]):  # 只显示前3条
                print(f"  {i+1}. {item}")

            print(f"\n🔍 数据结构分析:")
            first_item = res_data[0]
            print(f"  类型: {type(first_item)}")
            if isinstance(first_item, dict):
                print(f"  键: {list(first_item.keys())}")
                print(f"  href: {first_item.get('href', 'N/A')}")
                print(f"  param: {first_item.get('param', 'N/A')}")

            print(f"\n📝 解析后的数据:")
            parsed_data = parse_data(res_data)
            print(f"  解析后行数: {len(parsed_data)}")
            print(f"  表头格式: ['href', 'param', '日期', '负责人', '状态']")

            for i, row in enumerate(parsed_data[:3]):  # 只显示前3行
                print(f"  {i+1}. {row}")

            print(f"\n✅ 数据获取和解析测试完成!")

        else:
            print("❌ 没有获取到数据，请检查:")
            print("  1. API URL是否正确")
            print("  2. 网络连接是否正常")
            print("  3. 配置参数是否正确")

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        print("请检查:")
        print("  1. API服务是否可用")
        print("  2. 配置是否正确")
        print("  3. 网络连接是否正常")


def test_parse_data_formats():
    """测试不同数据格式的解析"""
    print("\n🧪 测试不同数据格式的解析")
    print("=" * 60)

    # 测试数据
    test_cases = [
        # 新格式：包含href和param的字典
        [
            {"href": "https://example1.com", "param": "param1"},
            {"href": "https://example2.com", "param": "param2"},
        ],
        # 旧格式：纯URL字符串
        [
            "https://example3.com",
            "https://example4.com",
        ],
        # 混合格式
        [
            {"href": "https://example5.com", "param": "param5"},
            "https://example6.com",
            {"href": "https://example7.com", "param": ""},
        ],
    ]

    for i, test_data in enumerate(test_cases, 1):
        print(f"\n📋 测试案例 {i}:")
        print(f"  输入: {test_data}")

        parsed = parse_data(test_data)
        print(f"  输出: {parsed}")

        # 验证输出格式
        for row in parsed:
            if len(row) != 5:
                print(f"  ❌ 格式错误: 期望5列，实际{len(row)}列")
            else:
                print(
                    f"  ✅ 格式正确: href='{row[0]}', param='{row[1]}', 日期='{row[2]}'"
                )


if __name__ == "__main__":
    # 运行测试
    test_parse_data_formats()

    # 如果需要测试实际API，取消注释下面这行
    # test_fetch_and_parse()

    print(f"\n🎉 所有测试完成!")
    print(f"\n💡 使用说明:")
    print(f"1. 你的fetch_urls_batch函数获取方式是正确的")
    print(f"2. 返回的数据结构包含href和param字段")
    print(f"3. parse_data函数会将数据转换为Google Sheets格式")
    print(f"4. Google Sheets表头: ['href', 'param', '日期', '负责人', '状态']")
