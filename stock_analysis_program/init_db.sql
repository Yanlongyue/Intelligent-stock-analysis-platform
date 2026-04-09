-- ============================================================
-- 股票分析平台 MySQL 初始化脚本
-- 使用方法：在宝塔面板 -> phpMyAdmin 中执行本脚本
-- 或者：mysql -u root -p < init_db.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS `stock_analysis`
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE `stock_analysis`;

-- 持仓表
CREATE TABLE IF NOT EXISTS holdings (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    code         VARCHAR(20)   NOT NULL COMMENT '股票代码，如 601868.SH',
    name         VARCHAR(50)   NOT NULL COMMENT '股票名称',
    amount       INT           NOT NULL DEFAULT 0 COMMENT '持仓数量（股）',
    cost_price   DECIMAL(10,4) NOT NULL DEFAULT 0 COMMENT '成本价',
    stock_type   VARCHAR(20)   NOT NULL DEFAULT 'value' COMMENT 'value/growth/concept',
    industry     VARCHAR(50)   DEFAULT NULL COMMENT '所属行业',
    created_at   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_code (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='持仓表';

-- 日线行情表
CREATE TABLE IF NOT EXISTS daily_quotes (
    id           BIGINT AUTO_INCREMENT PRIMARY KEY,
    code         VARCHAR(20)   NOT NULL COMMENT '股票代码',
    trade_date   DATE          NOT NULL COMMENT '交易日期',
    open         DECIMAL(10,4) COMMENT '开盘价',
    high         DECIMAL(10,4) COMMENT '最高价',
    low          DECIMAL(10,4) COMMENT '最低价',
    close        DECIMAL(10,4) COMMENT '收盘价',
    pre_close    DECIMAL(10,4) COMMENT '昨收价',
    change_amt   DECIMAL(10,4) COMMENT '涨跌额',
    pct_chg      DECIMAL(10,4) COMMENT '涨跌幅（%）',
    vol          BIGINT        COMMENT '成交量（手）',
    amount       DECIMAL(20,4) COMMENT '成交额（千元）',
    data_source  VARCHAR(20)   DEFAULT 'AkShare' COMMENT '数据来源',
    created_at   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_code_date (code, trade_date),
    INDEX idx_code (code),
    INDEX idx_trade_date (trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='日线行情表';

-- 每日基本面指标表
CREATE TABLE IF NOT EXISTS daily_basic (
    id           BIGINT AUTO_INCREMENT PRIMARY KEY,
    code         VARCHAR(20)   NOT NULL,
    trade_date   DATE          NOT NULL,
    pe           DECIMAL(12,4) COMMENT '市盈率',
    pe_ttm       DECIMAL(12,4) COMMENT '市盈率（TTM）',
    pb           DECIMAL(12,4) COMMENT '市净率',
    ps           DECIMAL(12,4) COMMENT '市销率',
    ps_ttm       DECIMAL(12,4) COMMENT '市销率（TTM）',
    dv_ratio     DECIMAL(12,4) COMMENT '股息率（%）',
    total_mv     DECIMAL(20,4) COMMENT '总市值（万元）',
    circ_mv      DECIMAL(20,4) COMMENT '流通市值（万元）',
    turnover_rate DECIMAL(10,4) COMMENT '换手率（%）',
    volume_ratio DECIMAL(10,4) COMMENT '量比',
    data_source  VARCHAR(20)   DEFAULT 'AkShare',
    created_at   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_code_date (code, trade_date),
    INDEX idx_code (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='每日基本面指标表';

-- 市场概况快照表
CREATE TABLE IF NOT EXISTS market_overview (
    id           BIGINT AUTO_INCREMENT PRIMARY KEY,
    index_code   VARCHAR(20)   NOT NULL COMMENT '指数代码',
    index_name   VARCHAR(50)   NOT NULL COMMENT '指数名称',
    trade_date   DATE          NOT NULL COMMENT '交易日期',
    close        DECIMAL(12,4) COMMENT '收盘点位',
    pct_chg      DECIMAL(10,4) COMMENT '涨跌幅（%）',
    vol          BIGINT        COMMENT '成交量',
    amount       DECIMAL(20,4) COMMENT '成交额',
    created_at   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_index_date (index_code, trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='市场概况表';

-- 北向资金流向表
CREATE TABLE IF NOT EXISTS moneyflow_hsgt (
    id           BIGINT AUTO_INCREMENT PRIMARY KEY,
    trade_date   DATE          NOT NULL COMMENT '交易日期',
    ggt_ss       DECIMAL(20,4) COMMENT '港股通（沪）净买入（亿元）',
    ggt_sz       DECIMAL(20,4) COMMENT '港股通（深）净买入（亿元）',
    hgt          DECIMAL(20,4) COMMENT '沪股通净买入（亿元）',
    sgt          DECIMAL(20,4) COMMENT '深股通净买入（亿元）',
    north_money  DECIMAL(20,4) COMMENT '北向资金净买入（亿元）',
    south_money  DECIMAL(20,4) COMMENT '南向资金净买入（亿元）',
    created_at   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_trade_date (trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='北向资金流向表';

-- 分析结果历史表
CREATE TABLE IF NOT EXISTS analysis_history (
    id           BIGINT AUTO_INCREMENT PRIMARY KEY,
    code         VARCHAR(20)   NOT NULL,
    name         VARCHAR(50)   DEFAULT NULL,
    analyze_date DATE          NOT NULL,
    score        DECIMAL(5,2)  COMMENT '综合评分（0-100）',
    risk_level   VARCHAR(20)   COMMENT '风险级别',
    suggestion   VARCHAR(50)   COMMENT '操作建议',
    current_price DECIMAL(10,4) COMMENT '分析时价格',
    result_json  MEDIUMTEXT    COMMENT '完整分析结果（JSON）',
    created_at   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_code (code),
    INDEX idx_date (analyze_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='分析结果历史表';

-- 初始化默认持仓（可按需修改）
INSERT IGNORE INTO holdings (code, name, amount, cost_price, stock_type, industry) VALUES
  ('601868.SH', '中国能建', 400, 3.15, 'value',   '基建'),
  ('002506.SZ', '协鑫集成', 400, 2.05, 'growth',  '光伏'),
  ('600821.SH', '金开新能', 600, 4.10, 'concept', '新能源');

SELECT '✅ 数据库初始化完成' AS status;
