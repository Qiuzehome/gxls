import json
import asyncio
import time
import hashlib
import os
from datetime import datetime, timedelta
from playwright.async_api import async_playwright
from concurrent.futures import ThreadPoolExecutor
import logging

# ===== 默认配置参数 =====

# 缓存配置
DEFAULT_CACHE_EXPIRE_HOURS = 24  # 缓存24小时
DEFAULT_MAX_CACHE_SIZE = 1000  # 最大缓存条目数
DEFAULT_CACHE_CLEANUP_SIZE = 500  # 缓存清理保留数量

# 页面检查配置
DEFAULT_PAGE_LOAD_TIMEOUT = 5000  # DOM加载等待时间（毫秒）
DEFAULT_NAVIGATION_TIMEOUT = 8000  # 页面导航超时（毫秒）
DEFAULT_SECONDARY_PAGE_TIMEOUT = 6000  # 二级页面检查超时（毫秒）
DEFAULT_MAX_SECONDARY_LINKS = 2  # 最多检查的二级链接数

# 并行处理配置
DEFAULT_MAX_CONCURRENT = 3  # 默认并发上下文数
DEFAULT_PAGES_PER_CONTEXT = 4  # 默认每上下文页面数

# 简单的内存缓存
_form_cache = {}
CACHE_EXPIRE_HOURS = DEFAULT_CACHE_EXPIRE_HOURS


async def check_forms_on_page(page, url, level=1):
    """检查页面是否包含有效表单（包含input元素的表单）"""
    try:
        # 优化：只等待domcontentloaded，不等待所有网络请求完成
        await page.wait_for_load_state(
            "domcontentloaded", timeout=DEFAULT_PAGE_LOAD_TIMEOUT
        )

        # 优化：使用更高效的CSS选择器直接查找包含input的表单
        valid_forms = await page.evaluate(
            """
            () => {
                const forms = document.querySelectorAll('form');
                let validCount = 0;
                for (const form of forms) {
                    if (form.querySelector('input')) {
                        validCount++;
                    }
                }
                return validCount;
            }
        """
        )

        if valid_forms > 0:
            print(
                f"{'  ' * (level-1)}✓ {level}级页面 {url} 包含 {valid_forms} 个有效表单（含input）"
            )
            return True, valid_forms

        # 如果主页面没有有效表单，检查同源iframe
        if valid_forms == 0:
            iframe_forms = await check_iframes_for_forms(page, url, level)
            if iframe_forms > 0:
                print(
                    f"{'  ' * (level-1)}✓ {level}级页面 {url} 在iframe中找到 {iframe_forms} 个有效表单"
                )
                return True, iframe_forms

        print(f"{'  ' * (level-1)}✗ {level}级页面 {url} 不包含有效表单")
        return False, 0

    except Exception as e:
        print(f"{'  ' * (level-1)}✗ {level}级页面 {url} 检查失败: {str(e)}")
        return False, 0


async def check_iframes_for_forms(page, url, level=1):
    """检查页面中的同源iframe是否包含有效表单"""
    try:
        # 获取页面的域名
        from urllib.parse import urlparse

        main_domain = urlparse(url).netloc

        # 查找所有iframe
        iframes = await page.query_selector_all("iframe")

        if not iframes:
            return 0

        print(f"{'  ' * level}🔍 找到 {len(iframes)} 个iframe，检查同源iframe...")

        total_iframe_forms = 0

        for i, iframe in enumerate(iframes):
            try:
                # 获取iframe的src和srcdoc属性
                iframe_src = await iframe.get_attribute("src")
                iframe_srcdoc = await iframe.get_attribute("srcdoc")

                is_same_origin = False
                iframe_description = ""

                if not iframe_src and not iframe_srcdoc:
                    # 没有src和srcdoc的iframe通常是同源的（动态创建或空iframe）
                    is_same_origin = True
                    iframe_description = "动态/空iframe"
                elif iframe_srcdoc:
                    # 使用srcdoc的iframe是同源的
                    is_same_origin = True
                    iframe_description = "srcdoc内联iframe"
                elif iframe_src:
                    # 检查src是否为同源
                    if iframe_src.startswith("//"):
                        iframe_src = f"https:{iframe_src}"
                    elif iframe_src.startswith("/"):
                        iframe_src = f"https://{main_domain}{iframe_src}"
                    elif not iframe_src.startswith(("http://", "https://")):
                        # 相对路径也是同源的
                        is_same_origin = True
                        iframe_description = f"相对路径iframe: {iframe_src}"
                    else:
                        iframe_domain = urlparse(iframe_src).netloc
                        if iframe_domain == main_domain:
                            is_same_origin = True
                            iframe_description = f"同源iframe: {iframe_src}"
                        else:
                            print(
                                f"{'  ' * (level+1)}⏭ iframe {i+1} 跨域，跳过: {iframe_domain}"
                            )
                            continue

                if not is_same_origin:
                    continue

                print(f"{'  ' * (level+1)}🔍 检查iframe {i+1}: {iframe_description}")

                # 获取iframe内容
                iframe_content = await iframe.content_frame()
                if iframe_content:
                    # 在iframe中查找表单
                    iframe_forms = await iframe_content.query_selector_all("form")
                    iframe_valid_forms = 0

                    for form in iframe_forms:
                        inputs = await form.query_selector_all("input")
                        if inputs:
                            iframe_valid_forms += 1

                    if iframe_valid_forms > 0:
                        print(
                            f"{'  ' * (level+1)}✓ iframe {i+1} 包含 {iframe_valid_forms} 个有效表单"
                        )
                        total_iframe_forms += iframe_valid_forms
                    else:
                        print(f"{'  ' * (level+1)}✗ iframe {i+1} 无有效表单")

            except Exception as e:
                print(f"{'  ' * (level+1)}✗ iframe {i+1} 检查失败: {str(e)}")
                continue

        return total_iframe_forms

    except Exception as e:
        print(f"{'  ' * level}✗ iframe检查失败: {str(e)}")
        return 0


async def get_links_from_page(page, max_links=10):
    """获取页面中的链接，限制数量以提高效率，优先返回包含contact的链接"""
    try:
        # 查找所有a标签的href属性
        links = await page.evaluate(
            """
            () => {
                const links = Array.from(document.querySelectorAll('a[href]'));
                return links
                    .map(link => link.href)
                    .filter(href => {
                        // 过滤掉无效链接
                        try {
                            const url = new URL(href);
                            return url.protocol === 'http:' || url.protocol === 'https:';
                        } catch {
                            return false;
                        }
                    });
            }
        """
        )

        # 将包含 /contact 的链接优先排序
        contact_links = [link for link in links if "/contact" in link.lower()]
        other_links = [link for link in links if "/contact" not in link.lower()]

        # 合并并限制数量
        prioritized_links = contact_links + other_links
        return prioritized_links[:max_links]

    except Exception as e:
        print(f"获取链接失败: {str(e)}")
        return []


def normalize_url(url):
    """标准化URL，添加协议前缀"""
    if not url.startswith(("http://", "https://")):
        return f"https://{url}"
    return url


def get_cache_key(url):
    """生成缓存键"""
    return hashlib.md5(url.encode()).hexdigest()


def is_cache_valid(timestamp):
    """检查缓存是否仍然有效"""
    if not timestamp:
        return False
    cache_time = datetime.fromisoformat(timestamp)
    return datetime.now() - cache_time < timedelta(hours=CACHE_EXPIRE_HOURS)


def get_cached_result(url):
    """获取缓存的结果"""
    cache_key = get_cache_key(url)
    if cache_key in _form_cache:
        cached_data = _form_cache[cache_key]
        if is_cache_valid(cached_data.get("timestamp")):
            print(f"🔄 使用缓存结果: {url}")
            return cached_data.get("has_forms")
    return None


def set_cached_result(url, has_forms):
    """设置缓存结果"""
    cache_key = get_cache_key(url)
    _form_cache[cache_key] = {
        "has_forms": has_forms,
        "timestamp": datetime.now().isoformat(),
    }
    # 简单的缓存清理：如果缓存过多，清理旧的
    if len(_form_cache) > DEFAULT_MAX_CACHE_SIZE:
        # 清理一半的旧缓存
        old_keys = list(_form_cache.keys())[:DEFAULT_CACHE_CLEANUP_SIZE]
        for key in old_keys:
            del _form_cache[key]


async def check_url_with_forms(page, url):
    """检查URL及其二级页面是否包含表单（优化+缓存版本）"""
    normalized_url = normalize_url(url)

    # 检查缓存
    cached_result = get_cached_result(normalized_url)
    if cached_result is not None:
        return cached_result

    print(f"🔍 检查: {normalized_url}")

    result = False
    try:
        # 优化：使用更快的导航策略
        await page.goto(
            normalized_url,
            timeout=DEFAULT_NAVIGATION_TIMEOUT,
            wait_until="domcontentloaded",
        )

        # 优化：使用更快的表单检测
        has_form, form_count = await check_forms_on_page(page, normalized_url, 1)

        if has_form:
            result = True
        else:
            # 优化：只检查最相关的二级页面（contact相关链接）
            try:
                # 优化：同时获取链接和执行快速表单检测
                contact_links = await page.evaluate(
                    f"""
                    () => {{
                        const links = Array.from(document.querySelectorAll('a[href*="contact"], a[href*="form"], a[href*="inquiry"]'));
                        return links.slice(0, {DEFAULT_MAX_SECONDARY_LINKS}).map(link => link.href).filter(href => {{
                            try {{
                                const url = new URL(href);
                                return url.protocol === 'http:' || url.protocol === 'https:';
                            }} catch {{
                                return false;
                            }}
                        }});
                    }}
                """
                )

                if contact_links:
                    print(f"📋 检查 {len(contact_links)} 个相关链接...")

                    # 快速检查contact相关页面
                    for link in contact_links:
                        try:
                            await page.goto(
                                link,
                                timeout=DEFAULT_SECONDARY_PAGE_TIMEOUT,
                                wait_until="domcontentloaded",
                            )
                            has_form, _ = await check_forms_on_page(page, link, 2)

                            if has_form:
                                print(f"✅ 在相关页面找到表单！{link}")
                                result = True
                                break

                        except Exception as e:
                            print(f"❌ 相关页面检查失败: {str(e)}")
                            continue

            except Exception as e:
                print(f"❌ 链接检查失败: {str(e)}")

    except Exception as e:
        print(f"❌ 无法访问: {str(e)}")
        result = False

    # 缓存结果
    set_cached_result(normalized_url, result)
    return result


async def check_single_url_with_page(page, url, page_id):
    """使用单个页面检查单个URL"""
    try:
        has_forms = await check_url_with_forms(page, url)
        if has_forms:
            print(f"✅ 页面{page_id}: {url} 包含表单")
            return url
        else:
            print(f"❌ 页面{page_id}: {url} 无表单")
            return None
    except Exception as e:
        print(f"❌ 页面{page_id}: {url} 检查失败: {str(e)}")
        return None


async def check_url_batch_multi_page(
    browser, urls_batch, batch_id, pages_per_context=4
):
    """批量检查URL（多页面并行处理）"""
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        viewport={"width": 1280, "height": 720},
        bypass_csp=True,
    )

    # 禁用图片、CSS、字体等非必要资源
    await context.route(
        "**/*",
        lambda route: (
            route.abort()
            if route.request.resource_type in ["image", "stylesheet", "font", "media"]
            else route.continue_()
        ),
    )

    # 创建多个页面
    pages = []
    for i in range(pages_per_context):
        page = await context.new_page()
        page.set_default_timeout(8000)
        pages.append(page)

    print(
        f"📦 批次 {batch_id}: 使用 {len(pages)} 个页面并行检查 {len(urls_batch)} 个URL"
    )

    results = []

    # 将URL分配给不同页面并行处理
    tasks = []
    for i, url in enumerate(urls_batch):
        page_index = i % len(pages)
        page = pages[page_index]
        page_id = f"{batch_id}-P{page_index+1}"

        task = check_single_url_with_page(page, url, page_id)
        tasks.append(task)

    # 并行执行所有任务
    task_results = await asyncio.gather(*tasks, return_exceptions=True)

    # 收集有效结果
    for result in task_results:
        if isinstance(result, str):  # 成功返回URL
            results.append(result)
        elif isinstance(result, Exception):
            print(f"⚠️ 批次 {batch_id}: 任务执行异常: {result}")

    await context.close()
    print(f"📦 批次 {batch_id}: 完成，找到 {len(results)} 个有效结果")
    return results


# 保留原来的单页面版本作为备选
async def check_url_batch(browser, urls_batch, batch_id):
    """批量检查URL（单页面处理，备选方案）"""
    return await check_url_batch_multi_page(
        browser, urls_batch, batch_id, pages_per_context=1
    )


async def load_url(
    urls,
    max_concurrent=DEFAULT_MAX_CONCURRENT,
    pages_per_context=DEFAULT_PAGES_PER_CONTEXT,
):
    """主函数：多页面并行检查所有URL是否包含表单"""
    async with async_playwright() as p:
        # 优化浏览器启动参数
        browser = await p.chromium.launch(
            headless=True,
            args=[
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
                "--disable-web-security",  # 允许跨域，提高兼容性
            ],
        )

        total_urls = len(urls)
        total_pages = max_concurrent * pages_per_context
        print(f"🚀 开始多页面并行检查 {total_urls} 个URL")
        print(
            f"📊 配置: {max_concurrent} 个上下文 × {pages_per_context} 个页面 = {total_pages} 个并行页面"
        )

        # 将URL分批处理，考虑每个上下文内的页面数
        batch_size = max(1, total_urls // max_concurrent)
        url_batches = [
            urls[i : i + batch_size] for i in range(0, total_urls, batch_size)
        ]

        print(f"📦 分为 {len(url_batches)} 个批次，每批约 {batch_size} 个URL")

        # 并行执行所有批次，每个批次内部使用多页面并行
        tasks = []
        for batch_id, batch in enumerate(url_batches, 1):
            task = check_url_batch_multi_page(
                browser, batch, batch_id, pages_per_context
            )
            tasks.append(task)

        # 等待所有批次完成
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)

        # 合并结果
        all_results = []
        for batch_result in batch_results:
            if isinstance(batch_result, list):
                all_results.extend(batch_result)
            else:
                print(f"⚠️ 批次执行出错: {batch_result}")

        await browser.close()

        print(f"🎯 多页面并行检查完成！总计找到 {len(all_results)} 个有效结果")
        print(f"📈 实际并行度: {total_pages} 个页面同时工作")
        return all_results


async def load_url_single_page(urls, max_concurrent=DEFAULT_MAX_CONCURRENT):
    """单页面版本（兼容性备选方案）"""
    return await load_url(urls, max_concurrent, pages_per_context=1)


# 运行检查
if __name__ == "__main__":
    asyncio.run(load_url())
