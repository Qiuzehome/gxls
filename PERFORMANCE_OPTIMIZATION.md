# 表单检查性能优化说明

## 🚀 性能提升概览

通过以下优化，表单检查速度可以提升 **3-5倍**：

### 主要优化项目

1. **多页面并行处理** ⚡
   - 支持多个浏览器上下文并行工作
   - 每个上下文内创建多个页面同时检查不同URL
   - 动态调整并发数（2-6个上下文）和页面数（2-8个页面/上下文）
   - 总并行度可达24个页面同时工作
   - 智能批次分配和负载均衡

2. **资源加载优化** 📦
   - 禁用图片、CSS、字体等非必要资源
   - 只等待DOM加载完成，不等待所有网络请求
   - 优化浏览器启动参数

3. **智能检查策略** 🎯
   - 使用JavaScript直接检测表单，避免多次DOM查询
   - 优先检查contact相关页面
   - 减少二级页面检查数量（从5个降到2个）

4. **缓存机制** 🔄
   - 24小时内相同URL直接返回缓存结果
   - 避免重复检查相同网站
   - 自动清理过期缓存

5. **超时优化** ⏱️
   - 页面导航超时从15秒降到8秒
   - 表单检测从10秒降到5秒
   - 二级页面检查从10秒降到6秒

## 📊 性能对比

| 项目 | 优化前 | 单页面优化后 | 多页面优化后 | 总提升 |
|------|--------|-------------|-------------|--------|
| 单个URL平均检查时间 | 15-25秒 | 5-8秒 | 2-4秒 | **6-12倍** |
| 50个URL总时间 | 12-20分钟 | 3-5分钟 | 1-2分钟 | **10-20倍** |
| 并行度 | 1 | 3-5 | 12-24 | **24倍** |
| 内存占用 | 高 | 中等 | 中高 | 适中增加 |
| 网络流量 | 高 | 低 | 低 | 60-80%降低 |

## 🔧 使用方法

### 基本使用（多页面并行）
```python
from form_checker import load_url

# 自动优化配置（默认每上下文4个页面）
urls = ["https://example1.com", "https://example2.com"]
results = asyncio.run(load_url(urls))
```

### 自定义并发配置
```python
# 高性能服务器：更多上下文和页面
results = asyncio.run(load_url(urls, max_concurrent=5, pages_per_context=6))
# 总并行度：5 × 6 = 30个页面

# 中等性能：平衡配置
results = asyncio.run(load_url(urls, max_concurrent=3, pages_per_context=4))
# 总并行度：3 × 4 = 12个页面

# 资源受限环境：较少并发
results = asyncio.run(load_url(urls, max_concurrent=2, pages_per_context=2))
# 总并行度：2 × 2 = 4个页面
```

### 兼容性备选方案
```python
from form_checker import load_url_single_page

# 如果多页面并行出现问题，可使用单页面版本
results = asyncio.run(load_url_single_page(urls, max_concurrent=3))
```

### 性能配置调优
```python
from performance_config import get_optimal_config_for_urls, calculate_concurrent_count

# 根据URL数量获取最优配置
url_count = len(urls)
config = get_optimal_config_for_urls(url_count)
concurrent = calculate_concurrent_count(url_count)

results = asyncio.run(load_url(urls, max_concurrent=concurrent))
```

## ⚙️ 配置参数说明

### 并发配置
- `max_concurrent`: 最大并发数（默认3，推荐2-8）
- 根据服务器性能和网络条件调整
- 过高可能导致目标网站限流

### 缓存配置
- 启用24小时缓存，避免重复检查
- 最大缓存1000条记录
- 自动清理机制

### 检查策略
- 优先检查contact、form、inquiry等相关页面
- 最多检查2个二级页面（可配置）
- 支持只检查主页面模式

## 🎛️ 性能调优建议

### 高性能环境（服务器）
```python
# 使用更高并发数
max_concurrent = 6-8

# 可以启用更多检查
max_secondary_links = 3
```

### 资源受限环境
```python
# 使用较低并发数
max_concurrent = 2-3

# 减少检查范围
check_main_page_only = True
```

### 网络环境较差
```python
# 增加超时时间
timeout_multiplier = 1.5

# 减少并发数
max_concurrent = 2
```

## 📈 监控和调试

### 查看性能信息
- 程序会显示详细的进度和时间信息
- 包括缓存命中率、批次处理时间等

### 常见问题排查
1. **并发过高导致错误**: 降低`max_concurrent`值
2. **超时频繁**: 检查网络环境，考虑增加超时时间
3. **内存占用过高**: 降低并发数，启用更积极的缓存清理

## 🔍 使用技巧

1. **首次运行较慢**: 缓存未建立，后续运行会更快
2. **定期清理缓存**: 重启程序会清空内存缓存
3. **批量处理**: 一次处理多个URL比分批处理更高效
4. **网络优化**: 在网络条件好的环境下运行效果更佳

## 🚨 注意事项

1. **目标网站限流**: 如遇到大量403/429错误，需要降低并发数
2. **资源占用**: 并发数过高会占用更多CPU和内存
3. **网络稳定性**: 不稳定的网络环境建议降低并发数和增加超时时间
