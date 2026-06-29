# Fortune Teller — 命理推算 Skill

基于中国传统命理学经典的八字排盘推算工具。输出 FateCat 标准三卷结构命理报告。

## 数据源

- **lunardate** — 农历转换（香港天文台 + Microsoft ChineseLunisolarCalendar 双重验证）
- 八字理论依据：《渊海子平》《三命通会》《滴天髓》《穷通宝鉴》《神峰通考》
- 紫微斗数：《紫微斗数全书》
- 六爻：《周易》纳甲法

## 安装

```bash
pip install lunardate
```

将 `fortune-teller` 文件夹放入 CherryStudio 的 Skills 目录：

- Windows: `%APPDATA%\CherryStudio\Data\Skills\`
- Mac: `~/Library/Application Support/CherryStudio/Data/Skills/`

## 使用

在 CherryStudio 中对 AI 说：

- 「帮我排个八字，1995年11月12日21点，男」
- 「农历1995年9月20日晚9点，看事业」
- 「1988年8月15日14点，女，感情运势」

报告自动输出到桌面。

或命令行使用：

```bash
python scripts/generate_report.py --name 姓名 --solar 1995 11 12 21 --gender 男
python scripts/generate_report.py --name 姓名 --lunar 1995 9 20 21 --gender 男
```

## 功能

- 四柱八字推算（年/月/日/时柱）
- 十神分析 + 十二长生
- 大运起运与十年大运排盘
- 袁天罡称骨
- 五行统计（含地支藏干）
- 1900-2100 万年历完整数据
