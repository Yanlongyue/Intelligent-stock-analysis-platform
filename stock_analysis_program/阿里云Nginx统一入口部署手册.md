# 阿里云 Nginx 统一入口部署手册（宝塔逐步操作版）

> 目标：把前端和后端一起部署到阿里云服务器，由 Nginx 统一对外提供访问入口。
>
> 最终访问方式：
> - 首页：`http://101.133.150.164/`
> - API：`http://101.133.150.164/api/...`
>
> 后续绑定域名并启用 HTTPS 后：
> - `https://你的域名/`
> - `https://你的域名/api/...`

---

## 一、这次部署的最终形态

### 1. 架构分工

- **Nginx**：统一对外入口，负责静态前端托管和 `/api/` 反向代理。
- **Python 后端**：运行 `real_data_backend.py`，仅监听服务器本机 `9000`。
- **前端页面**：直接放在服务器站点目录，由 Nginx 提供访问。
- **浏览器**：只访问 `80/443`，不再直接访问 `9000`。

### 2. 当前代码已完成的配套调整

- `stock_analysis_program/config.js` 已切换为生产环境 **same-origin** 模式。
- 前端上线后会自动使用当前站点 origin 作为 API 基础地址。
- 已提供 `stock_analysis_program/nginx.stock-analysis.conf.sample` 作为 Nginx 配置样例。

这意味着：

- 本地开发：仍走 `http://localhost:9000`
- 线上部署：走当前站点同源 `/api`
- 旧路线“GitHub Pages + 公网 9000 裸 API”不再作为正式方案

---

## 二、部署前检查清单

在宝塔里开始操作前，先确认这几件事：

- 已能登录阿里云服务器
- 已能登录宝塔面板
- 宝塔版本：`9.2.0`
- 代码目录已准备上传或可通过 Git 拉取
- 已有 Tushare Token，并准备通过环境变量注入
- 阿里云安全组已开放 `80`
- 如果后面要上 HTTPS，再开放 `443`

### 端口策略

**推荐策略：**

- 公网开放：`80`、`443`
- 本机内部使用：`9000`
- 不建议长期对公网暴露：`9000`

> 如果你只是为了临时排查，可短时间放开 `9000`，但上线稳定后应及时关闭。

---

## 三、推荐服务器目录

### 方案 A：整仓库部署（推荐）

```text
/www/wwwroot/Intelligent-stock-analysis-platform/
```

前后端实际代码目录：

```text
/www/wwwroot/Intelligent-stock-analysis-platform/stock_analysis_program/
```

### 方案 B：只上传业务目录

```text
/www/wwwroot/stock_analysis_program/
```

> 后续所有宝塔和 Nginx 配置，关键只有一件事：**Nginx 和 Python 必须指向同一份线上代码。**

---

## 四、宝塔里先装哪些东西

### 1. 打开软件商店

宝塔左侧菜单：

- **软件商店**

安装这些组件：

- `Nginx`
- `Python 项目管理器`
- `Python 3.10` 或 `Python 3.11`

### 2. 可选安装

如果你更习惯守护进程方式，也可以额外安装：

- `Supervisor` 或宝塔的守护进程管理插件

---

## 五、上传代码到服务器

### 方式 A：Git 拉取（推荐）

宝塔左侧菜单：

- **终端**

执行：

```bash
cd /www/wwwroot
git clone https://github.com/Yanlongyue/Intelligent-stock-analysis-platform.git
```

完成后代码目录一般是：

```text
/www/wwwroot/Intelligent-stock-analysis-platform/stock_analysis_program/
```

### 方式 B：宝塔文件管理器上传

宝塔左侧菜单：

- **文件** → 进入 `/www/wwwroot/`

操作顺序：

1. 点击“上传”
2. 上传项目压缩包
3. 右键解压
4. 确认最终目录中能看到：
   - `real_data_backend.py`
   - `real_data_frontend.html`
   - `config.js`
   - `data/`

---

## 六、先把后端跑起来

### 第 1 步：安装依赖

宝塔左侧菜单：

- **终端**

如果你是整仓库部署，执行：

```bash
cd /www/wwwroot/Intelligent-stock-analysis-platform/stock_analysis_program
pip3 install -r requirements.txt
```

如果 `pip3` 不可用，可以改成系统实际可用版本，例如：

```bash
python3 -m pip install -r requirements.txt
```

### 第 2 步：确认 Python 可用

执行：

```bash
python3 --version
```

建议使用：

- `Python 3.10`
- `Python 3.11`

### 第 3 步：先手动验证后端能启动

执行：

```bash
cd /www/wwwroot/Intelligent-stock-analysis-platform/stock_analysis_program
python3 real_data_backend.py
```

如果启动正常，另开一个终端窗口执行：

```bash
curl http://127.0.0.1:9000/api/health
curl http://127.0.0.1:9000/api/data_status
```

只要能返回 JSON，说明后端基本没问题。

验证后按 `Ctrl+C` 停止，下一步改为宝塔托管常驻运行。

---

## 七、宝塔里如何添加 Python 项目

宝塔左侧菜单：

- **Python 项目管理器**

点击：

- **添加项目**

### 1. 推荐填写示例

> 不同版本宝塔的字段名字可能略有差异，例如“启动文件 / 启动命令 / 运行方式”可能不完全一样，但核心值不变。

| 字段 | 推荐填写内容 |
|------|--------------|
| 项目名称 | `stock-analysis-api` |
| 项目路径 | `/www/wwwroot/Intelligent-stock-analysis-platform/stock_analysis_program` |
| Python 版本 | 选择已安装的 `3.10` 或 `3.11` |
| 启动方式 | 脚本启动 |
| 启动文件 | `real_data_backend.py` |
| 运行端口 | `9000` |
| 开机自启 | 开启 |
| 工作目录 | 与项目路径一致 |

### 2. 环境变量怎么填

如果界面里有“环境变量”区域，新增：

| 变量名 | 值 |
|-------|----|
| `TUSHARE_TOKEN` | 你的真实 Token |

> 不要把 Token 写进代码、文档、仓库配置里。环境变量才是正路。

### 3. 如果界面不是“启动文件”而是“启动命令”

直接填：

```bash
python3 real_data_backend.py
```

如果宝塔要求写绝对路径，可以填：

```bash
/www/server/pyenv/versions/3.10.x/bin/python3 real_data_backend.py
```

### 4. 添加后立即验证

项目添加完成后：

1. 点击“启动”
2. 确认状态变为“运行中”
3. 再到终端执行：

```bash
curl http://127.0.0.1:9000/api/health
```

如果这里通了，再继续配 Nginx。

---

## 八、宝塔里如何新建网站并挂前端

宝塔左侧菜单：

- **网站**

点击：

- **添加站点**

### 1. 先用 IP 建站也可以

如果还没有域名，可以先填：

- 站点域名：`101.133.150.164`

### 2. 关键字段这样填

| 字段 | 推荐填写内容 |
|------|--------------|
| 域名 | `101.133.150.164`（或后续正式域名） |
| 根目录 | `/www/wwwroot/Intelligent-stock-analysis-platform/stock_analysis_program` |
| PHP 版本 | 纯静态 / 不使用 PHP |
| 数据库 | 不创建 |

### 3. 建站完成后先别急着测页面

因为默认站点首页未必会自动指向 `real_data_frontend.html`，下一步需要改 Nginx 配置。

---

## 九、宝塔里如何替换 Nginx 配置

### 第 1 步：找到站点配置入口

宝塔左侧菜单：

- **网站** → 找到你的站点 → **设置** → **配置文件**

### 第 2 步：使用项目自带样例

项目里已有样例文件：

```text
stock_analysis_program/nginx.stock-analysis.conf.sample
```

你可以：

1. 打开样例文件
2. 复制整段 `server { ... }`
3. 粘贴覆盖宝塔站点配置中的对应 `server` 块

### 第 3 步：至少检查这 4 个地方

| 配置项 | 应该改成什么 |
|-------|--------------|
| `server_name` | `101.133.150.164` 或你的域名 |
| `root` | 线上实际前端目录 |
| `access_log` | `/www/wwwlogs/stock-analysis.access.log` |
| `error_log` | `/www/wwwlogs/stock-analysis.error.log` |

### 第 4 步：保存并重载

在宝塔配置文件页面：

1. 点击“保存”
2. 如果弹出语法检查，先确认通过
3. 点击“重载 Nginx”

---

## 十、你最终应该看到的 Nginx 行为

Nginx 配好后，应满足下面 3 个条件：

### 1. 首页请求

访问：

```text
http://101.133.150.164/
```

应打开：

- `real_data_frontend.html`

### 2. API 请求

访问：

```text
http://101.133.150.164/api/health
```

应被代理到：

```text
http://127.0.0.1:9000/api/health
```

### 3. 前端请求逻辑

前端会自动使用当前站点 origin，因此浏览器实际请求会变成：

```text
http://101.133.150.164/api/...
```

而不是去请求裸露的 `9000`。

---

## 十一、按顺序怎么验收

别乱跳，按这个顺序验：

### 验收 1：后端本机能通

在服务器终端执行：

```bash
curl http://127.0.0.1:9000/api/health
```

### 验收 2：Nginx 代理能通

在服务器终端执行：

```bash
curl http://127.0.0.1/api/health
```

或者：

```bash
curl http://101.133.150.164/api/health
```

### 验收 3：首页能打开

浏览器访问：

```text
http://101.133.150.164/
```

### 验收 4：前端功能正常

重点确认：

- 页面能正常加载
- 浏览器控制台不再出现 mixed content 错误
- `/api/positions` 可正常读写
- `/api/data_status` 返回合理状态
- 分析请求能打到真实后端

---

## 十二、上线后立刻要做的安全动作

### 1. 收口 9000

当 `/api/` 代理已经稳定后：

- 阿里云安全组关闭公网 `9000`
- 宝塔防火墙关闭公网 `9000`
- 保留 `80/443`

### 2. 绑定域名后上 HTTPS

如果已有域名：

宝塔左侧菜单：

- **网站** → 目标站点 → **SSL**

操作：

1. 申请 Let's Encrypt 免费证书
2. 开启 SSL
3. 配置 `80 -> 443` 跳转
4. 再次验证：
   - `https://你的域名/`
   - `https://你的域名/api/health`

### 3. 不要回退到旧路线

正式部署后，不建议再用：

- GitHub Pages 托管正式前端
- 浏览器直连 `http://公网IP:9000`

因为这两种方式都不适合作为长期正式部署方案。

---

## 十三、出问题时先看哪里

### 情况 1：页面打不开

优先检查：

- 站点目录是否填对
- `real_data_frontend.html` 是否存在
- Nginx 是否已重载成功

### 情况 2：页面能打开但没有数据

优先检查：

- `curl http://127.0.0.1:9000/api/health`
- `curl http://101.133.150.164/api/health`
- Nginx `/api/` 反代是否生效
- `TUSHARE_TOKEN` 是否正确注入

### 情况 3：Python 项目总是掉

优先检查：

- Python 版本是否正确
- 启动命令是否写对
- 日志里是否缺依赖
- 项目工作目录是否填错

### 情况 4：HTTPS 上了但前端还是报错

优先检查：

- 页面是否真的走 `https://`
- `/api/` 是否也走同域 `https://`
- 是否还有旧缓存
- 是否仍有某个地方硬编码旧的 `http://IP:9000`

---

## 十四、一句话收口

> 这套系统的正式部署路线已经很明确：**前端和后端一起放到阿里云，Nginx 做统一入口，浏览器只访问 80/443，后端 9000 只留给服务器本机。**

---

*更新说明：2026-04-08 13:21，已补齐宝塔逐步操作路径、字段填写示例、验收顺序与安全收口步骤。*
