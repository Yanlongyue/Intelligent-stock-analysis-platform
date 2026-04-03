#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Tushare Token是否有效
"""

import tushare as ts

def test_tushare_token():
    """测试Tushare Token"""
    print("🔍 测试Tushare Token有效性...")
    
    # 设置Token
    token = "79e520d18d7db694aeb048f3cc577e5b323687a3434e1cfdd32a75cd"
    ts.set_token(token)
    
    try:
        # 初始化API
        pro = ts.pro_api()
        print("✅ Tushare Pro API初始化成功")
        
        # 测试简单查询
        print("📊 测试数据查询...")
        
        # 测试查询平安银行（000001.SZ）的最新数据
        # 获取今天的日期（格式：YYYYMMDD）
        import datetime
        today = datetime.datetime.now().strftime("%Y%m%d")
        
        print(f"📅 查询日期: {today}")
        print(f"🔗 查询股票: 000001.SZ (平安银行)")
        
        # 查询日线数据
        data = pro.daily(ts_code='000001.SZ', trade_date=today)
        
        if not data.empty:
            print("🎉 Token验证成功！")
            print(f"📈 获取到 {len(data)} 条数据")
            print("📋 数据预览:")
            print(data[['ts_code', 'trade_date', 'open', 'close', 'pct_chg']].head())
            
            # 测试其他接口
            print("\n🔍 测试其他API接口...")
            
            # 获取北向资金流向
            moneyflow = pro.moneyflow_hsgt(trade_date=today)
            if not moneyflow.empty:
                print(f"💰 北向资金数据: {len(moneyflow)} 条")
            
            # 获取指数成分股
            index_weight = pro.index_weight(index_code='000300.SH', trade_date=today)
            if not index_weight.empty:
                print(f"📊 沪深300成分股: {len(index_weight)} 只")
                
            return True
            
        else:
            print("⚠️ Token有效，但今天可能没有交易数据（周末或节假日）")
            print("📝 测试历史数据...")
            
            # 测试历史数据
            historical_data = pro.daily(ts_code='000001.SZ', start_date='20240101', end_date='20240105')
            if not historical_data.empty:
                print("🎉 Token验证成功（历史数据可访问）")
                print(f"📈 获取到 {len(historical_data)} 条历史数据")
                return True
            else:
                print("❌ Token验证失败：无法获取任何数据")
                return False
                
    except Exception as e:
        print(f"❌ Token验证失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Tushare Token 验证测试")
    print("=" * 60)
    
    success = test_tushare_token()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Token验证成功！七步法股票分析程序可以正常运行！")
        print("\n🚀 下一步:")
        print("1. 运行完整分析: python3 src/main.py")
        print("2. 运行测试模式: python3 src/main.py --test")
        print("3. 查看配置摘要: python3 src/main.py --summary")
    else:
        print("❌ Token验证失败！请检查:")
        print("  1. Token是否正确")
        print("  2. 网络连接是否正常")
        print("  3. Tushare Pro账户是否有效")
    print("=" * 60)