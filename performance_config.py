# -*- coding: utf-8 -*-
"""
表单检查性能配置文件
用于调整各种性能参数以获得最佳效果
"""

# ===== 默认性能配置参数 =====

# 并发配置默认值
DEFAULT_MAX_CONCURRENT_CONTEXTS = 5
DEFAULT_MIN_PAGES_PER_CONTEXT = 2
DEFAULT_MAX_PAGES_PER_CONTEXT = 8
DEFAULT_PAGES_PER_CONTEXT = 4
DEFAULT_MIN_CONCURRENT = 2
DEFAULT_MAX_CONCURRENT = 6
DEFAULT_CONCURRENT_RATIO = 15
DEFAULT_MAX_TOTAL_PAGES = 24

# 批次大小默认值
DEFAULT_BATCH_SIZE_SMALL = 20
DEFAULT_BATCH_SIZE_MEDIUM = 30
DEFAULT_BATCH_SIZE_LARGE = 50

# 超时配置默认值（毫秒）
DEFAULT_PAGE_NAVIGATION_TIMEOUT = 8000
DEFAULT_PAGE_LOAD_WAIT_TIMEOUT = 5000
DEFAULT_FORM_DETECTION_TIMEOUT = 3000
DEFAULT_SECONDARY_PAGE_TIMEOUT = 6000
DEFAULT_BROWSER_CONTEXT_TIMEOUT = 30000

# 缓存配置默认值
DEFAULT_CACHE_ENABLED = True
DEFAULT_CACHE_EXPIRE_HOURS = 24
DEFAULT_MAX_CACHE_SIZE = 1000
DEFAULT_CACHE_CLEANUP_THRESHOLD = 500

# 浏览器配置默认值
DEFAULT_BROWSER_HEADLESS = True
DEFAULT_DISABLE_IMAGES = True
DEFAULT_DISABLE_CSS = True
DEFAULT_DISABLE_FONTS = True
DEFAULT_DISABLE_MEDIA = True
DEFAULT_DISABLE_JAVASCRIPT = False
DEFAULT_VIEWPORT_WIDTH = 1280
DEFAULT_VIEWPORT_HEIGHT = 720

# 日志配置默认值
DEFAULT_SHOW_PROGRESS = True
DEFAULT_SHOW_CACHE_HITS = True
DEFAULT_SHOW_DETAILED_ERRORS = True
DEFAULT_SHOW_TIMING_INFO = True

# 并发配置
PARALLEL_CONFIG = {
    # 最大并发浏览器上下文数
    "max_concurrent_contexts": DEFAULT_MAX_CONCURRENT_CONTEXTS,
    # 每个上下文的页面数配置
    "min_pages_per_context": DEFAULT_MIN_PAGES_PER_CONTEXT,
    "max_pages_per_context": DEFAULT_MAX_PAGES_PER_CONTEXT,
    "default_pages_per_context": DEFAULT_PAGES_PER_CONTEXT,
    # 动态调整并发数的公式参数
    "min_concurrent": DEFAULT_MIN_CONCURRENT,
    "max_concurrent": DEFAULT_MAX_CONCURRENT,
    "concurrent_ratio": DEFAULT_CONCURRENT_RATIO,
    # 批次大小配置
    "batch_size_small": DEFAULT_BATCH_SIZE_SMALL,
    "batch_size_medium": DEFAULT_BATCH_SIZE_MEDIUM,
    "batch_size_large": DEFAULT_BATCH_SIZE_LARGE,
    # 总并行度限制（上下文数 × 页面数）
    "max_total_pages": DEFAULT_MAX_TOTAL_PAGES,
}

# 超时配置（毫秒）
TIMEOUT_CONFIG = {
    "page_navigation": DEFAULT_PAGE_NAVIGATION_TIMEOUT,  # 页面导航超时
    "page_load_wait": DEFAULT_PAGE_LOAD_WAIT_TIMEOUT,  # 页面加载等待
    "form_detection": DEFAULT_FORM_DETECTION_TIMEOUT,  # 表单检测超时
    "secondary_page": DEFAULT_SECONDARY_PAGE_TIMEOUT,  # 二级页面检查超时
    "browser_context": DEFAULT_BROWSER_CONTEXT_TIMEOUT,  # 浏览器上下文超时
}

# 缓存配置
CACHE_CONFIG = {
    "enabled": DEFAULT_CACHE_ENABLED,  # 是否启用缓存
    "expire_hours": DEFAULT_CACHE_EXPIRE_HOURS,  # 缓存过期时间（小时）
    "max_cache_size": DEFAULT_MAX_CACHE_SIZE,  # 最大缓存条目数
    "cleanup_threshold": DEFAULT_CACHE_CLEANUP_THRESHOLD,  # 缓存清理阈值
}

# 页面检查策略
CHECK_STRATEGY = {
    "check_main_page_only": False,  # 是否只检查主页面
    "max_secondary_links": 2,  # 最多检查的二级链接数
    "prioritize_contact_pages": True,  # 是否优先检查contact页面
    "contact_keywords": [
        "contact",
        "form",
        "inquiry",
        "get-quote",
        "request",
    ],  # contact页面关键词
}

# 浏览器优化配置
BROWSER_CONFIG = {
    "headless": DEFAULT_BROWSER_HEADLESS,
    "disable_images": DEFAULT_DISABLE_IMAGES,  # 禁用图片加载
    "disable_css": DEFAULT_DISABLE_CSS,  # 禁用CSS加载
    "disable_fonts": DEFAULT_DISABLE_FONTS,  # 禁用字体加载
    "disable_media": DEFAULT_DISABLE_MEDIA,  # 禁用媒体文件
    "disable_javascript": DEFAULT_DISABLE_JAVASCRIPT,  # 是否禁用JavaScript（表单检测需要JS）
    "viewport_width": DEFAULT_VIEWPORT_WIDTH,
    "viewport_height": DEFAULT_VIEWPORT_HEIGHT,
    # Chrome启动参数
    "chrome_args": [
        "--disable-blink-features=AutomationControlled",
        "--disable-dev-shm-usage",
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-gpu",
        "--disable-background-timer-throttling",
        "--disable-backgrounding-occluded-windows",
        "--disable-renderer-backgrounding",
        "--disable-features=TranslateUI",
        "--disable-ipc-flooding-protection",
        "--memory-pressure-off",
        "--max_old_space_size=4096",
    ],
}

# 日志配置
LOGGING_CONFIG = {
    "show_progress": DEFAULT_SHOW_PROGRESS,  # 显示进度信息
    "show_cache_hits": DEFAULT_SHOW_CACHE_HITS,  # 显示缓存命中信息
    "show_detailed_errors": DEFAULT_SHOW_DETAILED_ERRORS,  # 显示详细错误信息
    "show_timing_info": DEFAULT_SHOW_TIMING_INFO,  # 显示时间信息
}


def get_optimal_config_for_urls(url_count):
    """根据URL数量返回最优配置（包括多页面支持）"""
    if url_count < 10:
        return {
            "max_concurrent": 2,
            "pages_per_context": 2,
            "batch_size": url_count,
            "timeout_multiplier": 1.5,  # 少量URL时可以等待更长时间
            "total_pages": 4,
        }
    elif url_count < 50:
        return {
            "max_concurrent": 3,
            "pages_per_context": 4,
            "batch_size": PARALLEL_CONFIG["batch_size_small"],
            "timeout_multiplier": 1.2,
            "total_pages": 12,
        }
    elif url_count < 200:
        return {
            "max_concurrent": 4,
            "pages_per_context": 5,
            "batch_size": PARALLEL_CONFIG["batch_size_medium"],
            "timeout_multiplier": 1.0,
            "total_pages": 20,
        }
    else:
        return {
            "max_concurrent": PARALLEL_CONFIG["max_concurrent"],
            "pages_per_context": PARALLEL_CONFIG["max_pages_per_context"],
            "batch_size": PARALLEL_CONFIG["batch_size_large"],
            "timeout_multiplier": 0.8,  # 大量URL时缩短超时时间
            "total_pages": PARALLEL_CONFIG["max_total_pages"],
        }


def calculate_optimal_pages_per_context(url_count, max_concurrent):
    """计算最优的每上下文页面数"""
    # 计算理想总页面数
    ideal_total_pages = min(url_count, PARALLEL_CONFIG["max_total_pages"])

    # 计算每个上下文应该有多少页面
    pages_per_context = max(
        PARALLEL_CONFIG["min_pages_per_context"],
        min(
            PARALLEL_CONFIG["max_pages_per_context"],
            ideal_total_pages // max_concurrent,
        ),
    )

    return pages_per_context


def calculate_concurrent_count(url_count):
    """动态计算并发数"""
    calculated = max(
        PARALLEL_CONFIG["min_concurrent"],
        min(
            PARALLEL_CONFIG["max_concurrent"],
            url_count // PARALLEL_CONFIG["concurrent_ratio"],
        ),
    )
    return calculated


if __name__ == "__main__":
    # 测试不同URL数量的配置
    test_counts = [5, 25, 100, 500]
    for count in test_counts:
        config = get_optimal_config_for_urls(count)
        concurrent = calculate_concurrent_count(count)
        pages_per_context = calculate_optimal_pages_per_context(count, concurrent)
        total_pages = concurrent * pages_per_context

        print(f"URL数量: {count}")
        print(f"  推荐配置: {config}")
        print(f"  并发上下文数: {concurrent}")
        print(f"  每上下文页面数: {pages_per_context}")
        print(f"  总并行页面数: {total_pages}")
        print(f"  预期加速比: {min(total_pages, count)}x")
        print()
