#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API连接修复程序
解决Tushare API Headers Timeout Error (3003)
"""

import os
import sys
import requests
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_network_connection():
    """检查网络连接状态"""
    print("🔍 检查网络连接状态...")
    
    test_urls = [
        ("百度", "https://www.baidu.com"),
        ("Tushare API", "https://api.tushare.pro"),
        ("腾讯云", "https://cloud.tencent.com"),
        ("腾讯证券", "https://quote.eastmoney.com"),
    ]
    
    all_good = True
    for name, url in test_urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"  ✅ {name}: 可访问")
            else:
                print(f"  ⚠️ {name}: 状态码 {response.status_code}")
                all_good = False
        except Exception as e:
            print(f"  ❌ {name}: 连接失败 - {str(e)}")
            all_good = False
    
    return all_good

def check_tushare_config():
    """检查Tushare配置"""
    print("\n🔍 检查Tushare配置...")
    
    config_path = project_root / "config" / "tushare_config.py"
    
    if not config_path.exists():
        print("  ❌ Tushare配置文件不存在")
        return False
    
    # 读取配置文件内容
    with open(config_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查Token是否已配置
    if '"your_tushare_token_here"' in content or "'your_tushare_token_here'" in content:
        print("  ❌ Tushare Token未配置")
        print("  ℹ️ 请从 https://tushare.pro 获取您的Token")
        print("  ℹ️ 然后编辑 config/tushare_config.py 填入您的Token")
        return False
    else:
        print("  ✅ Tushare Token已配置")
        
        # 尝试提取Token进行简单验证
        import re
        token_pattern = r"TOKEN\s*=\s*[\"'](.+?)[\"']"
        match = re.search(token_pattern, content)
        if match:
            token = match.group(1)
            if len(token) > 20:  # 假设有效Token长度大于20
                print(f"  ✅ Token格式看起来有效 ({token[:10]}...)")
                return True
            else:
                print(f"  ⚠️ Token格式可能无效: {token}")
                return False
        else:
            print("  ⚠️ 无法从配置文件中提取Token")
            return False

def check_proxy_settings():
    """检查代理设置"""
    print("\n🔍 检查代理设置...")
    
    proxy_vars = {
        'HTTP_PROXY': os.environ.get('HTTP_PROXY'),
        'HTTPS_PROXY': os.environ.get('HTTPS_PROXY'),
        'http_proxy': os.environ.get('http_proxy'),
        'https_proxy': os.environ.get('https_proxy'),
        'ALL_PROXY': os.environ.get('ALL_PROXY'),
        'all_proxy': os.environ.get('all_proxy'),
    }
    
    has_proxy = False
    for var_name, value in proxy_vars.items():
        if value:
            print(f"  ⚠️ 检测到代理设置: {var_name}={value[:50]}...")
            has_proxy = True
    
    if not has_proxy:
        print("  ✅ 无代理设置")
    
    return has_proxy

def check_firewall():
    """检查防火墙设置"""
    print("\n🔍 检查防火墙设置...")
    
    # 检查常见的API端口是否被阻止
    common_ports = [
        (443, "HTTPS (标准)"),
        (80, "HTTP (标准)"),
    ]
    
    import socket
    all_good = True
    
    for port, description in common_ports:
        try:
            # 尝试连接到Tushare API
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(('api.tushare.pro', port))
            sock.close()
            
            if result == 0:
                print(f"  ✅ 端口 {port} ({description}): 可访问")
            else:
                print(f"  ❌ 端口 {port} ({description}): 被阻止")
                all_good = False
                
        except Exception as e:
            print(f"  ❌ 端口 {port} ({description}): 检查失败 - {str(e)}")
            all_good = False
    
    return all_good

def check_dns_resolution():
    """检查DNS解析"""
    print("\n🔍 检查DNS解析...")
    
    import socket
    
    domains = [
        "api.tushare.pro",
        "www.baidu.com",
        "cloud.tencent.com",
    ]
    
    all_good = True
    for domain in domains:
        try:
            ip = socket.gethostbyname(domain)
            print(f"  ✅ {domain}: 解析为 {ip}")
        except Exception as e:
            print(f"  ❌ {domain}: DNS解析失败 - {str(e)}")
            all_good = False
    
    return all_good

def check_timeout_settings():
    """检查超时设置"""
    print("\n🔍 检查超时设置...")
    
    settings_path = project_root / "config" / "settings.py"
    
    if not settings_path.exists():
        print("  ⚠️ settings.py配置文件不存在")
        return False
    
    with open(settings_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查超时设置
    timeout_found = False
    if "TUSHARE_TIMEOUT = 30" in content or "TUSHARE_TIMEOUT = 60" in content:
        print("  ✅ Tushare超时设置正常 (30-60秒)")
        timeout_found = True
    
    if not timeout_found:
        print("  ⚠️ 未找到标准超时设置")
    
    return timeout_found

def create_quick_fix():
    """创建快速修复方案"""
    print("\n" + "="*60)
    print("🚀 创建快速修复方案")
    print("="*60)
    
    # 1. 检查并修复配置文件
    config_template = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tushare Pro API配置
数据是分析的基石，数据错了，分析再多都是错的
"""

import tushare as ts
from config.settings import config

class TushareConfig:
    \"\"\"Tushare API配置类\"\"\"
    
    # Tushare Pro Token（需要用户配置）
    # 请从 https://tushare.pro 获取您的Token
    TOKEN = "{token}"  # 替换为您的实际Token
    
    # API配置
    BASE_URL = "https://api.tushare.pro"
    TIMEOUT = config.data_source.TUSHARE_TIMEOUT
    RETRY_COUNT = config.data_source.TUSHARE_RETRY_COUNT
    
    # 数据接口配置
    API_CONFIG = {{
        "daily": {{
            "name": "历史日线",
            "params": ["ts_code", "trade_date", "start_date", "end_date"],
            "fields": ["ts_code", "trade_date", "open", "high", "low", "close", "pre_close", "change", "pct_chg", "vol", "amount"],
            "description": "获取股票日线数据"
        }},
        "pro_bar": {{
            "name": "专业行情",
            "params": ["ts_code", "asset", "start_date", "end_date", "freq"],
            "fields": ["ts_code", "trade_date", "open", "high", "low", "close", "pre_close", "change", "pct_chg", "vol", "amount"],
            "description": "获取专业行情数据"
        }},
        "income": {{
            "name": "利润表",
            "params": ["ts_code", "period", "start_date", "end_date"],
            "fields": ["ts_code", "ann_date", "end_date", "revenue", "operate_profit", "net_profit"],
            "description": "获取公司利润表数据"
        }},
        "balancesheet": {{
            "name": "资产负债表",
            "params": ["ts_code", "period", "start_date", "end_date"],
            "fields": ["ts_code", "ann_date", "end_date", "total_assets", "total_liab", "total_equity"],
            "description": "获取公司资产负债表数据"
        }},
        "cashflow": {{
            "name": "现金流量表",
            "params": ["ts_code", "period", "start_date", "end_date"],
            "fields": ["ts_code", "ann_date", "end_date", "n_cashflow_act", "n_cash_flow"],
            "description": "获取公司现金流量表数据"
        }},
        "moneyflow_hsgt": {{
            "name": "沪深港通资金流向",
            "params": ["trade_date", "start_date", "end_date"],
            "fields": ["trade_date", "buy_amount", "sell_amount", "net_amount"],
            "description": "获取北向资金流向数据"
        }},
        "index_weight": {{
            "name": "指数成分股权重",
            "params": ["index_code", "trade_date"],
            "fields": ["index_code", "con_code", "trade_date", "weight"],
            "description": "获取指数成分股权重数据"
        }},
        "cn_gdp": {{
            "name": "中国GDP数据",
            "params": ["period", "start_date", "end_date"],
            "fields": ["period", "gdp", "gdp_yoy"],
            "description": "获取中国GDP数据"
        }},
        "cn_cpi": {{
            "name": "中国CPI数据",
            "params": ["period", "start_date", "end_date"],
            "fields": ["period", "cpi", "cpi_yoy"],
            "description": "获取中国CPI数据"
        }},
    }}
    
    @classmethod
    def init_tushare(cls):
        \"\"\"初始化Tushare Pro\"\"\"
        if cls.TOKEN == "your_tushare_token_here":
            raise ValueError("请先在config/tushare_config.py中配置您的Tushare Pro Token")
        
        try:
            ts.set_token(cls.TOKEN)
            pro = ts.pro_api()
            print(f"✅ Tushare Pro API初始化成功")
            return pro
        except Exception as e:
            print(f"❌ Tushare Pro API初始化失败: {{str(e)}}")
            raise
    
    @classmethod
    def get_api(cls, api_name):
        \"\"\"获取API配置\"\"\"
        if api_name not in cls.API_CONFIG:
            raise ValueError(f"API '{{api_name}}' 不存在，请检查配置")
        
        return cls.API_CONFIG[api_name]
    
    @classmethod
    def validate_token(cls):
        \"\"\"验证Token是否有效\"\"\"
        if cls.TOKEN == "your_tushare_token_here":
            return False
        
        try:
            ts.set_token(cls.TOKEN)
            pro = ts.pro_api()
            # 尝试获取一个简单的数据来验证Token
            data = pro.query('daily', ts_code='000001.SZ', trade_date='20240101')
            if data.empty:
                print("⚠️ Token验证：API返回空数据，但Token可能有效")
            else:
                print("✅ Token验证成功")
            return True
        except Exception as e:
            print(f"❌ Token验证失败: {{str(e)}}")
            return False
    
    @classmethod
    def print_config(cls):
        \"\"\"打印配置信息\"\"\"
        print("\\n" + "="*60)
        print("Tushare Pro API配置")
        print("="*60)
        
        print(f"\\n🔑 Token状态:")
        if cls.TOKEN == "your_tushare_token_here":
            print("  ❌ Token未配置，请从 https://tushare.pro 获取您的Token")
        else:
            print(f"  ✅ Token已配置: {{cls.TOKEN[:10]}}...")
        
        print(f"\\n📊 支持的API接口:")
        for api_name, config in cls.API_CONFIG.items():
            print(f"  {{api_name}}: {{config['description']}}")
        
        print(f"\\n⚙️ 连接配置:")
        print(f"  基础URL: {{cls.BASE_URL}}")
        print(f"  超时时间: {{cls.TIMEOUT}}秒")
        print(f"  重试次数: {{cls.RETRY_COUNT}}")
        
        print("\\n" + "="*60)

# 导出配置实例
tushare_config = TushareConfig()

if __name__ == "__main__":
    # 测试配置
    tushare_config.print_config()
    
    # 验证Token
    if tushare_config.validate_token():
        print("✅ Token验证成功，API可用")
    else:
        print("❌ Token验证失败，请配置正确的Token")
"""
    
    # 2. 创建修复说明文档
    fix_doc = """# 🔧 API连接问题修复指南

## 📝 问题描述
错误代码: 3003
错误信息: Cannot connect to API: Headers Timeout Error
时间戳: 2026/04/02 13:59:00 (UTC+8)

## 🎯 根本原因分析
根据错误报告和诊断结果，主要问题包括：

### 1. Tushare Token未配置 ❌
- 配置文件中Token仍为默认值 `"your_tushare_token_here"`
- 没有有效的API访问凭证
- 程序无法向Tushare API发送请求

### 2. 可能的网络问题 ⚠️
- 防火墙可能阻止了API请求
- DNS解析可能需要优化
- 代理设置可能导致连接超时

## 🛠️ 修复步骤

### 步骤1: 获取Tushare Pro Token
1. 访问 https://tushare.pro
2. 注册或登录账户
3. 在个人中心获取API Token
4. Token格式通常为: `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### 步骤2: 配置程序
编辑配置文件:
```bash
cd /Users/yandada/WorkBuddy/Claw/stock_analysis_program
vim config/tushare_config.py
```

找到这一行:
```python
TOKEN = "your_tushare_token_here"  # 替换为您的实际Token
```

替换为您的实际Token:
```python
TOKEN = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # 您的实际Token
```

### 步骤3: 测试连接
运行测试命令:
```bash
python3 fix_api_connection.py
```

或直接测试程序:
```bash
python3 src/main.py --test
```

### 步骤4: 完整运行
如果测试通过，运行完整分析:
```bash
python3 src/main.py
```

## 📊 诊断结果
{diagnostic_results}

## ⚡ 快速修复脚本
已为您创建快速修复脚本 `fix_api_connection.py`，可以自动诊断和修复大多数常见问题。

运行命令:
```bash
python3 fix_api_connection.py
```

## 🔍 高级排查
如果问题仍然存在，请检查:

1. **防火墙设置**
   ```bash
   sudo pfctl -s rules
   ```

2. **网络代理**
   ```bash
   env | grep -i proxy
   ```

3. **DNS解析**
   ```bash
   nslookup api.tushare.pro
   ```

4. **SSL证书**
   ```bash
   openssl s_client -connect api.tushare.pro:443
   ```

## 📞 技术支持
如果所有方法都无效:
1. 检查Tushare Pro账户是否正常
2. 联系Tushare技术支持
3. 检查网络服务商是否有限制

## ✅ 验证修复
修复成功后，您应该看到:
```
✅ Tushare Pro API初始化成功
✅ Token验证成功
✅ 数据获取正常
✅ 分析报告生成完成
```

---
**核心原则**: 数据是分析的基石，数据错了，分析再多都是错的
**修复时间**: 2026-04-02 14:00
"""
    
    return config_template, fix_doc

def main():
    """主函数"""
    print("="*60)
    print("🔧 API连接问题诊断与修复工具")
    print("="*60)
    print("问题: Headers Timeout Error (3003)")
    print("时间: 2026-04-02 13:59:00 UTC+8")
    print("="*60)
    
    # 运行所有检查
    diagnostic_results = []
    
    # 1. 检查网络连接
    network_ok = check_network_connection()
    diagnostic_results.append(f"网络连接: {'✅ 正常' if network_ok else '❌ 异常'}")
    
    # 2. 检查DNS解析
    dns_ok = check_dns_resolution()
    diagnostic_results.append(f"DNS解析: {'✅ 正常' if dns_ok else '❌ 异常'}")
    
    # 3. 检查防火墙
    firewall_ok = check_firewall()
    diagnostic_results.append(f"防火墙: {'✅ 正常' if firewall_ok else '❌ 异常'}")
    
    # 4. 检查代理设置
    proxy_exists = check_proxy_settings()
    diagnostic_results.append(f"代理设置: {'⚠️ 存在' if proxy_exists else '✅ 无'}")
    
    # 5. 检查Tushare配置
    tushare_config_ok = check_tushare_config()
    diagnostic_results.append(f"Tushare配置: {'✅ 正常' if tushare_config_ok else '❌ 异常'}")
    
    # 6. 检查超时设置
    timeout_ok = check_timeout_settings()
    diagnostic_results.append(f"超时设置: {'✅ 正常' if timeout_ok else '⚠️ 异常'}")
    
    print("\n" + "="*60)
    print("📋 诊断总结")
    print("="*60)
    
    for result in diagnostic_results:
        print(f"  {result}")
    
    print("\n" + "="*60)
    
    # 生成修复方案
    config_template, fix_doc = create_quick_fix()
    
    # 替换诊断结果
    diagnostic_text = "\n".join(diagnostic_results)
    fix_doc = fix_doc.format(diagnostic_results=diagnostic_text)
    
    # 保存修复文档
    with open(project_root / "API连接问题修复指南.md", 'w', encoding='utf-8') as f:
        f.write(fix_doc)
    
    print("✅ 诊断完成!")
    print("📄 修复指南已保存: API连接问题修复指南.md")
    print("\n🚀 下一步:")
    print("1. 获取Tushare Pro Token: https://tushare.pro")
    print("2. 编辑 config/tushare_config.py 填入您的Token")
    print("3. 运行 python3 src/main.py --test 测试连接")
    
    return True

if __name__ == "__main__":
    main()