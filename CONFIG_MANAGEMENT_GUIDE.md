# 配置管理指南

## 🎯 概述

现在所有默认配置参数都已经提取到文件顶部，方便统一管理和修改。这样的设计有以下优势：

1. **集中管理**：所有配置都在文件开头定义
2. **易于维护**：修改配置只需要改一个地方
3. **一致性**：确保所有地方使用相同的默认值
4. **可读性**：配置参数有清晰的命名和注释

## 📁 配置文件结构

### 1. `config.py` - 主配置文件
```python
# ===== 默认配置参数 =====

# 调度器默认配置
DEFAULT_SCHEDULE_TIME = "09:00"

# Google Sheets默认配置
DEFAULT_CREDENTIALS_PATH = "credentials.json"
DEFAULT_SHEET_NAME = "TSTASK"
DEFAULT_WORKSHEET_NAME = "p0"

# 表单检查默认配置
DEFAULT_MIN_RESULTS = 10
DEFAULT_BATCH_SIZE = 50
DEFAULT_REALTIME_WRITE = True
DEFAULT_WRITE_RETRY = 3
# ... 更多配置
```

### 2. `performance_config.py` - 性能配置文件
```python
# ===== 默认性能配置参数 =====

# 并发配置默认值
DEFAULT_MAX_CONCURRENT = 6
DEFAULT_PAGES_PER_CONTEXT = 4
DEFAULT_MAX_TOTAL_PAGES = 24

# 超时配置默认值（毫秒）
DEFAULT_PAGE_NAVIGATION_TIMEOUT = 8000
DEFAULT_SECONDARY_PAGE_TIMEOUT = 6000
# ... 更多配置
```

### 3. `form_checker.py` - 表单检查配置
```python
# ===== 默认配置参数 =====

# 缓存配置
DEFAULT_CACHE_EXPIRE_HOURS = 24
DEFAULT_MAX_CACHE_SIZE = 1000

# 页面检查配置
DEFAULT_PAGE_LOAD_TIMEOUT = 5000
DEFAULT_MAX_SECONDARY_LINKS = 2
# ... 更多配置
```

## 🔧 如何修改配置

### 方法1：修改默认值（推荐）
直接在文件顶部修改相应的默认配置：

```python
# 在 config.py 顶部修改
DEFAULT_BATCH_SIZE = 30  # 从50改为30
DEFAULT_WRITE_RETRY = 5  # 从3改为5

# 在 performance_config.py 顶部修改
DEFAULT_MAX_CONCURRENT = 8  # 从6改为8
DEFAULT_PAGES_PER_CONTEXT = 6  # 从4改为6
```

### 方法2：命令行参数
```bash
# 使用命令行参数覆盖默认配置
python scheduler.py --batch-size 30 --write-retry 5 --min-results 20
```

### 方法3：程序化配置
```python
from config import Config

config = Config()
config.batch_size = 30
config.write_retry = 5
config.min_results = 20
```

## 📋 主要配置参数说明

### 调度器配置
| 参数 | 默认值 | 说明 |
|------|--------|------|
| `DEFAULT_SCHEDULE_TIME` | "09:00" | 每天执行时间 |

### Google Sheets配置
| 参数 | 默认值 | 说明 |
|------|--------|------|
| `DEFAULT_CREDENTIALS_PATH` | "credentials.json" | 凭证文件路径 |
| `DEFAULT_SHEET_NAME` | "TSTASK" | Google Sheet文件名 |
| `DEFAULT_WORKSHEET_NAME` | "p0" | 工作表名称 |

### 表单检查配置
| 参数 | 默认值 | 说明 |
|------|--------|------|
| `DEFAULT_MIN_RESULTS` | 10 | 最少需要的结果数 |
| `DEFAULT_BATCH_SIZE` | 50 | URL批次大小 |
| `DEFAULT_MAX_BATCHES` | 10 | 最大批次数 |
| `DEFAULT_TIMEOUT` | 15000 | 页面超时时间（毫秒） |
| `DEFAULT_REALTIME_WRITE` | True | 是否实时写入 |
| `DEFAULT_WRITE_RETRY` | 3 | 写入重试次数 |

### 性能配置
| 参数 | 默认值 | 说明 |
|------|--------|------|
| `DEFAULT_MAX_CONCURRENT` | 6 | 最大并发上下文数 |
| `DEFAULT_PAGES_PER_CONTEXT` | 4 | 每上下文页面数 |
| `DEFAULT_MAX_TOTAL_PAGES` | 24 | 最大总页面数 |
| `DEFAULT_PAGE_NAVIGATION_TIMEOUT` | 8000 | 页面导航超时 |
| `DEFAULT_SECONDARY_PAGE_TIMEOUT` | 6000 | 二级页面超时 |

### 缓存配置
| 参数 | 默认值 | 说明 |
|------|--------|------|
| `DEFAULT_CACHE_EXPIRE_HOURS` | 24 | 缓存过期时间（小时） |
| `DEFAULT_MAX_CACHE_SIZE` | 1000 | 最大缓存条目数 |
| `DEFAULT_MAX_SECONDARY_LINKS` | 2 | 最多检查的二级链接数 |

## 🎛️ 配置优化建议

### 高性能环境
```python
# 在相应文件顶部修改
DEFAULT_MAX_CONCURRENT = 8
DEFAULT_PAGES_PER_CONTEXT = 6
DEFAULT_BATCH_SIZE = 30
DEFAULT_WRITE_RETRY = 2
```

### 网络受限环境
```python
DEFAULT_MAX_CONCURRENT = 2
DEFAULT_PAGES_PER_CONTEXT = 2
DEFAULT_TIMEOUT = 20000
DEFAULT_WRITE_RETRY = 5
```

### 大批量处理
```python
DEFAULT_BATCH_SIZE = 100
DEFAULT_MIN_RESULTS = 50
DEFAULT_MAX_BATCHES = 20
DEFAULT_REALTIME_WRITE = True  # 确保数据安全
```

## 🔄 配置更新流程

### 1. 备份当前配置
```bash
cp config.py config.py.backup
cp performance_config.py performance_config.py.backup
```

### 2. 修改配置参数
在文件顶部的默认配置区域修改相应参数

### 3. 测试新配置
```bash
python test_multi_page_performance.py
```

### 4. 部署到生产环境
确认测试无误后，部署新配置

## 📊 配置监控

### 查看当前配置
```python
from config import Config
from performance_config import *

config = Config()
print("当前配置:")
print(f"  批次大小: {config.batch_size}")
print(f"  最大并发: {DEFAULT_MAX_CONCURRENT}")
print(f"  页面数/上下文: {DEFAULT_PAGES_PER_CONTEXT}")
print(f"  实时写入: {config.realtime_write}")
```

### 性能测试
```python
# 运行性能测试脚本
python test_multi_page_performance.py

# 查看不同配置的性能表现
python performance_config.py
```

## 🚨 注意事项

### 1. 配置依赖关系
- `DEFAULT_MAX_TOTAL_PAGES` 应该 >= `DEFAULT_MAX_CONCURRENT` × `DEFAULT_PAGES_PER_CONTEXT`
- `DEFAULT_BATCH_SIZE` 建议是 `DEFAULT_MAX_CONCURRENT` 的倍数
- 超时时间应该合理设置，避免过短或过长

### 2. 资源限制
- 并发数过高可能导致内存不足
- 页面数过多可能触发目标网站限制
- 缓存大小要考虑内存使用

### 3. 兼容性
- 修改配置前要测试兼容性
- 某些配置可能影响其他模块
- 建议渐进式调整，不要一次改动太大

## 💡 最佳实践

1. **渐进调优**：逐步调整配置，观察效果
2. **环境区分**：开发、测试、生产使用不同配置
3. **监控指标**：关注成功率、响应时间、资源使用
4. **定期评估**：根据实际使用情况调整配置
5. **文档记录**：记录配置变更的原因和效果

现在所有配置都集中管理，修改起来更加方便和安全！
