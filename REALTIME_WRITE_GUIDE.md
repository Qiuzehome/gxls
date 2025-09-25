# Google Sheets实时写入功能说明

## 🚀 功能概述

现在支持**实时写入Google Sheets**功能！每批次URL检查完成后，会立即将结果写入Google Sheets，而不是等到所有URL检查完毕才写入。

## ✅ 优势

### 1. **数据安全**
- 避免程序中断导致数据丢失
- 每批次结果都会立即保存
- 失败时自动保存本地备份

### 2. **实时监控**
- 可以实时查看Google Sheets中的进度
- 无需等待整个任务完成就能看到结果
- 便于及时发现和处理问题

### 3. **内存优化**
- 不需要在内存中积累大量结果
- 减少内存占用
- 提高程序稳定性

## 🔧 使用方法

### 默认使用（推荐）
```python
from config import Config
from get_url import get_url

# 默认启用实时写入
config = Config()
url = "your_api_url"
get_url(url, config)
```

### 命令行参数控制
```bash
# 启用实时写入（默认）
python scheduler.py --realtime-write

# 禁用实时写入，使用批量写入
python scheduler.py --no-realtime-write

# 设置写入失败重试次数
python scheduler.py --write-retry 5
```

### 程序化配置
```python
from config import Config

# 创建配置
config = Config()

# 启用实时写入，设置重试次数
config.realtime_write = True
config.write_retry = 3

# 禁用实时写入，使用传统批量写入
config.realtime_write = False
```

## 📊 工作流程对比

### 实时写入模式（新）
```
批次1: 检查URLs → 立即写入Google Sheets → 继续下一批次
批次2: 检查URLs → 立即写入Google Sheets → 继续下一批次
批次3: 检查URLs → 立即写入Google Sheets → 完成
```

### 批量写入模式（旧）
```
批次1: 检查URLs → 缓存结果
批次2: 检查URLs → 缓存结果  
批次3: 检查URLs → 缓存结果 → 最后统一写入Google Sheets
```

## 🛡️ 容错机制

### 1. **自动重试**
- 写入失败时自动重试（默认3次）
- 使用指数退避策略（2秒、4秒、8秒）
- 可配置重试次数

### 2. **本地备份**
- 写入失败时自动保存到本地文件
- 备份文件包含时间戳和批次信息
- 便于后续手动恢复

### 3. **详细日志**
- 显示每批次的写入状态
- 记录成功/失败的详细信息
- 便于问题排查

## 📝 日志输出示例

```
🔧 并行配置: 3 上下文 × 4 页面 = 12 并行度
📦 批次 1: 使用 4 个页面并行检查 20 个URL
✅ 页面1: https://example1.com 包含表单
❌ 页面2: https://example2.com 无表单
📝 立即写入第 1 批次的 5 个结果到Google Sheets...
✅ 第 1 批次结果已成功写入Google Sheets

第 1 批次完成:
  - 检查URL数: 20
  - 有效结果: 5
  - 累计有效结果: 5
  - 目标进度: 5/180
  - ✅ 本批次结果已实时写入Google Sheets
```

## ⚙️ 配置选项

### realtime_write
- **类型**: Boolean
- **默认**: True
- **说明**: 是否启用实时写入模式

### write_retry
- **类型**: Integer  
- **默认**: 3
- **说明**: Google Sheets写入失败重试次数

## 🔍 故障排除

### 1. **写入失败**
```
❌ 第 1 批次写入Google Sheets失败，已重试 3 次: [错误信息]
💾 已保存到本地备份文件: backup_batch_1_p0_20241225_143022.txt
```
**解决方案**:
- 检查网络连接
- 验证Google Sheets权限
- 查看本地备份文件手动恢复

### 2. **权限问题**
```
❌ 第 2 批次写入失败，第 1 次重试: 403 Forbidden
```
**解决方案**:
- 确认服务账号有Sheet写入权限
- 检查credentials.json文件是否正确
- 验证Sheet是否已分享给服务账号

### 3. **网络超时**
```
⚠️  第 3 批次写入失败，第 2 次重试: Request timeout
```
**解决方案**:
- 检查网络稳定性
- 增加重试次数
- 考虑使用VPN或代理

## 💡 最佳实践

### 1. **推荐配置**
```python
config.realtime_write = True    # 启用实时写入
config.write_retry = 3          # 适中的重试次数
config.batch_size = 30          # 较小的批次大小，更频繁的写入
```

### 2. **大批量任务**
- 使用较小的batch_size（20-30）
- 启用实时写入避免数据丢失
- 监控Google Sheets API配额

### 3. **网络不稳定环境**
- 增加重试次数到5-10次
- 考虑禁用实时写入，使用批量写入
- 定期检查本地备份文件

## 🚨 注意事项

1. **API配额限制**: Google Sheets API有请求频率限制，大量实时写入可能触发限制
2. **网络依赖**: 实时写入需要稳定的网络连接
3. **权限要求**: 确保服务账号有目标Sheet的编辑权限
4. **备份重要性**: 即使启用实时写入，也要定期备份重要数据

## 📈 性能影响

### 优势
- ✅ 数据安全性大幅提升
- ✅ 实时监控和反馈
- ✅ 内存占用减少

### 考虑
- ⚠️ 网络请求次数增加
- ⚠️ 可能触发API限制
- ⚠️ 单次写入失败影响整体进度

总的来说，**建议在大多数情况下启用实时写入功能**，特别是在处理重要数据或长时间运行的任务时。
