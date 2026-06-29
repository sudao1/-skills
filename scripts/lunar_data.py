"""
万年历数据库 — 基于 lunardate 权威库 (经 Microsoft ChineseLunisolarCalendar 验证)
自动从 lunardate 提取 1900-2100 完整农历数据（含闰月、大小月）
每次导入时动态生成，确保数据一致性
"""

import lunardate
from datetime import date, timedelta

def _build_lunar_db():
    """从 lunardate 提取完整农历数据库"""
    db = {}
    for year in range(1900, 2100):
        # 闰月
        leap = 0
        for m in range(1, 13):
            try:
                ld = lunardate.LunarDate(year, m, 1, 1)
                ld.toSolarDate()
                leap = m
                break
            except (ValueError, OverflowError):
                pass

        # 正月初一公历日期
        ld_cny = lunardate.LunarDate(year, 1, 1, 0)
        cny_solar = ld_cny.toSolarDate()

        # 每月天数编码 (1=大月30天, 0=小月29天)
        bits = ''
        for m in range(1, 13):
            md1 = lunardate.LunarDate(year, m, 1, 0).toSolarDate()
            if m < 12:
                md2 = lunardate.LunarDate(year, m + 1, 1, 0).toSolarDate()
                if leap > 0 and m == leap:
                    ml1 = lunardate.LunarDate(year, m, 1, 1).toSolarDate()
                    bits += '1' if (ml1 - md1).days == 30 else '0'
                    md2 = lunardate.LunarDate(year, m + 1, 1, 0).toSolarDate()
                    bits += '1' if (md2 - ml1).days == 30 else '0'
                else:
                    bits += '1' if (md2 - md1).days == 30 else '0'
            else:
                ny = lunardate.LunarDate(year + 1, 1, 1, 0).toSolarDate()
                bits += '1' if (ny - md1).days == 30 else '0'

        db[year] = {
            'cny': cny_solar,
            'leap': leap,
            'bits': bits,
        }
    return db

# 全局缓存
_LUNAR_DB = None

def _get_db():
    global _LUNAR_DB
    if _LUNAR_DB is None:
        _LUNAR_DB = _build_lunar_db()
    return _LUNAR_DB

def get_cny_date(lunar_year):
    """正月初一对应的公历日期"""
    return _get_db()[lunar_year]['cny']

def get_leap_month(lunar_year):
    """闰月月份 (0=无闰月)"""
    return _get_db()[lunar_year]['leap']

def get_month_days(lunar_year, lunar_month):
    """农历月天数 (29或30)"""
    db = _get_db()
    bits = db[lunar_year]['bits']
    leap = db[lunar_year]['leap']
    idx = lunar_month - 1
    if leap > 0 and lunar_month > leap:
        idx += 1
    return 30 if idx < len(bits) and bits[idx] == '1' else 29

def get_leap_month_days(lunar_year):
    """闰月天数 (无闰月返回0)"""
    db = _get_db()
    leap = db[lunar_year]['leap']
    if leap == 0:
        return 0
    bits = db[lunar_year]['bits']
    return 30 if len(bits) > leap and bits[leap] == '1' else 29

def lunar_year_days(lunar_year):
    """农历年总天数"""
    bits = _get_db()[lunar_year]['bits']
    return sum(30 if b == '1' else 29 for b in bits)

def lunar_month_count(lunar_year):
    """农历年月份数 (12或13)"""
    return len(_get_db()[lunar_year]['bits'])

LUNAR_YEARS = []  # 兼容旧接口

# 构建时打印关键年份供验证
def verify_key_years():
    db = _get_db()
    y95 = db[1995]
    cny95 = y95['cny']
    d = cny95
    for m in range(1, 9):
        d += timedelta(days=get_month_days(1995, m))
        if y95['leap'] == m:
            d += timedelta(days=get_leap_month_days(1995))
    d += timedelta(days=19)
    print(f'[lunar_data] 1995 leap={y95["leap"]}, Sep20={d}')
    print(f'[lunar_data] 1995-10-14 lunar={solar_to_lunar_str(date(1995,10,14))}')

def solar_to_lunar_str(solar_date):
    """公历→农历 字符串(供调试)"""
    db = _get_db()
    year = solar_date.year
    cny = db[year]['cny']
    if solar_date < cny:
        year -= 1
        cny = db[year]['cny']
    if year < 2100:
        next_cny = db[year + 1]['cny']
    else:
        next_cny = date(2100, 2, 1)
    if solar_date >= next_cny:
        year += 1
        cny = next_cny

    days = (solar_date - cny).days
    leap = db[year]['leap']
    for m in range(1, 13):
        md = get_month_days(year, m)
        if days < md:
            return f'{year}年{m}月{days+1}日'
        days -= md
        if leap == m:
            ld = get_leap_month_days(year)
            if days < ld:
                return f'{year}年闰{m}月{days+1}日'
            days -= ld
    return 'unknown'

if __name__ == '__main__':
    verify_key_years()
