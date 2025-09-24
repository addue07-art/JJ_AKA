def fib_extension_levels(high, low, close, apply_limit=False, show_short=False, show_close=False):
    rng = high - low
    limit_up = low * 1.10
    limit_down = high * 0.90
    levels = []

    def annotate(label, value, note, style):
        if apply_limit:
            if style == "long" and value > limit_up:
                return None
            if style == "short" and value < limit_down:
                return None
            if style == "close" and (value > limit_up or value < limit_down):
                return None
        if style == "custom":
            note = f'<span style="color:orange">{note}</span>'
        elif style == "short":
            note = f'<span style="color:blue">{note}</span>'
        elif style == "close":
            note = f'<span style="color:green">{note}</span>'
        if not apply_limit:
            if style == "long" and value > limit_up:
                note += ' <span style="color:gray">(超出漲幅限制)</span>'
            if style == "short" and value < limit_down:
                note += ' <span style="color:gray">(超出跌幅限制)</span>'
            if style == "close" and (value > limit_up or value < limit_down):
                note += ' <span style="color:gray">(超出漲跌幅限制)</span>'
        return (label, value, note)

    # 多方延伸
    long_levels = [
        ("高點 − 波幅×0.382", high - rng * 0.382, "黃金分割回檔支撐", "long"),
        ("低點 + 波幅×1.03", low + rng * 1.03, "小幅突破前高，試探新高", "long"),
        ("低點 + 波幅×1.2", low + rng * 1.2, "第一個明顯延伸壓力位", "long"),
        ("低點 + 波幅×1.5", low + rng * 1.5, "關鍵心理整數＋1.5 倍目標壓力", "long"),
        ("自訂延伸（低點 + 波幅×0.06）", low + rng * 0.06, "微支撐區（自訂）", "custom"),
        ("自訂延伸（低點 + 波幅×0.31）", low + rng * 0.31, "短期反彈目標（自訂）", "custom"),
    ]

    # 空方延伸
    short_levels = [
        ("高點 − 波幅×0.03", high - rng * 0.03, "微幅跌破，測試支撐", "short"),
        ("高點 − 波幅×0.2", high - rng * 0.2, "第一個空方延伸支撐", "short"),
        ("高點 − 波幅×0.5", high - rng * 0.5, "中段支撐（空方）", "short"),
        ("高點 − 波幅×0.618", high - rng * 0.618, "強支撐，空方延伸目標", "short"),
        ("高點 − 波幅×0.8", high - rng * 0.8, "空方極限支撐", "short"),
    ]

    # 收盤延伸
    close_levels = [
        ("收盤 + 波幅×0.06", close + rng * 0.06, "短線反彈（收盤起點）", "close"),
        ("收盤 + 波幅×0.31", close + rng * 0.31, "中段反彈（收盤起點）", "close"),
        ("收盤 − 波幅×0.06", close - rng * 0.06, "短線回檔（收盤起點）", "close"),
        ("收盤 − 波幅×0.31", close - rng * 0.31, "中段回檔（收盤起點）", "close"),
    ]

    for item in long_levels:
        result = annotate(*item)
        if result:
            levels.append(result)

    if show_short:
        for item in short_levels:
            result = annotate(*item)
            if result:
                levels.append(result)

    if show_close:
        for item in close_levels:
            result = annotate(*item)
            if result:
                levels.append(result)

    return levels
