# 统一参数配置使用指南

## 🎯 **现在所有模块都使用统一的参数配置！**

### **可用的参数：**

#### **调度器参数**
- `--time 09:00` - 每天执行时间（默认: 09:00）
- `--run-now` - 立即执行一次任务（测试用）
- `--daemon` - 以守护进程模式运行

#### **Google Sheets参数**
- `--credentials credentials.json` - Google凭证文件路径
- `--sheet-name TSTASK` - Google Sheet文件名
- `--worksheet-name worksheet` - 工作表名称

#### **表单检查参数**
- `--max-urls 10` - 最大检查URL数量（用于测试）
- `--min-results 10` - 最少需要的有效结果数量（默认: 10）
- `--batch-size 50` - 每次获取的URL批次大小（默认: 50）
- `--max-batches 10` - 最大批次数量，防止无限循环（默认: 10）
- `--timeout 15000` - 页面加载超时时间（毫秒）
- `--headless` - 使用无头浏览器模式

#### **日志参数**
- `--log-level INFO` - 日志级别（DEBUG/INFO/WARNING/ERROR）
- `--log-file app.log` - 日志文件路径

## 🚀 **使用示例：**

### **1. 运行定时调度器**
```bash
# 基本用法 - 每天09:00执行
python scheduler.py

# 自定义时间 - 每天14:30执行
python scheduler.py --time 14:30

# 立即测试执行
python scheduler.py --run-now

# 使用自定义配置
python scheduler.py --time 10:00 --sheet-name "MySheet" --max-urls 5

# 设置最少需要20个有效结果
python scheduler.py --min-results 20 --batch-size 100

# 调整日志级别
python scheduler.py --log-level DEBUG --log-file debug.log
```

### **2. 直接运行Google Sheets**
```bash
# 使用默认配置
python google_sheets.py

# 使用自定义配置
python google_sheets.py --credentials my-creds.json --sheet-name "TestSheet"
```

### **3. 直接运行URL检查**
```bash
# 使用默认配置
python get_url.py

# 限制检查数量（测试用）
python get_url.py --max-urls 3 --log-level DEBUG

# 设置最少需要15个有效结果，每批次处理30个URL
python get_url.py --min-results 15 --batch-size 30 --max-batches 5
```

### **4. 查看所有可用参数**
```bash
python scheduler.py --help
python google_sheets.py --help
python get_url.py --help
python config.py --help
```

## 🎉 **优势：**

1. **统一参数** - 所有模块使用相同的参数名称
2. **无冲突** - 解决了argparse参数冲突问题
3. **灵活配置** - 可以在任何模块中使用任何参数
4. **易于维护** - 参数定义集中在config.py中
5. **向后兼容** - 保持原有的使用方式

## 📁 **文件说明：**

- `config.py` - 统一的参数配置管理
- `scheduler.py` - 定时任务调度器
- `google_sheets.py` - Google Sheets操作
- `get_url.py` - URL获取和处理
- `form_checker.py` - 表单检查逻辑
