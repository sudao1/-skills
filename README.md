# 🔮 Fortune Teller — 命理推算

[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://python.org)
[![CherryStudio](https://img.shields.io/badge/CherryStudio-Skill-orange)](https://cherry-ai.com)

基于中国传统命理学经典著作的专业八字排盘推算工具。支持公历/农历输入，输出 FateCat 标准三卷结构命理报告。**所有推算结论依据经典原文，不编造理论。**

---

## ✨ 功能特性

- **四柱八字** — 年柱（立春为界）、月柱（节气为界）、日柱（万年历公式）、时柱（五鼠遁）
- **十神分析** — 比劫/食伤/财/官杀/印 + 十二长生状态
- **地支藏干** — 含深浅比例加权
- **大运推算** — 阳男阴女顺行/阴男阳女逆行，精准起运年龄
- **袁天罡称骨** — 年月日时骨重加总 + 传统歌诀
- **五行统计** — 天干 + 地支 + 藏干加权
- **闰月处理** — lunardate 权威库，正确识别闰月
- **FateCat 三卷报告** — 先天命格 → 后天运路 → 民俗建议

## 📚 理论依据

所有推算方法严格依据以下八部经典著作原文：

| 经典 | 朝代/作者 | 用途 |
|------|----------|------|
| 《渊海子平》 | 宋·徐大升 | 子平八字奠基，十神体系 |
| 《三命通会》 | 明·万民英 | 十二卷总汇 |
| 《滴天髓》 | 明·刘基 | 天干论/格局论/体用论/寒暖论 |
| 《穷通宝鉴》 | 清 | 调候用神，十干各月取用 |
| 《神峰通考》 | 明·张楠 | 动静说/病药说/杂气财官论 |
| 《紫微斗数全书》 | — | 紫微斗数体系 |
| 《周易》 | — | 纳甲六爻装卦 |
| 《奇门遁甲统宗》 | — | 奇门遁甲体系 |

## 📊 数据精度

- **农历 → 公历**：`lunardate` 权威库（香港天文台 + Microsoft ChineseLunisolarCalendar 双重验证）
- **年代范围**：1900 - 2100 年
- **闰月**：自动识别，含闰月大小月数据
- **节气**：二十四节气精确到日

## 🚀 快速开始

### 安装

```bash
# 1. 安装 Python 依赖
pip install lunardate

# 2. 将 fortune-teller 文件夹放入 CherryStudio Skills 目录
# Windows: %APPDATA%\CherryStudio\Data\Skills\
# Mac:     ~/Library/Application Support/CherryStudio/Data/Skills/

# 3. 重启 CherryStudio
```

### 使用

在 CherryStudio 中直接对话：

```
帮我排个八字，农历1995年9月20日晚9点，男，榆林
看下事业运
```

或在命令行使用：

```bash
# 公历输入
python scripts/generate_report.py --name 张三 --solar 1990 5 20 8 --gender 男

# 农历输入
python scripts/generate_report.py --name 李四 --lunar 1988 8 15 14 --gender 女

# 指定输出路径
python scripts/generate_report.py --name 王五 --solar 2000 1 1 12 --gender 男 --out ~/Desktop/我的八字.txt
```

报告自动保存到桌面。

## 📋 报告结构

```
第一卷：先天命格（静态分析）
├── 基本资料（公历/农历/真太阳时/节气）
├── 八字排盘详情（四柱/藏干/十神/十二长生）
├── 干支合克与入库
├── 神煞断语
├── 日主概览（滴天髓天干论原文）
├── 五行喜忌（穷通宝鉴调候 + 病药用神）
├── 干支取象（自然意象投射）
├── 命造格局
└── 节气司令

第二卷：后天运路（动态趋势）
├── 大运分析（起运/当前大运/十年走势）
├── 流年动态（当年流年分析）
└── 流月运势

第三卷：民俗与建议（生活应用）
├── 袁天罡称骨
└── 命理生活建议（行业/方位/色彩/性格）
```

## 🛠️ 脚本说明

| 文件 | 功能 |
|------|------|
| `SKILL.md` | CherryStudio Skill 定义（AI 加载入口） |
| `scripts/lunar_data.py` | lunardate 接口，1900-2100 万年历 |
| `scripts/bazi_calculator.py` | 八字推算核心（CLI + Python API） |
| `scripts/generate_report.py` | FateCat 报告生成（通用版） |

## ⚠️ 免责声明

本工具仅供传统文化研究与娱乐参考。命理学非精密科学，推算结果不应作为人生决策的唯一依据。每个人的命运由自身选择、努力和环境共同塑造。

## 📄 License

MIT
