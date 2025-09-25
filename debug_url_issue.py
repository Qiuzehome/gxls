# -*- coding: utf-8 -*-
"""
调试URL参数传递问题
"""


def debug_function_calls():
    """调试函数调用链"""
    print("🔍 调试URL参数传递")
    print("=" * 60)

    # 模拟正确的API URL
    api_url = "http://testing-novabid-dsp.testing.svc.gzk8s.zhizh.com/api/admin/script/export/filter"

    print(f"1. scheduler.py中的API_URL: {api_url}")
    print(f"2. 调用: get_url(API_URL, config)")
    print(f"3. get_url函数接收的api_url参数: {api_url}")
    print(f"4. 调用: fetch_urls_batch(api_url, batch_size, skip, config)")
    print(f"5. fetch_urls_batch函数接收的api_url参数: {api_url}")
    print(f"6. 执行: requests.post(api_url, json=data)")

    print("\n✅ 修复后的调用链应该保持API URL不变")

    # 检查可能的问题
    print(f"\n🚨 之前的问题可能原因:")
    print(f"1. 变量名冲突：函数参数'url'与局部变量'url'冲突")
    print(f"2. 在处理URL列表时，API URL被意外覆盖")

    print(f"\n🔧 修复措施:")
    print(f"1. 将函数参数名从'url'改为'api_url'，避免冲突")
    print(f"2. 将局部变量'url'改为'result_url'，避免冲突")
    print(f"3. 添加调试信息，显示实际调用的API URL")


if __name__ == "__main__":
    debug_function_calls()
