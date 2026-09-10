# 高校教师 AI 提效技能包

把高校教师最耗时的 14 类工作交给 AI 出**初稿**，教师只做判断与补全。

## 快速开始

```bash
# 1. 安装文档产出层依赖（首次必做）
bash vendor/office-layer/bootstrap.sh

# 2. 从总控路由开始
#    先读 SKILL.md，它会按你的意图路由到对应子技能
open SKILL.md
```

在支持 Agent Skills 的客户端里，把本目录加入技能搜索路径即可。入口是根目录的 `SKILL.md`。

### 关于体积

`vendor/office-layer/.venv/` 约 105 MB，是 `bootstrap.sh` 生成的**可再生产物**，已在 `.gitignore` 中排除。
打包分发时请一并剔除，届时整个包约 **5 MB**，接收方跑一次 `bootstrap.sh` 即可复原。

依赖里 `matplotlib` + `numpy` 占约 39 MB，但确有用途（`paper-to-slides` 重绘论文图表、
`research-assistant` 出统计图），故保留。


## 目录结构

```
.
├── SKILL.md                 # 总控路由（先读这个）
├── CONVENTIONS.md           # 开发与使用宪法：不虚构、人工确认位、敏感数据
├── ROADMAP.md               # 场景规划与实现状态
├── README.md                # 本文件
├── vendor/                  # 上游底座（禁止重写，只能引用）
│   ├── VENDOR.md            #   溯源表 + 许可证合规说明
│   ├── office-layer/        #   自建：文件产出唯一通道（docx/pptx/xlsx）
│   ├── awesome-benzi/       #   申报书引擎（七阶段工作流 + 质量门）
│   ├── education-skills/    #   繁體中文教学类
│   ├── ibook-skills/        #   出题/课程分析/学习图谱/术语表/FAQ
│   ├── k12-teacher-skills/  #   教学法参考（Apache-2.0）
│   ├── learning-education/  #   闪卡(FSRS) + 苏格拉底提问 + 学习路径
│   ├── paper-slides/        #   论文 → 汇报 PPT
│   ├── slides-polish/       #   幻灯片视觉打磨
│   └── empirical-research/  #   实证研究（审计/数据字典/文献综述）
└── skills/                  # 14 个子技能
    ├── [教学] lesson-plan / lecture-slides / quiz-generator
    │         exam-pipeline / classroom-live / teaching-contest
    ├── [科研] research-assistant / grant-proposal / paper-to-slides / peer-review
    ├── [指导] thesis-supervisor / lab-meeting
    └── [考核对外] annual-review / science-outreach
```

## 14 个子技能

| 场景 | 子技能 | 教师会说 |
|---|---|---|
| 教学 | `lesson-plan` | 帮我写个教案 |
| | `lecture-slides` | 做课件 / 把这章做成 PPT |
| | `quiz-generator` | 出一套题 / 编几道练习题 |
| | `exam-pipeline` | 审核试卷 / 考后成绩分析 |
| | `classroom-live` | 随堂投票题 / 算平时分 |
| | `teaching-contest` | 准备教学竞赛 / 设计示范课 |
| 科研 | `research-assistant` | 帮我设计研究方案 / 数据分析 |
| | `grant-proposal` | 写本子 / 选题查重 / 模拟评审 |
| | `paper-to-slides` | 把论文做成汇报 PPT |
| | `peer-review` | 帮我写审稿意见 |
| 指导 | `thesis-supervisor` | 看开题报告 / 写论文评语 / 批改论文 |
| | `lab-meeting` | 安排组会轮值 / 生成组会纪要 |
| 考核对外 | `annual-review` | 写年度述职 / 整理职称材料 |
| | `science-outreach` | 做个科普 PPT |

## 文件产出层

所有 docx / pptx / xlsx 产出走 `vendor/office-layer/`，针对中文场景做了处理：

```bash
PY="vendor/office-layer/.venv/bin/python"

# Markdown → Word（中文字体、页码、首行缩进两字）
$PY vendor/office-layer/scripts/docx_kit.py md --in draft.md --out 交付.docx

# 在学生的 Word 文档上写「真批注」（Word 原生，学生看得见批注气球）
$PY vendor/office-layer/scripts/docx_kit.py comment \
    --in 学生论文.docx --out 学生论文_批注.docx --comments 批注.json --author "指导教师"

# 成绩分析（得分率 / 区分度 / 分数段分布）
$PY vendor/office-layer/scripts/xlsx_kit.py analyze \
    --in 成绩.xlsx --out 试卷分析.xlsx --first-q-col 3

# 课件（16:9，可写演讲者备注，自带信息密度检查）
$PY vendor/office-layer/scripts/pptx_kit.py build --spec 课件.json --out 课件.pptx
```

受限环境需要可写的 matplotlib 缓存目录：

```bash
export MPLCONFIGDIR=/tmp/mplcache && mkdir -p /tmp/mplcache
```

## 三条铁律

1. **不虚构**。学生数据绝不生成；文献、政策条文、个人成果一律用 `【待补：…】` 占位。
   高校材料一旦编造，后果是学术不端。
2. **产出是初稿**。涉及评价、打分、结论的内容必须留人工确认位，AI 不给终稿。
3. **文件产出走 office-layer**。不用文本框拼表格，不把 Markdown 当交付物。

## 敏感数据

成绩、学号、姓名、联系方式属个人信息：

- 只在本机处理，不上传、不外发
- 任务结束后删除中间文件
- 交付说明注明「本文件含学生个人信息，请注意保管」

## 许可证

本包**自建部分**（`SKILL.md`、`CONVENTIONS.md`、`skills/*`、`vendor/office-layer/`）为本项目所有。

**上游底座**各自遵循其原许可证，详见 `vendor/VENDOR.md`。特别注意：

- ⚠️ **未收录** Anthropic 官方 `docx`/`pptx`/`xlsx`/`pdf` —— 其为专有许可，
  禁止复制、创作衍生作品与分发。本包以自建 `office-layer/` 替代。
- ⚠️ `vendor/ibook-skills/` 上游仓库**无 LICENSE 文件**，依法默认保留全部权利，
  当前仅供本机自用。对外分发前请先向作者取得授权或移除该目录。
