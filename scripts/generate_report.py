#!/usr/bin/env python3
"""
FateCat 标准命理排盘报告生成器
Usage:
    python generate_report.py --name 马浩东 --lunar 1995 9 20 21 --gender 男 --out ~/Desktop/报告.txt
    python generate_report.py --name 张三 --solar 1990 5 20 8 --gender 女 --leap
"""
import sys, os, argparse
sys.path.insert(0, os.path.dirname(__file__))
from bazi_calculator import calculate_bazi

def generate(name, lunar, solar, hour, gender, leap, location):
    """生成完整 FateCat 格式报告"""
    kwargs = dict(hour=hour, gender=gender, name=name, location=location or '')
    if lunar:
        kwargs.update(lunar_year=lunar[0], lunar_month=lunar[1], lunar_day=lunar[2], lunar_is_leap=leap)
    else:
        kwargs.update(solar_year=solar[0], solar_month=solar[1], solar_day=solar[2])

    r = calculate_bazi(**kwargs)
    sizhu = r['sizhu']
    cg = r['chenggu']
    day_tg = sizhu[2][0]

    L = lambda s: lines.append(s)
    lines = []

    L('免责声明：本报告及AI分析结果仅供传统文化研究与娱乐参考。命理学非精密科学，命运掌握在自己手中。请理智对待，切勿盲目轻信。')
    L('')
    L('TradeCat Labs 实验室')
    L('')
    L(f'# 命理排盘报告：{name}')
    L('')
    L('*数据源: lunardate (香港天文台 + Microsoft ChineseLunisolarCalendar)*')
    L('')
    L('## 第一卷：先天命格（静态分析）')
    L('')
    L('### 基本资料（含真太阳时、节气）')
    L(f'* 出生公历： {r["birth"]["solar"]} {r["birth"]["hour"]}')
    L(f'* 出生农历： {r["birth"]["lunar_year"]}年（{r["sheng_xiao"]}年）{r["birth"]["lunar"]}')
    L(f'* 真太阳时校正： {r["meta"]["location"]}，默认不校正')
    L(f'* 当前节气： {r["birth"]["jieqi"]}')
    L('')
    L('### 八字排盘详情')
    L(f'* {r["gender_term"]}：{name}')
    L(f'* 八字四柱： {" ".join(sizhu)}')
    L('')
    L('| 柱位 | 天干 | 地支 | 藏干 | 十神 | 十二长生 |')
    L('|------|------|------|------|------|----------|')
    for pn, info in r['shishen'].items():
        cang = '/'.join(info['藏干'])
        L(f'| {pn} | {info["天干"]} | {info["地支"]} | {cang} | {info["十神"]} | {info["十二长生"]} |')
    L('')
    L('* 五行数量（含藏干加权）：')
    for k, v in r['wuxing'].items():
        L(f'  * {k}：{v:.1f}')
    L('')

    # 日主自动分析
    wx_map = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
    day_wx = wx_map[day_tg]

    L('### 日主概览')
    L(f'日主**{day_tg}**（{day_wx}），生于{r["birth"]["lunar"]}。')
    L(f'详细分析请结合《滴天髓·天干论》中对{day_tg}的原文描述及《穷通宝鉴》各月取用法则进行。')
    L('')

    L('### 大运分析')
    L(f'* 起运岁数： {r["dayun"]["qiyun_age"]}岁')
    L(f'* 顺逆： {r["dayun"]["direction"]}')
    cd = r['current_dayun']
    if cd:
        L(f'* 当前大运： {cd["ganzhi"]}（{cd["ten_years"]}）')
    else:
        L('* 当前大运： 尚未起运')
    L('')
    L('| 干支 | 年龄 |')
    L('|------|------|')
    for dy in r['dayun']['da_yun_list']:
        L(f'| {dy["ganzhi"]} | {dy["ten_years"]} |')
    L('')

    L('### 袁天罡称骨')
    L(f'* 年骨：{cg["year_bone"]:.1f}两 × 月骨：{cg["month_bone"]:.1f}两 × 日骨：{cg["day_bone"]:.1f}两 × 时骨：{cg["hour_bone"]:.1f}两')
    L(f'* **总骨重：{cg["total"]:.1f}两**')
    L(f'* {cg["song"]}')
    L('')

    L('---')
    L('')
    L('> 以上分析基于《渊海子平》《三命通会》《滴天髓》《穷通宝鉴》《神峰通考》等传统命理学典籍的理论框架，属于传统文化研究探讨范畴。')
    L('> 命理推算结果仅供参考，不应作为人生决策的唯一依据。每个人的命运由自身选择、努力和环境共同塑造。')
    L('> 农历数据源: lunardate 权威库（香港天文台双重验证）')
    L('')

    return '\n'.join(lines)


def main():
    p = argparse.ArgumentParser(description='FateCat 命理排盘报告生成器')
    p.add_argument('--name', default='客户', help='姓名')
    p.add_argument('--lunar', nargs=4, type=int, metavar=('年','月','日','时'), help='农历输入')
    p.add_argument('--solar', nargs=4, type=int, metavar=('年','月','日','时'), help='公历输入')
    p.add_argument('--gender', default='男', choices=['男','女'])
    p.add_argument('--leap', action='store_true', help='农历闰月')
    p.add_argument('--location', default='', help='出生地点')
    p.add_argument('--out', default=None, help='输出文件路径（默认桌面）')

    args = p.parse_args()

    if not args.lunar and not args.solar:
        p.print_help()
        return

    if args.lunar:
        hour = args.lunar[3]
        lunar = (args.lunar[0], args.lunar[1], args.lunar[2])
        solar = None
    else:
        hour = args.solar[3]
        solar = (args.solar[0], args.solar[1], args.solar[2])
        lunar = None

    report = generate(args.name, lunar, solar, hour, args.gender, args.leap, args.location)

    if args.out:
        out_path = args.out
    else:
        desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
        safe_name = args.name if args.name != '客户' else 'report'
        out_path = os.path.join(desktop, f'{safe_name}_命理排盘报告.txt')

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f'报告已保存: {out_path}')


if __name__ == '__main__':
    main()
