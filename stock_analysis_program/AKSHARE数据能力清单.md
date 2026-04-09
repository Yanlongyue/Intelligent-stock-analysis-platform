# AkShare 数据能力清单

> 本文档列出当前项目通过 AkShare 可获取的全部真实数据类型
> 更新日期：2026-04-09

---

## 一、当前已集成的数据接口

### 1. 个股日线行情 ✅
**接口函数**：`get_daily_quotes(ts_code, start_date, end_date)`

**数据来源**：
- 方案1：腾讯财经 `stock_zh_a_hist_tx`（优先）
- 方案2：东方财富 `stock_zh_a_hist`（备用，带重试）
- 方案3：实时行情 `stock_zh_a_spot_em`（兜底）

**返回字段**：
```python
{
    "trade_date": "日期",
    "open": "开盘价",
    "high": "最高价",
    "low": "最低价",
    "close": "收盘价",
    "vol": "成交量",
    "amount": "成交额",
    "pct_chg": "涨跌幅"
}
```

**使用示例**：
```python
provider = AkShareDataProvider()
data = provider.get_daily_quotes("601868.SH", start_date="20250301", end_date="20250409")
```

---

### 2. 指数日线行情 ✅
**接口函数**：`get_index_daily(ts_code, start_date, end_date)`

**数据来源**：
- 方案1：东方财富 `stock_zh_index_daily_em`
- 方案2：实时指数 `stock_zh_index_spot_em`
- 方案3：全球指数 `index_global_spot_em`

**支持指数**：
- 上证指数 (000001.SH)
- 深证成指 (399001.SZ)
- 创业板指 (399006.SZ)
- 沪深300 (000300.SH)
- 中证500 (000905.SH)

**返回字段**：
```python
{
    "trade_date": "日期",
    "close": "收盘价",
    "pct_chg": "涨跌幅"
}
```

---

### 3. 实时价格 ✅
**接口函数**：`get_stock_realtime_price(ts_code)`

**数据来源**：通过日线接口获取最新收盘价

---

### 4. 市场概况 ✅
**接口函数**：`get_market_overview()`

**数据来源**：
- 指数行情：`stock_zh_index_daily_em`
- 市场资金流向：`stock_market_fund_flow`
- 市场活跃度：`stock_market_activity_legu`

**返回字段**：
```python
{
    "indices": [...],           # 主要指数数据
    "market_flow": {...},       # 主力资金流向
    "market_activity": {...}    # 涨跌家数统计
}
```

---

### 5. 北向资金流向 ✅
**接口函数**：`get_north_money_flow(start_date, end_date)` / `get_moneyflow_hsgt()`

**数据来源**：
- 方案1：北向持股统计 `stock_hsgt_hold_stock_em`
- 方案2：个股明细 `stock_hsgt_individual_em`
- 方案3：板块排行 `stock_hsgt_board_rank_em`

**返回字段**：
```python
{
    "trade_date": "交易日期",
    "net_amount": "净流入金额",
    "total_holdings": "持股数量"
}
```

---

### 6. 涨停池数据 ✅
**接口函数**：`get_limit_list(trade_date)`

**数据来源**：`stock_zt_pool_em`（东方财富涨停池）

**返回字段**：
```python
{
    "ts_code": "代码",
    "name": "名称",
    "p_change": "涨跌幅",
    "amount": "成交额",
    "reason": "涨停原因"
}
```

---

### 7. 股票新闻 ✅
**接口函数**：`get_stock_news(symbol)`

**数据来源**：`stock_news_em`

**返回字段**：
```python
{
    "title": "新闻标题",
    "content": "新闻内容",
    "time": "发布时间",
    "source": "新闻来源"
}
```

---

## 二、AkShare 还能获取但未集成的数据（推荐补充）

### 1. 个股实时行情快照 📌 强烈推荐
**AkShare 接口**：`stock_zh_a_spot_em`

**数据内容**：全市场5000+股票的实时行情
```python
ak.stock_zh_a_spot_em()
# 返回：最新价、涨跌幅、成交量、成交额、换手率、振幅等
```

**建议**：用这个替换目前的日线数据获取实时价格，延迟更低

---

### 2. 个股财务指标 📌 强烈推荐
**AkShare 接口**：
- `stock_financial_report_em` - 财务报表（三大表）
- `stock_yjbb_em` - 业绩快报
- `stock_yysj_em` - 预约披露时间

**数据内容**：
- 营业收入、净利润
- ROE、ROA
- 资产负债率
- 每股收益(EPS)
- 市盈率(PE)、市净率(PB)

---

### 3. 资金流向 📌 强烈推荐
**AkShare 接口**：
- `stock_individual_fund_flow_em` - 个股资金流向
- `stock_sector_fund_flow` - 板块资金流向
- `stock_market_fund_flow` - 市场资金流向

**数据内容**：
- 主力净流入/流出
- 超大单/大单/中单/小单资金流向
- 净流入占比

---

### 4. 龙虎榜详情 📌 推荐
**AkShare 接口**：
- `stock_lhb_detail_daily_sina` - 龙虎榜详情
- `stock_lhb_stock_detail_em` - 个股龙虎榜

**数据内容**：
- 上榜营业部
- 买入/卖出金额
- 净买入金额
- 机构专用席位

---

### 5. 板块/行业数据 📌 推荐
**AkShare 接口**：
- `stock_board_industry_name_em` - 行业板块列表
- `stock_board_concept_name_em` - 概念板块列表
- `stock_board_industry_spot_em` - 行业板块行情
- `stock_board_concept_spot_em` - 概念板块行情

**数据内容**：
- 各行业/概念涨跌幅排名
- 领涨个股
- 板块资金流向

---

### 6. 融资融券数据 📌 推荐
**AkShare 接口**：
- `stock_margin_detail_sse` - 上交所两融明细
- `stock_margin_detail_szse` - 深交所两融明细

**数据内容**：
- 融资余额
- 融券余量
- 融资融券余额差

---

### 7. 个股公告 📌 推荐
**AkShare 接口**：`stock_notice_report_em`

**数据内容**：
- 公司公告
- 业绩预告
- 重大事项

---

### 8. 期权数据
**AkShare 接口**：
- `option_finance_board_em` - 金融期权
- `option_commodity_exchange_em` - 商品期权

---

### 9. 债券数据
**AkShare 接口**：
- `bond_zh_hs_spot` - 沪深债券行情
- `bond_convertible_jsl` - 可转债数据

---

### 10. 期货数据
**AkShare 接口**：
- `futures_zh_spot` - 期货实时行情
- `futures_main_sina` - 期货主力合约

---

## 三、数据优先级策略（当前实现）

```
获取数据时按以下顺序尝试：

Tushare Pro (API调用)
    ↓ 失败/无权限
AkShare (东方财富/腾讯财经)
    ↓ 失败
返回空结构（不再使用模拟数据）
```

---

## 四、立即可用的增强建议

### 建议1：个股实时快照替换日线接口
当前：`get_daily_quotes` 获取日线后再取最新一条
优化：直接使用 `stock_zh_a_spot_em` 获取全市场实时快照

**优势**：
- 延迟更低（秒级 vs 分钟级）
- 可获取全市场5000+股票
- 包含换手率、振幅等更多字段

### 建议2：补充财务数据获取
使用 `stock_financial_report_em` 获取ROE、PE、PB等核心指标

### 建议3：补充资金流向
使用 `stock_individual_fund_flow_em` 获取个股主力资金流向

### 建议4：板块热点
使用 `stock_board_concept_spot_em` 获取概念板块排行

---

## 五、AkShare vs Tushare 对比

| 数据类型 | Tushare | AkShare | 备注 |
|---------|---------|---------|------|
| 日线行情 | ✅ | ✅ | 两者都稳定 |
| 实时价格 | ⚠️ 需权限 | ✅ | AkShare免费 |
| 财务指标 | ✅ 需积分 | ✅ | AkShare免费 |
| 资金流向 | ✅ 需权限 | ✅ | AkShare免费 |
| 龙虎榜 | ✅ 需权限 | ✅ | AkShare免费 |
| 北向资金 | ✅ 需权限 | ✅ | AkShare免费 |
| 板块数据 | ✅ 需权限 | ✅ | AkShare免费 |
| 融资融券 | ✅ 需权限 | ✅ | AkShare免费 |
| 新闻快讯 | ✅ | ✅ | 两者都可用 |
| 宏观经济 | ✅ | ✅ | AkShare更丰富 |

---

## 六、当前代码中的调用位置

| 数据类型 | 后端API端点 | 调用函数 |
|---------|------------|---------|
| 日线行情 | `/api/price_history/<code>` | `get_daily_quotes` |
| 指数日线 | `/api/index_daily/<code>` | `get_index_daily` |
| 市场概况 | `/api/market_overview` | `get_market_overview` |
| 北向资金 | `/api/moneyflow_hsgt` | `get_moneyflow_hsgt` |
| 涨停池 | `/api/limit_list_d` | `get_limit_list_d` |
| 股票新闻 | `/api/news` | `get_news` |
| 实时价格 | 内部使用 | `get_stock_realtime_price` |
| 每日基本面 | `/api/daily_basic/<code>` | `get_daily_basic` |

---

## 七、完整数据链路图

```
┌─────────────────────────────────────────────────────────────┐
│                     数据消费者层                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ 持仓管理 │ │ 分析引擎 │ │ 市场概况 │ │ 价格历史 │       │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘       │
└───────┼────────────┼────────────┼────────────┼─────────────┘
        │            │            │            │
        └────────────┴────────────┴────────────┘
                         │
              ┌──────────▼──────────┐
              │   FallbackDataProvider  │
              │   (链式回退数据提供者)  │
              └──────────┬──────────┘
                         │
           ┌─────────────┼─────────────┐
           │             │             │
           ▼             ▼             ▼
    ┌──────────┐  ┌──────────┐  ┌──────────┐
    │ Tushare  │  │ AkShare  │  │   Mock   │
    │ Pro API  │  │ 东方财富 │  │ (已禁用) │
    │ 需Token  │  │ 免费     │  │         │
    └──────────┘  └──────────┘  └──────────┘
           │             │             │
           │    ┌────────┼────────┐   │
           │    │        │        │   │
           │    ▼        ▼        ▼   │
           │ 腾讯财经  东方财富  交易所 │
           │          实时行情        │
           │                        │
           └────────────────────────┘
                      │
              ┌───────▼────────┐
              │   MySQL数据库   │
              │  (持久化存储)   │
              └────────────────┘
```

---

**总结**：
- ✅ 当前已实现7大类真实数据获取
- ✅ AkShare 免费提供Tushare需要高权限的数据
- 📝 建议补充：实时快照、财务指标、个股资金流向
- 🚫 不再使用模拟数据，真实数据失败时返回空结构
