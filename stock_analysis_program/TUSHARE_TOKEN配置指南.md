# Tushare Pro API Token 配置指南

## 📋 **概述**

股票分析系统现在支持**真实金融数据**接入，通过Tushare Pro API获取实时行情、财务数据、资金流向等信息。

## 🎯 **获取Tushare Pro Token**

### **步骤1：注册Tushare Pro账号**
1. 访问 https://tushare.pro/
2. 点击右上角"注册"
3. 填写邮箱、密码等信息完成注册

### **步骤2：获取API Token**
1. 登录后进入"个人中心"
2. 在"接口权限"页面找到"Token"
3. 复制您的Token（格式类似：`xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`）

### **步骤3：Token权限**
- **基础权限**：免费用户可获得基础数据权限
- **高级权限**：如需更多数据接口，可购买积分升级

## 🔧 **配置Token方法**

### **方法1：环境变量配置（推荐）**

在终端中设置环境变量：

```bash
# macOS/Linux
export TUSHARE_TOKEN=您的Token

# Windows PowerShell
$env:TUSHARE_TOKEN="您的Token"

# Windows Command Prompt
set TUSHARE_TOKEN=您的Token
```

### **唯一推荐方式：环境变量配置**

系统现在只支持通过环境变量注入 Token，这样可以避免把敏感信息写进代码、文档或仓库历史。

如果您希望长期生效，可把环境变量写入 shell 配置文件（如 `~/.bashrc`、`~/.zshrc`）。

## 📊 **支持的API接口**

### **股票数据**
- `daily` - 历史日线行情
- `daily_basic` - 每日指标（市盈率、换手率等）
- `moneyflow` - 资金流向
- `top_list` - 龙虎榜数据
- `fina_indicator` - 财务指标

### **指数数据**
- `index_daily` - 指数日线行情
- `index_dailybasic` - 指数每日指标

### **宏观经济**
- `cn_gdp` - GDP数据
- `cn_cpi` - CPI数据
- `cn_ppi` - PPI数据

### **更多接口**
系统支持Tushare Pro的**209个接口**，涵盖股票、指数、期货、债券、基金、宏观经济等15大类。

## 🚀 **启动真实数据系统**

### **启动脚本**
```bash
cd stock_analysis_program
./start_real_data_system.sh
```

### **手动启动**
```bash
# 启动后端服务
python3 real_data_backend.py

# 启动Web界面
python3 -m http.server 8888 --bind 0.0.0.0
```

### **访问地址**
- Web界面：http://localhost:8888/real_data_frontend.html
- API服务：http://localhost:9000/api/health

## 📈 **数据模式切换**

### **真实数据模式**
当配置了有效的Tushare Token时，系统自动使用真实数据。

### **模拟数据模式**
当Token未配置或API调用失败时，系统自动切换到模拟数据模式。

### **数据状态检查**
访问 http://localhost:9000/api/data_status 查看当前数据模式。

## 🔍 **API调用示例**

### **获取股票日线行情**
```python
# 在real_data_provider.py中
daily_data = provider.get_daily_quotes("601868.SH", "20240301", "20240331")
```

### **获取财务指标**
```python
financials = provider.get_financial_indicators("601868.SH")
```

### **获取资金流向**
```python
moneyflow = provider.get_moneyflow_data("601868.SH")
```

## ⚠️ **注意事项**

### **API调用限制**
- Tushare Pro有调用频率限制（每分钟1500次）
- 系统内置缓存机制减少重复调用
- 批量操作时适当增加延迟

### **数据更新频率**
- 行情数据：实时更新
- 财务数据：季度/年度更新
- 资金流向：每日更新

### **错误处理**
- API调用失败时自动切换到模拟数据
- 网络异常时提供友好的错误提示
- 缓存过期时自动重新获取

## 🛠️ **调试与测试**

### **测试API连接**
```bash
cd stock_analysis_program
python3 real_data_provider.py
```

### **查看日志**
后端服务会输出API调用状态和错误信息。

### **验证Token**
```python
# 在real_data_provider.py中测试
provider = RealDataProvider("您的Token")
test_result = provider.get_stock_basic_info("601868.SH")
print(f"API连接测试: {test_result}")
```

## 📝 **常见问题**

### **Q1：Token无效怎么办？**
- 检查Token是否正确复制
- 确认账号是否激活
- 查看Tushare Pro个人中心的接口权限

### **Q2：API调用返回错误怎么办？**
- 检查网络连接
- 确认接口参数格式
- 查看Tushare Pro文档中的接口说明

### **Q3：数据更新不及时怎么办？**
- Tushare Pro数据有更新延迟
- 部分数据需要T+1更新
- 实时数据需要高级权限

### **Q4：如何添加更多股票？**
修改 `real_data_backend.py` 中的 `positions` 列表：

```python
self.positions = [
    {"code": "601868.SH", "name": "中国能建", "amount": 400, "cost_price": 3.15},
    {"code": "002506.SZ", "name": "协鑫集成", "amount": 400, "cost_price": 2.05},
    {"code": "600821.SH", "name": "金开新能", "amount": 600, "cost_price": 4.10},
    # 添加更多股票...
]
```

## 🎉 **成功标志**

当系统显示"数据模式：真实数据"时，表示已成功接入Tushare Pro API。

**享受真实金融数据带来的精准分析吧！** 🚀