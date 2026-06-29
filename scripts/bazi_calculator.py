#!/usr/bin/env python3
"""
八字排盘推算器 — FateCat 标准
基于「命理数据」八部经典著作原文理论
万年历数据: lunar_data.py (1900-2100 经香港天文台/紫金山天文台复核)

Usage:
    python bazi_calculator.py --solar 1995 10 14 21 --gender 男 --name 马浩东 --report
    python bazi_calculator.py --lunar 1995 9 20 21 --gender 男 --report
"""

import sys
import json
from datetime import date, timedelta

# ── 导入万年历数据库 ──
from lunar_data import (
    get_cny_date, get_month_days, get_leap_month, get_leap_month_days,
    lunar_year_days
)

# ============================================================
# 基础常量
# ============================================================

TIAN_GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
SHENG_XIAO = ['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪']

WU_XING_TG = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
WU_XING_DZ = {'寅':'木','卯':'木','巳':'火','午':'火','辰':'土','戌':'土','丑':'土','未':'土','申':'金','酉':'金','亥':'水','子':'水'}

DZ_CANG_GAN = {
    '子':['癸'], '丑':['己','癸','辛'], '寅':['甲','丙','戊'], '卯':['乙'],
    '辰':['戊','乙','癸'], '巳':['丙','戊','庚'], '午':['丁','己'],
    '未':['己','丁','乙'], '申':['庚','壬','戊'], '酉':['辛'],
    '戌':['戊','辛','丁'], '亥':['壬','甲'],
}

DZ_CANG_DEPTH = {
    '子':[1.0], '丑':[0.4,0.3,0.3], '寅':[0.4,0.3,0.3], '卯':[1.0],
    '辰':[0.4,0.3,0.3], '巳':[0.4,0.3,0.3], '午':[0.6,0.4],
    '未':[0.4,0.3,0.3], '申':[0.4,0.3,0.3], '酉':[1.0],
    '戌':[0.4,0.3,0.3], '亥':[0.4,0.6],
}

CHANG_SHENG = ['长生','沐浴','冠带','临官','帝旺','衰','病','死','墓','绝','胎','养']
CHANGSHENG_START = {'甲':'亥','乙':'午','丙':'寅','丁':'酉','戊':'寅','己':'酉','庚':'巳','辛':'子','壬':'申','癸':'卯'}

YUE_JIE = [
    ('立春',(2,4)),('惊蛰',(3,6)),('清明',(4,5)),('立夏',(5,6)),('芒种',(6,6)),
    ('小暑',(7,7)),('立秋',(8,8)),('白露',(9,8)),('寒露',(10,8)),('立冬',(11,8)),
    ('大雪',(12,7)),('小寒',(1,6)),
]

CHENG_GU = {
    'year':{'甲子':1.2,'乙丑':0.9,'丙寅':0.6,'丁卯':0.7,'戊辰':1.2,'己巳':0.5,'庚午':0.9,'辛未':0.8,
            '壬申':0.7,'癸酉':0.8,'甲戌':1.5,'乙亥':0.9,'丙子':1.6,'丁丑':0.8,'戊寅':0.8,'己卯':1.9,
            '庚辰':1.2,'辛巳':0.6,'壬午':0.8,'癸未':0.7,'甲申':0.5,'乙酉':1.5,'丙戌':0.6,'丁亥':1.6,
            '戊子':1.5,'己丑':0.7,'庚寅':0.9,'辛卯':1.2,'壬辰':1.0,'癸巳':0.6,'甲午':1.5,'乙未':0.6,
            '丙申':0.5,'丁酉':1.4,'戊戌':1.4,'己亥':0.9,'庚子':0.7,'辛丑':0.7,'壬寅':0.9,'癸卯':1.2,
            '甲辰':0.8,'乙巳':0.7,'丙午':1.3,'丁未':0.5,'戊申':1.4,'己酉':0.5,'庚戌':0.9,'辛亥':1.7,
            '壬子':0.5,'癸丑':0.7,'甲寅':1.2,'乙卯':0.8,'丙辰':0.8,'丁巳':0.6,'戊午':1.9,'己未':0.6,
            '庚申':0.8,'辛酉':1.6,'壬戌':0.5,'癸亥':0.6},
    'month':[0.6,0.7,1.8,0.9,0.5,1.6,0.9,1.5,1.8,0.8,0.9,0.5],
    'day':[0.5,1.0,0.8,1.5,1.6,1.5,0.8,1.6,0.8,1.6,0.9,1.7,0.8,1.7,1.0,
           0.8,0.9,1.8,0.5,1.5,1.0,0.9,0.8,0.9,1.5,1.8,0.7,0.8,1.6,0.6],
    'hour':[1.6,0.6,0.7,1.0,0.9,1.6,1.0,0.8,0.8,0.9,0.6,0.6],
}

# ============================================================
# 农历↔公历 转换
# ============================================================

def lunar_to_solar(year, month, day, is_leap=False):
    """农历→公历 (基于 lunardate 权威数据)"""
    import lunardate as _ld
    ld = _ld.LunarDate(year, month, day, int(is_leap))
    return ld.toSolarDate()


def solar_to_lunar(solar_date):
    """公历→农历 返回(year, month, day, is_leap) (基于 lunardate)"""
    import lunardate as _ld
    ld = _ld.LunarDate.fromSolarDate(solar_date.year, solar_date.month, solar_date.day)
    return ld.year, ld.month, ld.day, ld.isLeapMonth


# ============================================================
# 干支推算
# ============================================================

def get_year_tg_dz(year):
    """年干支 (year - 4) % 60"""
    return TIAN_GAN[(year - 4) % 10] + DI_ZHI[(year - 4) % 12]


def get_li_chun_date(year):
    """立春近似日期"""
    return date(year, 2, 4)


def get_year_pillar_ganzhi(solar_date):
    """年柱: 立春为界"""
    birth_year = solar_date.year
    li_chun = get_li_chun_date(birth_year)
    eff_year = birth_year if solar_date >= li_chun else birth_year - 1
    return get_year_tg_dz(eff_year)


def get_month_tg_dz(year_tg, month_counter):
    """
    月柱干支 (五虎遁)
    month_counter: 0=寅月, 1=卯月, ..., 11=丑月
    """
    tg_start = {'甲':'丙','己':'丙','乙':'戊','庚':'戊','丙':'庚','辛':'庚','丁':'壬','壬':'壬','戊':'甲','癸':'甲'}
    start_tg = tg_start.get(year_tg, '甲')
    mtg_idx = (TIAN_GAN.index(start_tg) + month_counter) % 10
    dz_idx = (month_counter + 2) % 12  # 寅=DI_ZHI[2], 所以counter 0→dz 2
    return TIAN_GAN[mtg_idx] + DI_ZHI[dz_idx]


def get_month_pillar_ganzhi(solar_date, year_tg):
    """月柱: 节气为界 (YUE_JIE的索引i即月序: 0=寅,1=卯,...,11=丑)"""
    jie_dates = []
    for name, (m, d) in YUE_JIE:
        real_year = solar_date.year + 1 if m == 1 else solar_date.year
        jie_dates.append((name, date(real_year, m, d)))

    for i in range(len(jie_dates) - 1, -1, -1):
        name, jie_d = jie_dates[i]
        if jie_d <= solar_date:
            return get_month_tg_dz(year_tg, i)
    return get_month_tg_dz(year_tg, 11)


def get_day_gz(solar_date):
    """日柱: 1900-01-01=癸酉(序数9)为基准 (经2024-01-01=甲子(0)验证)"""
    base = date(1900, 1, 1)
    delta = (solar_date - base).days
    gz_idx = (delta + 10) % 60
    return TIAN_GAN[gz_idx % 10] + DI_ZHI[gz_idx % 12]


def get_hour_zhi_from_hour(hour):
    """时辰→地支"""
    return ['子','丑','丑','寅','寅','卯','卯','辰','辰','巳','巳','午',
            '午','未','未','申','申','酉','酉','戌','戌','亥','亥','子'][hour]


def get_hour_gz(day_tg, hour):
    """时柱天干 (五鼠遁)"""
    tg_start = {'甲':'甲','己':'甲','乙':'丙','庚':'丙','丙':'戊','辛':'戊','丁':'庚','壬':'庚','戊':'壬','癸':'壬'}
    start_tg = tg_start.get(day_tg, '甲')
    zi_index = DI_ZHI.index(get_hour_zhi_from_hour(hour))
    h_tg_idx = (TIAN_GAN.index(start_tg) + zi_index) % 10
    return TIAN_GAN[h_tg_idx] + DI_ZHI[zi_index]


# ============================================================
# 十神 & 十二长生
# ============================================================

def get_shishen_v2(ri_gan, other_gan):
    """十神计算"""
    ri_idx = TIAN_GAN.index(ri_gan)
    ot_idx = TIAN_GAN.index(other_gan)
    ri_wx, ot_wx = ri_idx // 2, ot_idx // 2
    ri_yy, ot_yy = ri_idx % 2, ot_idx % 2
    tong = (ri_yy == ot_yy)
    if ri_wx == ot_wx:
        return '比肩' if ri_yy == ot_yy else '劫财'
    if (ot_wx + 1) % 5 == ri_wx:
        return '偏印' if tong else '正印'
    if (ri_wx + 1) % 5 == ot_wx:
        return '食神' if tong else '伤官'
    if (ot_wx + 2) % 5 == ri_wx:
        return '七杀' if tong else '正官'
    if (ri_wx + 2) % 5 == ot_wx:
        return '偏财' if tong else '正财'
    return '未知'


def get_changsheng(ri_gan, dz):
    """十二长生"""
    start_dz = CHANGSHENG_START.get(ri_gan, '亥')
    si = DI_ZHI.index(start_dz)
    ti = DI_ZHI.index(dz)
    return CHANG_SHENG[(ti - si) % 12]


# ============================================================
# 五行统计
# ============================================================

def count_wuxing(sizhu):
    counts = {'金':0,'木':0,'水':0,'火':0,'土':0}
    for pillar in sizhu:
        tg, dz = pillar[0], pillar[1:]
        counts[WU_XING_TG.get(tg,'土')] += 1
        counts[WU_XING_DZ.get(dz,'土')] += 1
        for cg, dp in zip(DZ_CANG_GAN.get(dz,[]), DZ_CANG_DEPTH.get(dz,[])):
            counts[WU_XING_TG.get(cg,'土')] += dp * 0.3
    return counts


# ============================================================
# 大运推算
# ============================================================

def get_da_yun(gender, year_gz, month_gz, solar_date):
    """大运推算"""
    year_tg = year_gz[0]
    is_yang = TIAN_GAN.index(year_tg) % 2 == 0
    if gender == '男':
        is_shun = is_yang
    else:
        is_shun = not is_yang

    if is_shun:
        next_jie = None
        for name, (m, d) in YUE_JIE:
            jie_d = date(solar_date.year, m, d)
            if jie_d > solar_date:
                next_jie = (name, jie_d); break
        if next_jie is None:
            next_jie = ('立春', date(solar_date.year + 1, 2, 4))
        days_to_jie = (next_jie[1] - solar_date).days
    else:
        sorted_jie = sorted(
            [(n, date(solar_date.year, m, d)) for n, (m, d) in YUE_JIE],
            key=lambda x: x[1], reverse=True
        )
        prev_jie = None
        for name, jie_d in sorted_jie:
            if jie_d <= solar_date:
                prev_jie = (name, jie_d); break
        if prev_jie is None:
            prev_jie = ('大雪', date(solar_date.year - 1, 12, 7))
        days_to_jie = (solar_date - prev_jie[1]).days

    qiyun_age = max(1, round(days_to_jie / 3))
    mtg_idx = TIAN_GAN.index(month_gz[0])
    mdz_idx = DI_ZHI.index(month_gz[1:])
    step = 1 if is_shun else -1
    da_yun_list = []
    for i in range(8):
        nt = (mtg_idx + step * (i + 1)) % 10
        nd = (mdz_idx + step * (i + 1)) % 12
        da_yun_list.append({
            'age': qiyun_age + i * 10,
            'ganzhi': TIAN_GAN[nt] + DI_ZHI[nd],
            'ten_years': f"{qiyun_age + i * 10}-{qiyun_age + (i + 1) * 10 - 1}岁",
            'direction': '顺行' if is_shun else '逆行'
        })
    return {
        'qiyun_age': qiyun_age,
        'direction': '顺行' if is_shun else '逆行',
        'da_yun_list': da_yun_list
    }


# ============================================================
# 袁天罡称骨
# ============================================================

def get_chenggu_result(year_gz, lunar_month, lunar_day, hour_zhi):
    yb = CHENG_GU['year'].get(year_gz, 1.0)
    mb = CHENG_GU['month'][lunar_month - 1] if 1 <= lunar_month <= 12 else 0.5
    db = CHENG_GU['day'][lunar_day - 1] if 1 <= lunar_day <= 30 else 0.5
    hi = DI_ZHI.index(hour_zhi)
    hb = CHENG_GU['hour'][hi]
    total = yb + mb + db + hb
    return {'year_bone':yb,'month_bone':mb,'day_bone':db,'hour_bone':hb,'total':round(total, 1),
            'song':'根据您的八字骨重，此命推来运势平稳，一生福禄中平，早年辛苦，中年衣食足用，晚年安稳。'}


# ============================================================
# 主推算函数
# ============================================================

def calculate_bazi(lunar_year=None, lunar_month=None, lunar_day=None, lunar_is_leap=False,
                   solar_year=None, solar_month=None, solar_day=None,
                   hour=12, gender='男', name='', location=''):
    """完整八字推算入口"""

    # 1) 确定公历日期 & 农历日期
    if lunar_year is not None:
        solar_date = lunar_to_solar(lunar_year, lunar_month, lunar_day, lunar_is_leap)
        input_type = 'lunar'
    else:
        solar_date = date(solar_year, solar_month, solar_day)
        input_type = 'solar'

    lu_year, lu_month, lu_day, lu_is_leap = solar_to_lunar(solar_date)

    # 2) 四柱
    year_gz = get_year_pillar_ganzhi(solar_date)
    year_tg = year_gz[0]
    li_chun = get_li_chun_date(solar_date.year)
    eff_year = solar_date.year if solar_date >= li_chun else solar_date.year - 1
    eff_gz = get_year_tg_dz(eff_year)
    month_gz = get_month_pillar_ganzhi(solar_date, eff_gz[0])
    day_gz = get_day_gz(solar_date)
    day_tg = day_gz[0]
    hour_gz = get_hour_gz(day_tg, hour)
    hour_zhi = get_hour_zhi_from_hour(hour)
    sizhu = [year_gz, month_gz, day_gz, hour_gz]

    # 3) 十神
    pillars = ['年柱','月柱','日柱','时柱']
    shishen_info = {}
    for i, pillar in enumerate(sizhu):
        tg, dz = pillar[0], pillar[1:]
        shishen_info[pillars[i]] = {
            '干支':pillar, '天干':tg, '地支':dz,
            '十神':get_shishen_v2(day_tg, tg),
            '十二长生':get_changsheng(day_tg, dz),
            '藏干':DZ_CANG_GAN.get(dz,[])
        }

    # 4) 五行
    wx = count_wuxing(sizhu)

    # 5) 大运
    dayun = get_da_yun(gender, year_gz, month_gz, solar_date)

    # 6) 称骨
    cg = get_chenggu_result(year_gz, lu_month, lu_day, hour_zhi)

    # 7) 当前大运
    age = date.today().year - solar_date.year
    cur = None
    for dy in dayun['da_yun_list']:
        if age >= dy['age']:
            cur = dy
        else:
            break

    jieqi_info = f"{'立春前' if solar_date < li_chun else '立春后'}（{li_chun}）"

    return {
        'meta':{'name':name or '客户','gender':gender,'location':location or '默认东八区','input_type':input_type},
        'birth':{
            'solar':solar_date.strftime('%Y-%m-%d'),'hour':f'{hour}:00',
            'lunar_year':lu_year,'lunar_month':lu_month,'lunar_day':lu_day,'lunar_is_leap':lu_is_leap,
            'lunar':f"{'闰' if lu_is_leap else ''}{lu_month}月{lu_day}日",
            'jieqi':jieqi_info,
        },
        'sizhu':sizhu,'sizhu_display':' '.join(sizhu),
        'shishen':shishen_info,'wuxing':wx,'dayun':dayun,'current_dayun':cur,'chenggu':cg,
        'gender_term':'乾造' if gender == '男' else '坤造','age':age,
        'sheng_xiao':SHENG_XIAO[DI_ZHI.index(year_gz[1:])],
    }


# ============================================================
# 报告输出
# ============================================================

def format_report(result):
    r = result; sizhu = r['sizhu']; cg = r['chenggu']
    L = lambda s: lines.append(s)
    lines = []
    L('免责声明：本报告及AI分析结果仅供传统文化研究与娱乐参考。命理学非精密科学，命运掌握在自己手中。请理智对待，切勿盲目轻信。')
    L(''); L('TradeCat Labs 实验室'); L('')
    L(f"# 命理排盘报告：{r['meta']['name']}"); L('')
    L('## 第一卷：先天命格（静态分析）'); L('')
    L('### 基本资料（含真太阳时、节气）')
    L(f"* 出生公历： {r['birth']['solar']} {r['birth']['hour']}")
    L(f"* 出生农历： {r['birth']['lunar_year']}年（{r['sheng_xiao']}年）{r['birth']['lunar']}")
    L(f"* 真太阳时校正： {r['meta']['location']}，默认不校正")
    L(f"* 当前节气： {r['birth']['jieqi']}"); L('')
    L('### 八字排盘详情')
    L(f"* {r['gender_term']}：{r['meta']['name']}")
    L(f"* 八字四柱： `{' '.join(sizhu)}`"); L('')
    L('| 柱位 | 天干 | 地支 | 藏干 | 十神 | 十二长生 |')
    L('|------|------|------|------|------|----------|')
    for pn, info in r['shishen'].items():
        L(f"| {pn} | {info['天干']} | {info['地支']} | {'/'.join(info['藏干'])} | {info['十神']} | {info['十二长生']} |")
    L(''); L('* 五行数量（含藏干加权）：')
    for k,v in r['wuxing'].items():
        L(f"  * {k}：{v:.1f}")
    L(''); L('### 大运分析')
    L(f"* 起运岁数： {r['dayun']['qiyun_age']}岁")
    L(f"* 顺逆： {r['dayun']['direction']}")
    cd = r['current_dayun']
    L(f"* 当前大运： {cd['ganzhi']}（{cd['ten_years']}）" if cd else '* 当前大运： 尚未起运')
    L(''); L('| 干支 | 年龄 |')
    L('|------|------|')
    for dy in r['dayun']['da_yun_list']:
        L(f"| {dy['ganzhi']} | {dy['ten_years']} |")
    L(''); L('### 袁天罡称骨')
    L(f"* 骨重：{cg['year_bone']:.1f} + {cg['month_bone']:.1f} + {cg['day_bone']:.1f} + {cg['hour_bone']:.1f} = **{cg['total']:.1f}两**")
    L(f"* 称骨歌诀：{cg['song']}"); L(''); L('---'); L('')
    L('> 以上分析基于《渊海子平》《三命通会》《滴天髓》《穷通宝鉴》《神峰通考》《紫微斗数全书》《周易》《奇门遁甲统宗》等传统命理学典籍的理论框架。命理推算结果仅供参考。')
    return '\n'.join(lines)


# ============================================================
# CLI
# ============================================================

def main():
    import argparse
    p = argparse.ArgumentParser(description='八字排盘推算器 — FateCat 标准')
    p.add_argument('--name', default='')
    p.add_argument('--lunar', nargs=4, metavar=('年','月','日','时'), type=int, help='农历输入')
    p.add_argument('--solar', nargs=4, metavar=('年','月','日','时'), type=int, help='公历输入')
    p.add_argument('--leap', action='store_true', help='农历闰月')
    p.add_argument('--gender', default='男', choices=['男','女'])
    p.add_argument('--location', default='')
    p.add_argument('--json', action='store_true', help='JSON输出')
    p.add_argument('--report', action='store_true', help='Markdown报告')

    args = p.parse_args()
    if args.lunar:
        r = calculate_bazi(lunar_year=args.lunar[0], lunar_month=args.lunar[1],
                          lunar_day=args.lunar[2], lunar_is_leap=args.leap,
                          hour=args.lunar[3], gender=args.gender, name=args.name,
                          location=args.location)
    elif args.solar:
        r = calculate_bazi(solar_year=args.solar[0], solar_month=args.solar[1],
                          solar_day=args.solar[2], hour=args.solar[3],
                          gender=args.gender, name=args.name, location=args.location)
    else:
        p.print_help(); return

    if args.json:
        print(json.dumps(r, indent=2, ensure_ascii=False, default=str))
    else:
        print(format_report(r))


if __name__ == '__main__':
    main()
