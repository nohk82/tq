import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

# =========================================================
# ⚙️ USER SETTINGS (Default)
# =========================================================
SYMBOL = 'TQQQ'
INITIAL_CAPITAL = 1000  # Changed to 1000 for better decimal visibility
# START_DATE = '2012-02-11' # Removed as it's now a parameter

# ★ 황금 파라미터 (CAGR 46% / MDD -31%)
DEFAULT_PARAMS = {'ma_period': 192, 'd_period': 3, 'w_period': 23, 'w_buy_max': 63, 'd_buy_cross': 28, 'w_sell_cross': 68, 'w_profit_max': 83, 'stop_loss': 0.18, 'start_date': '2010-02-01'}

def get_data(symbol, start_date):
    try:
        df = yf.download(symbol, start=start_date, progress=False, auto_adjust=True)
        if df.empty: return pd.DataFrame()

        if isinstance(df.columns, pd.MultiIndex):
            try:
                df = df.xs(symbol, axis=1, level=1)
            except:
                pass

        col = 'Adj Close' if 'Adj Close' in df.columns else 'Close'
        df = df[[col]].rename(columns={col: 'Close'})
        df.index = df.index.tz_localize(None)
        return df.sort_index()
    except Exception as e:
        print(f"Data download error: {e}")
        return pd.DataFrame()

def calculate_indicators(df, p):
    df = df.copy()
    df['MA'] = df['Close'].rolling(p['ma_period']).mean()

    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(p['d_period']).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(p['d_period']).mean()
    rs = gain / loss
    df['RSI_D'] = 100 - (100 / (1 + rs))

    df_w = df.resample('W-FRI').last()
    d_w = df_w['Close'].diff()
    g_w = (d_w.where(d_w > 0, 0)).rolling(p['w_period']).mean()
    l_w = (-d_w.where(d_w < 0, 0)).rolling(p['w_period']).mean()
    rs_w = g_w / l_w
    df_w['RSI_W'] = 100 - (100 / (1 + rs_w))

    df['RSI_W'] = df_w['RSI_W'].reindex(df.index).ffill()
    return df.dropna()

def get_strategy_data(symbol=SYMBOL, params=None):
    if params is None:
        params = DEFAULT_PARAMS

    start_date = params.get('start_date', '2020-01-01')
    df_raw = get_data(symbol, start_date)
    if df_raw.empty:
        return {"error": "Failed to download data"}

    df = calculate_indicators(df_raw, params)

    # Backtest
    start_date = params.get('start_date', '2020-01-01')
    df_bt = df[df.index >= pd.to_datetime(start_date)].copy()
    prices = df_bt['Close'].values
    ma_vals = df_bt['MA'].values
    rsi_d = df_bt['RSI_D'].values
    rsi_w = df_bt['RSI_W'].values
    dates = df_bt.index

    balance = INITIAL_CAPITAL
    shares = 0
    in_pos = False
    equity_curve = []
    trades = []
    last_buy_price = 0
    last_buy_date = None
    win_count = 0

    for i in range(len(prices)):
        price = prices[i]
        ma = ma_vals[i]
        curr_date = dates[i]
        
        # 1. Calculate Balance (Before trades today)
        if not in_pos:
            curr_eq = balance
        else:
            curr_eq = shares * price

        if i == 0:
            equity_curve.append({
                "date": curr_date.strftime("%Y-%m-%d"),
                "equity": round(curr_eq, 2),
                "price": round(price, 2),
                "ma": round(ma, 2),
                "rsi_w": 0,
                "rsi_d": 0,
                "s": 0
            })
            continue

        prev_rd, curr_rd = rsi_d[i - 1], rsi_d[i]
        prev_rw, curr_rw = rsi_w[i - 1], rsi_w[i]
        is_uptrend = price > ma
        
        # 2. Check Signals
        daily_status = 1 if is_uptrend else 0  # Default: Wait/Bull or Bear
        if in_pos: daily_status = 3 # Hold

        # Buy Signal
        if not in_pos:
            if is_uptrend:
                if (curr_rw < params['w_buy_max']) and (prev_rd < params['d_buy_cross']) and (
                        curr_rd >= params['d_buy_cross']):
                    in_pos = True
                    daily_status = 2 # Buy
                    shares = balance / price
                    balance = 0
                    last_buy_price = price
                    last_buy_date = curr_date
                    trades.append({
                        'date': curr_date.strftime("%Y-%m-%d"),
                        'type': 'Buy',
                        'price': round(price, 2),
                        'size': round(shares, 4)
                    })
        # Sell Signal
        else:
            cond_ma = not is_uptrend
            ref_price = last_buy_price if last_buy_price > 0 else price
            cond_stop = ((price - ref_price) / ref_price) < -params['stop_loss']
            cond_trend = (prev_rw > params['w_sell_cross']) and (curr_rw <= params['w_sell_cross'])
            cond_profit = (curr_rw >= params['w_profit_max'])

            if cond_ma or cond_stop or cond_trend or cond_profit:
                daily_status = 6 # Trend Break
                if cond_profit: daily_status = 4
                elif cond_stop: daily_status = 5
                elif cond_ma: daily_status = 6 # MA Break
                elif cond_ma: daily_status = 6 # MA Break
                
                # Win Check
                if price > last_buy_price:
                    win_count += 1
                
                # Calculate holding period and profit
                holding_days = (curr_date - last_buy_date).days if last_buy_date else 0
                profit_pct = ((price - last_buy_price) / last_buy_price * 100) if last_buy_price > 0 else 0
                
                balance = shares * price
                shares = 0
                in_pos = False
                reason = 'MA Break' if cond_ma else (
                    'Stop Loss' if cond_stop else ('Profit Max' if cond_profit else 'Trend Broken'))
                trades.append({
                    'date': curr_date.strftime("%Y-%m-%d"),
                    'type': 'Sell',
                    'price': round(price, 2),
                    'reason': reason,
                    'balance': round(balance, 2),
                    'holding_days': holding_days,
                    'profit_pct': round(profit_pct, 2)
                })

        # 3. Append to Curve (End of Day State)
        # Note: If we bought today, eq is calculated at close price
        if in_pos and shares > 0:
            curr_eq = shares * price
        elif not in_pos:
            curr_eq = balance

        equity_curve.append({
            "date": curr_date.strftime("%Y-%m-%d"),
            "equity": round(curr_eq, 2),
            "price": round(price, 2),
            "ma": round(ma, 2),
            "rsi_w": round(curr_rw, 2),
            "rsi_d": round(curr_rd, 2),
            "s": daily_status
        })


    final_val = equity_curve[-1]['equity']
    total_days = (dates[-1] - dates[0]).days
    years = total_days / 365.25
    cagr = (final_val / INITIAL_CAPITAL) ** (1 / years) - 1 if years > 0 else 0
    
    # Calculate MDD
    eq_series = pd.Series([e['equity'] for e in equity_curve])
    running_max = eq_series.cummax()
    drawdown = (eq_series - running_max) / running_max
    mdd = drawdown.min()

    # Live Diagnosis
    last_idx = df.index[-1]
    prev_idx = df.index[-2]
    today_row = df.loc[last_idx]
    prev_row = df.loc[prev_idx]

    curr_p = today_row['Close']
    curr_ma = today_row['MA']
    cur_rd = today_row['RSI_D']
    pre_rd = prev_row['RSI_D']
    cur_rw = today_row['RSI_W']
    is_bull = curr_p > curr_ma

    cond_buy = (cur_rw < params['w_buy_max']) and (pre_rd < params['d_buy_cross']) and (cur_rd >= params['d_buy_cross'])
    
    status_label = "관망"
    status_color = "gray"
    action_msg = "특이사항 없음"

    if not is_bull:
        status_label = "하락장/관망"
        status_color = "red"
        action_msg = "시장 하락세(201일선 이탈). 현금 100% 보유 추천."
    elif cond_buy:
        status_label = "강력 매수"
        status_color = "green"
        action_msg = "상승장 속 눌림목 반등 포착! 진입하세요."
    elif in_pos: # Note: This is an estimation since we don't track live position state perfectly without a db, but we can infer from the last simulated trade
        status_label = "보유 지속"
        status_color = "blue"
        action_msg = "상승 추세 유지 중. 계속 보유하세요."

    # Force check for sell signals on 'today' even if we don't have shares in sim
    # (Just signal check)
    pre_rw = prev_row['RSI_W']
    cond_trend_break = (pre_rw > params['w_sell_cross']) and (cur_rw <= params['w_sell_cross'])
    cond_profit_max = cur_rw >= params['w_profit_max']
    
    if cond_trend_break:
        status_label = "매도 신호 (추세 꺾임)"
        status_color = "orange"
        action_msg = "주봉 추세 꺾임. 리스크 관리 필요."
    elif cond_profit_max:
        status_label = "익절 신호 (과열)"
        status_color = "gold"
        action_msg = "과열권 도달. 수익 실현 추천."


    # Calculate win stats
    total_trades = len([t for t in trades if t['type'] == 'Sell'])
    win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0

    # Benchmarks (Buy & Hold)
    bnh_start = 0
    bnh_first_buy = 0
    
    if len(prices) > 0:
        # 1. B&H from Start Date
        start_price = prices[0]
        final_price = prices[-1]
        
        if start_price > 0:
            bnh_start = (INITIAL_CAPITAL / start_price) * final_price
        
        # 2. B&H from First Buy Date strategy entered
        # Find first buy trade
        first_buy_price = 0
        for t in trades:
            if t['type'] == 'Buy':
                first_buy_price = t['price']
                break
        
        if first_buy_price > 0:
            bnh_first_buy = (INITIAL_CAPITAL / first_buy_price) * final_price

    return {
        "symbol": symbol,
        "start_date": dates[0].strftime("%Y-%m-%d"),
        "last_date": last_idx.strftime("%Y-%m-%d"),
        "final_balance": round(final_val, 0),
        "bnh_start": round(bnh_start if bnh_start == bnh_start else 0, 0),       # New: Handle NaN
        "bnh_first_buy": round(bnh_first_buy if bnh_first_buy == bnh_first_buy else 0, 0), # New: Handle NaN
        "initial_capital": INITIAL_CAPITAL,
        "cagr": round(cagr * 100, 2),
        "mdd": round(mdd * 100, 2),
        "total_trades": total_trades,
        "win_count": win_count,
        "win_rate": round(win_rate, 1),
        "diagnosis": {
            "price": round(curr_p, 2),
            "ma": round(curr_ma, 2),
            "rsi_w": round(cur_rw, 1),
            "rsi_d": round(cur_rd, 1),
            "status": status_label,
            "status_color": status_color,
            "message": action_msg,
            # Boolean Flags for Icons
            "is_bull": bool(is_bull),
            "is_rsi_w_safe": bool(cur_rw < params['w_buy_max']),
            "is_rsi_d_cross": bool((pre_rd < params['d_buy_cross']) and (cur_rd >= params['d_buy_cross'])),
            "cond_buy": bool(cond_buy),
            "cond_trend_break": bool(cond_trend_break),
            "cond_profit_max": bool(cond_profit_max)
        },
        "trades": trades[::-1], # Newest first
        "equity_curve": equity_curve
    }

