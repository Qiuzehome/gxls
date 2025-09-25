# -*- coding: utf-8 -*-
"""
多页面并行性能测试脚本
用于对比单页面和多页面并行处理的性能差异
"""

import asyncio
import time
from form_checker import load_url, load_url_single_page
from performance_config import (
    get_optimal_config_for_urls,
    calculate_concurrent_count,
    calculate_optimal_pages_per_context,
)

# 测试URL列表（可以替换为实际需要测试的URL）
TEST_URLS = [
    "https://acehandymanfranchising.com",
    "https://example.com",
    "https://httpbin.org/forms/post",
    "https://www.w3schools.com/html/html_forms.asp",
    "https://developer.mozilla.org/en-US/docs/Web/HTML/Element/form",
    "https://github.com",
    "https://stackoverflow.com",
    "https://www.google.com",
    "https://www.microsoft.com",
    "https://www.apple.com",
    "https://www.amazon.com",
    "https://www.facebook.com",
    "https://www.twitter.com",
    "https://www.linkedin.com",
    "https://www.youtube.com",
]


async def test_single_page_performance(urls):
    """测试单页面处理性能"""
    print("🔄 开始单页面性能测试...")
    start_time = time.time()

    results = await load_url_single_page(urls, max_concurrent=3)

    end_time = time.time()
    duration = end_time - start_time

    print(f"⏱️ 单页面处理完成:")
    print(f"   耗时: {duration:.2f} 秒")
    print(f"   找到表单的URL数: {len(results)}")
    print(f"   平均每URL耗时: {duration/len(urls):.2f} 秒")

    return results, duration


async def test_multi_page_performance(urls, pages_per_context=4):
    """测试多页面处理性能"""
    print(f"🚀 开始多页面性能测试 (每上下文{pages_per_context}页面)...")
    start_time = time.time()

    results = await load_url(
        urls, max_concurrent=3, pages_per_context=pages_per_context
    )

    end_time = time.time()
    duration = end_time - start_time

    print(f"⏱️ 多页面处理完成:")
    print(f"   耗时: {duration:.2f} 秒")
    print(f"   找到表单的URL数: {len(results)}")
    print(f"   平均每URL耗时: {duration/len(urls):.2f} 秒")
    print(f"   并行页面数: {3 * pages_per_context}")

    return results, duration


async def run_performance_comparison():
    """运行性能对比测试"""
    print("🎯 开始多页面并行性能对比测试")
    print(f"📊 测试URL数量: {len(TEST_URLS)}")
    print("=" * 60)

    # 获取推荐配置
    config = get_optimal_config_for_urls(len(TEST_URLS))
    concurrent = calculate_concurrent_count(len(TEST_URLS))
    pages_per_context = calculate_optimal_pages_per_context(len(TEST_URLS), concurrent)

    print(f"📈 推荐配置:")
    print(f"   并发上下文数: {concurrent}")
    print(f"   每上下文页面数: {pages_per_context}")
    print(f"   总并行页面数: {concurrent * pages_per_context}")
    print("=" * 60)

    # 测试单页面处理
    single_results, single_duration = await test_single_page_performance(TEST_URLS)

    print("\n" + "=" * 60)

    # 测试多页面处理
    multi_results, multi_duration = await test_multi_page_performance(
        TEST_URLS, pages_per_context
    )

    print("\n" + "=" * 60)
    print("📊 性能对比结果:")
    print(f"   单页面处理: {single_duration:.2f} 秒")
    print(f"   多页面处理: {multi_duration:.2f} 秒")

    if multi_duration > 0:
        speedup = single_duration / multi_duration
        print(f"   🚀 性能提升: {speedup:.2f}x")
        print(
            f"   ⏰ 时间节省: {single_duration - multi_duration:.2f} 秒 ({(1-multi_duration/single_duration)*100:.1f}%)"
        )

    # 验证结果一致性
    single_set = set(single_results)
    multi_set = set(multi_results)

    if single_set == multi_set:
        print(f"   ✅ 结果一致性: 通过 ({len(single_results)} 个结果)")
    else:
        print(f"   ⚠️  结果一致性: 不一致")
        print(f"      单页面独有: {single_set - multi_set}")
        print(f"      多页面独有: {multi_set - single_set}")


async def test_different_page_counts():
    """测试不同页面数的性能"""
    print("🧪 测试不同页面数配置的性能...")

    page_counts = [1, 2, 4, 6, 8]
    results = {}

    for page_count in page_counts:
        print(f"\n📝 测试每上下文 {page_count} 页面...")
        start_time = time.time()

        urls_subset = TEST_URLS[:10]  # 使用较少URL进行快速测试
        result = await load_url(
            urls_subset, max_concurrent=2, pages_per_context=page_count
        )

        duration = time.time() - start_time
        results[page_count] = {
            "duration": duration,
            "results_count": len(result),
            "pages_total": 2 * page_count,
        }

        print(
            f"   耗时: {duration:.2f} 秒, 找到: {len(result)} 个, 总页面数: {2 * page_count}"
        )

    print("\n📊 不同页面数配置对比:")
    print("页面数 | 总页面 | 耗时(秒) | 找到数 | 效率")
    print("-" * 45)

    for page_count, data in results.items():
        efficiency = (
            data["results_count"] / data["duration"] if data["duration"] > 0 else 0
        )
        print(
            f"{page_count:^6} | {data['pages_total']:^6} | {data['duration']:^8.2f} | {data['results_count']:^6} | {efficiency:^6.2f}"
        )


if __name__ == "__main__":
    print("🎯 Playwright多页面并行性能测试")
    print("=" * 60)

    # 运行主要对比测试
    asyncio.run(run_performance_comparison())

    print("\n" + "=" * 60)

    # 运行不同页面数测试
    asyncio.run(test_different_page_counts())

    print("\n🎉 测试完成！")
    print("\n💡 优化建议:")
    print("1. 根据服务器性能调整pages_per_context参数")
    print("2. 监控内存使用情况，避免过多并行页面")
    print("3. 网络条件差时减少并行度")
    print("4. 目标网站有反爬限制时降低并发数")
