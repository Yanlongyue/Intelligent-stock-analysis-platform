# 🚀 Gitee Pages + 后端API部署方案 (方案B)

## 📋 **方案概述**

### **架构设计**
```
┌─────────────────────────┐      ┌─────────────────────────┐      ┌─────────────────────────┐
│    Gitee Pages          │      │    后端API服务          │      │    数据源               │
│   (前端静态文件)        │◄────►│    (Python Flask)       │◄────►│    (Tushare/实时)       │
│   • 网页界面            │      │   • 五维度算法          │      │   • 股票数据            │
│   • 用户交互            │      │   • 数据计算            │      │   • 财务数据            │
│   • 图表展示            │      │   • API接口            │      │   • 新闻数据            │
│   • 响应式设计          │      │   • 数据缓存            │      │                        │
└─────────────────────────┘      └─────────────────────────┘      └─────────────────────────┘
   https://xxx.gitee.io/               https://api.example.com/           https://api.tushare.pro/
           │                                     │                                    │
           └───────────── CORS跨域 ──────────────┘                                    │
                                                                                     │
                                                                         ┌───────────┴───────────┐
                                                                         │     您的Mac/服务器     │
                                                                         │   • 运行API服务        │
                                                                         │   • 数据更新任务       │
                                                                         └───────────────────────┘
```

---

## 🎯 **部署目标**

1. **前端**: Gitee Pages - 免费、稳定、HTTPS
2. **后端**: 3种选项可选（根据需求和技术能力）
3. **数据**: 实时股票数据 + 五维度算法
4. **访问**: 任何设备、任何网络、随时随地

---

## 📋 **部署步骤**

### **阶段1：后端API服务部署**

#### **选项A：本地后端 + 内网穿透**（推荐新手）
**优点**: 零成本、快速部署  
**缺点**: 需要电脑一直开机

**步骤**:
1. 在您的Mac运行Python后端
2. 使用ngrok/Cloudflare Tunnel暴露API
3. 前端通过外网URL调用API

```bash
# 1. 启动后端服务
cd /Users/yandada/WorkBuddy/Claw/stock_analysis_program
export TUSHARE_TOKEN=your_tushare_pro_token_here
python3 real_data_backend.py

# 2. 使用ngrok暴露服务（需要注册ngrok账号）
ngrok http 9000
# 会得到：https://xxxx-xxx-xxx-xxx.ngrok-free.app

# 3. 将 config.js 的 production 改成 ngrok 地址，或直接运行一键部署脚本自动生成
```

#### **选项B：云服务器部署**（最稳定）
**优点**: 7x24小时运行、高性能  
**缺点**: 每月约50元成本

**步骤**:
1. 购买腾讯云/阿里云轻量服务器
2. 部署Python后端 + Nginx
3. 配置域名和SSL证书

**推荐配置**:
- CPU: 1核
- 内存: 2GB
- 系统: Ubuntu 22.04
- 月费: 约50元

#### **选项C：Serverless函数**（最经济）
**优点**: 按调用付费、零运维  
**缺点**: 冷启动延迟

**步骤**:
1. 注册腾讯云SCF/阿里云函数计算
2. 部署Python函数
3. 配置API网关

---

### **阶段2：前端Gitee Pages部署**

#### **步骤1：创建Gitee仓库**
1. 访问 https://gitee.com
2. 点击"新建仓库"
3. 填写信息：
   - 仓库名称: `stock-analysis-program`
   - 仓库介绍: 智能股票分析系统
   - **必须**: 选择"公开"仓库
   - 初始化仓库: 不勾选（我们推送现有代码）

#### **步骤2：推送代码到Gitee**
```bash
# 进入项目目录
cd /Users/yandada/WorkBuddy/Claw/stock_analysis_program

# 添加Gitee远程仓库
git remote add gitee https://gitee.com/您的用户名/stock-analysis-program.git

# 推送代码
git push gitee main
```

#### **步骤3：配置API地址**
创建配置文件 `config.js`:
```javascript
window.APP_CONFIG = {
    version: '2026.04.03-1',
    api: {
        development: 'http://localhost:9000',
        production: 'https://您的公网后端地址',
        allowQueryOverride: true
    }
};

window.resolveApiBaseUrl = function resolveApiBaseUrl() {
    const config = (window.APP_CONFIG && window.APP_CONFIG.api) || {};
    const params = new URLSearchParams(window.location.search);
    const queryApi = config.allowQueryOverride === false ? '' : (params.get('api') || '').trim();
    const hostname = window.location.hostname;
    const isLocalHost = hostname === 'localhost' || hostname === '127.0.0.1';
    const normalize = (value) => (value || '').trim().replace(/\/+$/, '');

    if (queryApi) return normalize(queryApi);
    if (isLocalHost) return normalize(config.development);
    return normalize(config.production);
};
```

前端页面中统一读取配置：
```html
<script src="config.js?v=20260403-1"></script>
```

```javascript
const runtime = window.getApiConfigStatus();
const apiBaseUrl = runtime.apiBaseUrl;
```

#### **步骤4：开启Gitee Pages**
1. 进入Gitee仓库 → 服务 → Gitee Pages
2. 选择分支: `main`
3. 部署目录: `/`（根目录）
4. 点击"启动"

#### **步骤5：访问网站**
等待2-5分钟，访问：
```
https://您的用户名.gitee.io/stock-analysis-program/web_interface_enhanced.html
```

---

### **阶段3：数据源配置**

#### **Tushare API配置**
1. 注册 https://tushare.pro
2. 获取API Token
3. 通过环境变量注入到后端服务

```bash
# macOS / Linux
export TUSHARE_TOKEN=your_tushare_pro_token_here

# Windows PowerShell
$env:TUSHARE_TOKEN="your_tushare_pro_token_here"
```

> ⚠️ 不要把 Token 写进 `config/tushare_config.py`、前端页面或仓库提交记录。

#### **数据更新机制**
当前项目的 `real_data_backend.py` 已内置价格缓存与按需刷新逻辑，优先建议直接通过 API 触发更新：

```bash
curl http://localhost:9000/api/update_prices
```

如果后续需要定时任务，再基于 `real_data_provider.py` 或独立调度脚本补充，不建议继续沿用旧的 `algorithm_backend.py` 更新示例。

---

## 🔧 **详细配置指南**

### **1. 后端API服务详细配置**

#### **直接使用仓库内置后端（推荐）**
本项目已经自带 `real_data_backend.py`，不需要再额外创建 `api_server.py`。

```bash
cd /Users/yandada/WorkBuddy/Claw/stock_analysis_program
export TUSHARE_TOKEN=your_tushare_pro_token_here
python3 real_data_backend.py
```

如果没有配置 `TUSHARE_TOKEN`，后端会自动降级为模拟数据模式，但 API 结构保持不变。

#### **安装依赖**
```bash
pip install -r requirements.txt
```

### **2. 前端跨域配置**

#### **CORS问题解决**
Gitee Pages访问外部API会遇到CORS限制，解决方案：

**方案A：后端配置CORS**
```python
# Flask后端添加CORS支持
from flask_cors import CORS
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "https://*.gitee.io"}})
```

**方案B：使用代理API**
创建代理服务或使用第三方CORS代理。

### **3. 性能优化**

#### **前端优化**
1. 压缩JS/CSS文件
2. 使用CDN加速
3. 实现懒加载

#### **后端优化**
1. 数据缓存（Redis/Memcached）
2. 数据库连接池
3. 异步处理

---

## 🎯 **推荐部署路线图**

### **第1天：快速部署测试版**
1. 使用**选项A（ngrok）**部署后端
2. 部署前端到Gitee Pages
3. 测试基本功能

### **第1周：完善功能**
1. 添加真实Tushare数据
2. 完善五维度算法
3. 优化用户体验

### **第1月：稳定运行**
1. 考虑迁移到**选项B（云服务器）**
2. 添加更多股票数据
3. 实现高级功能

---

## 📱 **访问方式**

### **手机访问**
```
https://您的用户名.gitee.io/stock-analysis-program/web_interface_enhanced.html
```

### **电脑访问**
- 任何浏览器直接输入上述网址
- 无需安装任何软件
- 支持Chrome、Safari、Edge、Firefox

### **平板访问**
- 完美适配响应式设计
- 触摸操作优化

---

## 🔧 **故障排除**

### **常见问题1：Gitee Pages访问空白**
**原因**: 路径错误或文件不存在
**解决**:
1. 检查文件是否推送成功
2. 确认访问路径正确
3. 查看浏览器控制台错误

### **常见问题2：API连接失败**
**原因**: CORS限制或后端服务未运行
**解决**:
1. 检查后端服务是否启动
2. 确认API地址正确
3. 检查CORS配置

### **常见问题3：数据不更新**
**原因**: Tushare API限制或配置错误
**解决**:
1. 检查Tushare Token
2. 查看API调用日志
3. 确认网络连接

---

## 📞 **技术支持**

### **遇到问题怎么办？**
1. **查看日志**: 浏览器控制台 + 后端日志
2. **检查网络**: 使用浏览器开发者工具
3. **简化测试**: 先测试本地环境，再测试部署环境

### **联系支持**
- Gitee Issues: 提交问题到仓库
- 邮件支持: 您的邮箱
- 在线文档: 本项目README

---

## 🎉 **部署成功标志**

✅ **前端访问正常**: 能打开网页界面  
✅ **API连接成功**: 显示"API已连接"  
✅ **数据显示正常**: 股票数据能正确加载  
✅ **算法计算正常**: 五维度评分能计算  
✅ **跨设备访问**: 手机、电脑都能访问  

---

## 📈 **后续扩展计划**

### **短期扩展（1个月内）**
1. 添加用户登录系统
2. 实现个性化持仓管理
3. 添加更多技术指标

### **中期扩展（3个月内）**
1. 移动App开发
2. 实时推送通知
3. 高级分析功能

### **长期扩展（6个月内）**
1. 机器学习预测模型
2. 量化交易策略
3. 社区分享功能

---

## 💡 **最佳实践建议**

### **安全性**
1. **API密钥保护**: 不要提交到Git仓库
2. **HTTPS强制**: Gitee Pages自动提供
3. **输入验证**: 前端后端双重验证

### **维护性**
1. **版本控制**: 使用Git标签管理版本
2. **备份策略**: 定期备份数据和配置
3. **监控告警**: 设置服务健康监控

### **性能**
1. **缓存策略**: 合理使用缓存减少API调用
2. **代码优化**: 定期review和优化代码
3. **负载均衡**: 高流量时考虑负载均衡

---

## 🚀 **立即开始**

### **最快开始方式**
```bash
# 1. 克隆本项目到Gitee
git clone https://gitee.com/您的用户名/stock-analysis-program.git

# 2. 启动后端服务
cd stock-analysis-program
export TUSHARE_TOKEN=your_tushare_pro_token_here
python3 real_data_backend.py

# 3. 使用ngrok暴露服务
ngrok http 9000

# 4. 更新 config.js 的 production 地址
# 5. 推送代码到Gitee
# 6. 开启Gitee Pages
```

### **一键部署脚本**
后续将提供一键部署脚本，简化所有步骤。

---

## 📚 **相关资源**

- [Gitee Pages官方文档](https://gitee.com/help/articles/4136)
- [Tushare Pro API文档](https://tushare.pro/document/2)
- [Flask官方文档](https://flask.palletsprojects.com/)
- [CORS跨域解决方案](https://developer.mozilla.org/zh-CN/docs/Web/HTTP/CORS)

---

**祝您部署顺利！有任何问题随时联系。** 🎯