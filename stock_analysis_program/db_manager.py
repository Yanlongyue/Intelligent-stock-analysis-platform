#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MySQL 数据库管理模块
负责股票数据、持仓数据、行情数据的持久化存储
"""

import os
import json
import time
import logging
from datetime import datetime, date
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# 尝试导入 pymysql；如果没有安装，提供降级提示
# ─────────────────────────────────────────────
try:
    import pymysql
    import pymysql.cursors
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    logger.warning("⚠️  pymysql 未安装，数据库功能不可用。请执行: pip3 install pymysql")


class DBConfig:
    """从环境变量读取数据库配置"""
    HOST     = os.getenv("MYSQL_HOST",     "127.0.0.1")
    PORT     = int(os.getenv("MYSQL_PORT", "3306"))
    USER     = os.getenv("MYSQL_USER",     "root")
    PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    DATABASE = os.getenv("MYSQL_DATABASE", "stock_analysis")
    CHARSET  = "utf8mb4"


# ─────────────────────────────────────────────
# DDL：数据库建表语句
# ─────────────────────────────────────────────
SCHEMA_SQL = """
-- 持仓表
CREATE TABLE IF NOT EXISTS holdings (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    code         VARCHAR(20)  NOT NULL COMMENT '股票代码，如 601868.SH',
    name         VARCHAR(50)  NOT NULL COMMENT '股票名称',
    amount       INT          NOT NULL DEFAULT 0 COMMENT '持仓数量（股）',
    cost_price   DECIMAL(10,4) NOT NULL DEFAULT 0 COMMENT '成本价',
    stock_type   VARCHAR(20)  NOT NULL DEFAULT 'value' COMMENT 'value/growth/concept',
    industry     VARCHAR(50)  DEFAULT NULL COMMENT '所属行业',
    created_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_code (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='持仓表';

-- 日线行情表
CREATE TABLE IF NOT EXISTS daily_quotes (
    id           BIGINT AUTO_INCREMENT PRIMARY KEY,
    code         VARCHAR(20)  NOT NULL COMMENT '股票代码',
    trade_date   DATE         NOT NULL COMMENT '交易日期',
    open         DECIMAL(10,4) COMMENT '开盘价',
    high         DECIMAL(10,4) COMMENT '最高价',
    low          DECIMAL(10,4) COMMENT '最低价',
    close        DECIMAL(10,4) COMMENT '收盘价',
    pre_close    DECIMAL(10,4) COMMENT '昨收价',
    change_amt   DECIMAL(10,4) COMMENT '涨跌额',
    pct_chg      DECIMAL(10,4) COMMENT '涨跌幅（%）',
    vol          BIGINT        COMMENT '成交量（手）',
    amount       DECIMAL(20,4) COMMENT '成交额（千元）',
    data_source  VARCHAR(20)  DEFAULT 'AkShare' COMMENT '数据来源',
    created_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_code_date (code, trade_date),
    INDEX idx_code (code),
    INDEX idx_trade_date (trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='日线行情表';

-- 每日基本面指标表（PE、PB、换手率等）
CREATE TABLE IF NOT EXISTS daily_basic (
    id           BIGINT AUTO_INCREMENT PRIMARY KEY,
    code         VARCHAR(20)  NOT NULL,
    trade_date   DATE         NOT NULL,
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
    data_source  VARCHAR(20)  DEFAULT 'AkShare',
    created_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_code_date (code, trade_date),
    INDEX idx_code (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='每日基本面指标表';

-- 市场概况快照表（指数行情）
CREATE TABLE IF NOT EXISTS market_overview (
    id           BIGINT AUTO_INCREMENT PRIMARY KEY,
    index_code   VARCHAR(20)  NOT NULL COMMENT '指数代码',
    index_name   VARCHAR(50)  NOT NULL COMMENT '指数名称',
    trade_date   DATE         NOT NULL COMMENT '交易日期',
    close        DECIMAL(12,4) COMMENT '收盘点位',
    pct_chg      DECIMAL(10,4) COMMENT '涨跌幅（%）',
    vol          BIGINT        COMMENT '成交量',
    amount       DECIMAL(20,4) COMMENT '成交额',
    created_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_index_date (index_code, trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='市场概况表';

-- 北向资金流向表
CREATE TABLE IF NOT EXISTS moneyflow_hsgt (
    id           BIGINT AUTO_INCREMENT PRIMARY KEY,
    trade_date   DATE         NOT NULL COMMENT '交易日期',
    ggt_ss       DECIMAL(20,4) COMMENT '港股通（沪）净买入（亿元）',
    ggt_sz       DECIMAL(20,4) COMMENT '港股通（深）净买入（亿元）',
    hgt          DECIMAL(20,4) COMMENT '沪股通净买入（亿元）',
    sgt          DECIMAL(20,4) COMMENT '深股通净买入（亿元）',
    north_money  DECIMAL(20,4) COMMENT '北向资金净买入（亿元）',
    south_money  DECIMAL(20,4) COMMENT '南向资金净买入（亿元）',
    created_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_trade_date (trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='北向资金流向表';

-- 分析结果历史表
CREATE TABLE IF NOT EXISTS analysis_history (
    id           BIGINT AUTO_INCREMENT PRIMARY KEY,
    code         VARCHAR(20)  NOT NULL,
    name         VARCHAR(50)  DEFAULT NULL,
    analyze_date DATE         NOT NULL,
    score        DECIMAL(5,2) COMMENT '综合评分（0-100）',
    risk_level   VARCHAR(20)  COMMENT '风险级别',
    suggestion   VARCHAR(50)  COMMENT '操作建议',
    current_price DECIMAL(10,4) COMMENT '分析时价格',
    result_json  MEDIUMTEXT   COMMENT '完整分析结果（JSON）',
    created_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_code (code),
    INDEX idx_date (analyze_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='分析结果历史表';
"""


class DBManager:
    """MySQL 数据库管理器（单例模式）"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.available = False
        self._conn = None

        if not MYSQL_AVAILABLE:
            logger.warning("DBManager: pymysql 不可用，跳过数据库初始化")
            return

        try:
            self._connect()
            self._init_schema()
            self.available = True
            logger.info("✅ MySQL 数据库连接成功，表结构已初始化")
        except Exception as e:
            logger.error(f"❌ MySQL 数据库初始化失败: {e}")
            self.available = False

    def _connect(self):
        """建立数据库连接，自动创建数据库（如果不存在）"""
        # 先不指定 database，确保库存在
        conn = pymysql.connect(
            host=DBConfig.HOST,
            port=DBConfig.PORT,
            user=DBConfig.USER,
            password=DBConfig.PASSWORD,
            charset=DBConfig.CHARSET,
            autocommit=True,
        )
        with conn.cursor() as cur:
            cur.execute(
                f"CREATE DATABASE IF NOT EXISTS `{DBConfig.DATABASE}` "
                f"DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        conn.close()

        # 再连接到目标数据库
        self._conn = pymysql.connect(
            host=DBConfig.HOST,
            port=DBConfig.PORT,
            user=DBConfig.USER,
            password=DBConfig.PASSWORD,
            database=DBConfig.DATABASE,
            charset=DBConfig.CHARSET,
            autocommit=True,
            cursorclass=pymysql.cursors.DictCursor,
        )

    def _ensure_connection(self):
        """确保连接有效，断线重连"""
        if not self._conn:
            self._connect()
            return
        try:
            self._conn.ping(reconnect=True)
        except Exception:
            try:
                self._connect()
            except Exception as e:
                logger.error(f"MySQL 重连失败: {e}")
                self.available = False

    def _init_schema(self):
        """执行建表语句"""
        self._ensure_connection()
        with self._conn.cursor() as cur:
            for stmt in SCHEMA_SQL.strip().split(";"):
                stmt = stmt.strip()
                if stmt and not stmt.startswith("--"):
                    cur.execute(stmt)

    @contextmanager
    def cursor(self):
        """上下文管理器：获取游标"""
        self._ensure_connection()
        cur = self._conn.cursor()
        try:
            yield cur
        finally:
            cur.close()

    # ─────────────────────────────────────────────
    # 持仓 CRUD
    # ─────────────────────────────────────────────

    def get_holdings(self):
        """获取所有持仓"""
        if not self.available:
            return []
        with self.cursor() as cur:
            cur.execute("SELECT * FROM holdings ORDER BY code")
            rows = cur.fetchall()
        result = []
        for row in rows:
            result.append({
                "code":       row["code"],
                "name":       row["name"],
                "amount":     row["amount"],
                "cost_price": float(row["cost_price"]),
                "type":       row["stock_type"],
                "industry":   row["industry"] or "",
            })
        return result

    def upsert_holding(self, holding: dict):
        """新增或更新持仓（按 code 唯一键）"""
        if not self.available:
            return False
        sql = """
            INSERT INTO holdings (code, name, amount, cost_price, stock_type, industry)
            VALUES (%(code)s, %(name)s, %(amount)s, %(cost_price)s, %(type)s, %(industry)s)
            ON DUPLICATE KEY UPDATE
                name       = VALUES(name),
                amount     = VALUES(amount),
                cost_price = VALUES(cost_price),
                stock_type = VALUES(stock_type),
                industry   = VALUES(industry),
                updated_at = CURRENT_TIMESTAMP
        """
        with self.cursor() as cur:
            cur.execute(sql, holding)
        return True

    def delete_holding(self, code: str):
        """删除持仓"""
        if not self.available:
            return False
        with self.cursor() as cur:
            cur.execute("DELETE FROM holdings WHERE code = %s", (code,))
        return True

    def import_holdings_from_list(self, positions: list):
        """批量导入持仓（用于从 positions.json 迁移）"""
        if not self.available:
            return 0
        count = 0
        for pos in positions:
            try:
                self.upsert_holding({
                    "code":       pos.get("code", ""),
                    "name":       pos.get("name", ""),
                    "amount":     pos.get("amount", 0),
                    "cost_price": pos.get("cost_price", 0),
                    "type":       pos.get("type", "value"),
                    "industry":   pos.get("industry", ""),
                })
                count += 1
            except Exception as e:
                logger.error(f"导入持仓失败 {pos.get('code')}: {e}")
        return count

    # ─────────────────────────────────────────────
    # 日线行情
    # ─────────────────────────────────────────────

    def save_daily_quotes(self, code: str, quotes: list, source: str = "AkShare"):
        """批量保存日线行情，忽略重复记录"""
        if not self.available or not quotes:
            return 0
        sql = """
            INSERT IGNORE INTO daily_quotes
              (code, trade_date, open, high, low, close, pre_close,
               change_amt, pct_chg, vol, amount, data_source)
            VALUES
              (%(code)s, %(trade_date)s, %(open)s, %(high)s, %(low)s,
               %(close)s, %(pre_close)s, %(change_amt)s, %(pct_chg)s,
               %(vol)s, %(amount)s, %(data_source)s)
        """
        rows = []
        for q in quotes:
            rows.append({
                "code":       code,
                "trade_date": q.get("trade_date") or q.get("date"),
                "open":       q.get("open"),
                "high":       q.get("high"),
                "low":        q.get("low"),
                "close":      q.get("close"),
                "pre_close":  q.get("pre_close"),
                "change_amt": q.get("change") or q.get("change_amt"),
                "pct_chg":    q.get("pct_chg") or q.get("pct_change"),
                "vol":        q.get("vol") or q.get("volume"),
                "amount":     q.get("amount"),
                "data_source": source,
            })
        with self.cursor() as cur:
            cur.executemany(sql, rows)
        return len(rows)

    def get_latest_price(self, code: str):
        """从数据库获取最新收盘价"""
        if not self.available:
            return None
        with self.cursor() as cur:
            cur.execute(
                "SELECT close, trade_date FROM daily_quotes "
                "WHERE code = %s ORDER BY trade_date DESC LIMIT 1",
                (code,)
            )
            row = cur.fetchone()
        if row:
            return float(row["close"])
        return None

    def get_price_history(self, code: str, days: int = 30):
        """获取最近 N 天的价格历史"""
        if not self.available:
            return []
        with self.cursor() as cur:
            cur.execute(
                "SELECT trade_date, open, high, low, close, vol, pct_chg "
                "FROM daily_quotes WHERE code = %s "
                "ORDER BY trade_date DESC LIMIT %s",
                (code, days)
            )
            rows = cur.fetchall()
        result = []
        for row in rows:
            result.append({
                "date":     str(row["trade_date"]),
                "open":     float(row["open"]) if row["open"] else None,
                "high":     float(row["high"]) if row["high"] else None,
                "low":      float(row["low"])  if row["low"]  else None,
                "close":    float(row["close"]) if row["close"] else None,
                "volume":   row["vol"],
                "pct_chg":  float(row["pct_chg"]) if row["pct_chg"] else None,
            })
        return list(reversed(result))

    def get_latest_quote_date(self, code: str):
        """获取数据库中该股票最新的行情日期"""
        if not self.available:
            return None
        with self.cursor() as cur:
            cur.execute(
                "SELECT MAX(trade_date) AS max_date FROM daily_quotes WHERE code = %s",
                (code,)
            )
            row = cur.fetchone()
        return row["max_date"] if row else None

    # ─────────────────────────────────────────────
    # 每日基本面
    # ─────────────────────────────────────────────

    def save_daily_basic(self, code: str, data: dict, source: str = "AkShare"):
        """保存每日基本面指标"""
        if not self.available or not data:
            return False
        sql = """
            INSERT INTO daily_basic
              (code, trade_date, pe, pe_ttm, pb, ps, ps_ttm,
               dv_ratio, total_mv, circ_mv, turnover_rate, volume_ratio, data_source)
            VALUES
              (%(code)s, %(trade_date)s, %(pe)s, %(pe_ttm)s, %(pb)s,
               %(ps)s, %(ps_ttm)s, %(dv_ratio)s, %(total_mv)s, %(circ_mv)s,
               %(turnover_rate)s, %(volume_ratio)s, %(data_source)s)
            ON DUPLICATE KEY UPDATE
              pe           = VALUES(pe),
              pe_ttm       = VALUES(pe_ttm),
              pb           = VALUES(pb),
              turnover_rate = VALUES(turnover_rate),
              data_source  = VALUES(data_source)
        """
        with self.cursor() as cur:
            cur.execute(sql, {
                "code":         code,
                "trade_date":   data.get("trade_date") or date.today().isoformat(),
                "pe":           data.get("pe"),
                "pe_ttm":       data.get("pe_ttm"),
                "pb":           data.get("pb"),
                "ps":           data.get("ps"),
                "ps_ttm":       data.get("ps_ttm"),
                "dv_ratio":     data.get("dv_ratio"),
                "total_mv":     data.get("total_mv"),
                "circ_mv":      data.get("circ_mv"),
                "turnover_rate": data.get("turnover_rate"),
                "volume_ratio": data.get("volume_ratio"),
                "data_source":  source,
            })
        return True

    # ─────────────────────────────────────────────
    # 北向资金
    # ─────────────────────────────────────────────

    def save_moneyflow_hsgt(self, records: list):
        """批量保存北向资金流向"""
        if not self.available or not records:
            return 0
        sql = """
            INSERT IGNORE INTO moneyflow_hsgt
              (trade_date, ggt_ss, ggt_sz, hgt, sgt, north_money, south_money)
            VALUES
              (%(trade_date)s, %(ggt_ss)s, %(ggt_sz)s,
               %(hgt)s, %(sgt)s, %(north_money)s, %(south_money)s)
        """
        with self.cursor() as cur:
            cur.executemany(sql, records)
        return len(records)

    def get_moneyflow_hsgt(self, days: int = 10):
        """获取最近 N 天北向资金"""
        if not self.available:
            return []
        with self.cursor() as cur:
            cur.execute(
                "SELECT * FROM moneyflow_hsgt ORDER BY trade_date DESC LIMIT %s",
                (days,)
            )
            rows = cur.fetchall()
        result = []
        for row in rows:
            result.append({
                "trade_date":  str(row["trade_date"]),
                "north_money": float(row["north_money"]) if row["north_money"] else None,
                "hgt":         float(row["hgt"]) if row["hgt"] else None,
                "sgt":         float(row["sgt"]) if row["sgt"] else None,
            })
        return list(reversed(result))

    # ─────────────────────────────────────────────
    # 分析结果历史
    # ─────────────────────────────────────────────

    def save_analysis_result(self, code: str, name: str, result: dict):
        """保存分析结果"""
        if not self.available:
            return False
        sql = """
            INSERT INTO analysis_history
              (code, name, analyze_date, score, risk_level, suggestion, current_price, result_json)
            VALUES
              (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        with self.cursor() as cur:
            cur.execute(sql, (
                code,
                name,
                date.today().isoformat(),
                result.get("comprehensive_score") or result.get("score"),
                result.get("risk_level"),
                result.get("suggestion") or result.get("action"),
                result.get("current_price"),
                json.dumps(result, ensure_ascii=False),
            ))
        return True

    def get_analysis_history(self, code: str, limit: int = 10):
        """获取指定股票的历史分析记录"""
        if not self.available:
            return []
        with self.cursor() as cur:
            cur.execute(
                "SELECT analyze_date, score, risk_level, suggestion, current_price "
                "FROM analysis_history WHERE code = %s "
                "ORDER BY analyze_date DESC, id DESC LIMIT %s",
                (code, limit)
            )
            rows = cur.fetchall()
        result = []
        for row in rows:
            result.append({
                "date":        str(row["analyze_date"]),
                "score":       float(row["score"]) if row["score"] else None,
                "risk_level":  row["risk_level"],
                "suggestion":  row["suggestion"],
                "price":       float(row["current_price"]) if row["current_price"] else None,
            })
        return result

    # ─────────────────────────────────────────────
    # 辅助工具
    # ─────────────────────────────────────────────

    def get_db_stats(self):
        """获取数据库统计信息"""
        if not self.available:
            return {"available": False}
        stats = {"available": True, "tables": {}}
        tables = ["holdings", "daily_quotes", "daily_basic",
                  "market_overview", "moneyflow_hsgt", "analysis_history"]
        with self.cursor() as cur:
            for table in tables:
                cur.execute(f"SELECT COUNT(*) AS cnt FROM `{table}`")
                row = cur.fetchone()
                stats["tables"][table] = row["cnt"] if row else 0
        return stats


# 全局单例
_db: DBManager = None


def get_db() -> DBManager:
    """获取全局 DBManager 单例"""
    global _db
    if _db is None:
        _db = DBManager()
    return _db
