# JobTool - 本地优先的求职投递管理助手

<p align="center">
  <strong>把零散的公司、岗位和投递进度，自动整理成可搜索、可跟进、可视化的 Excel 求职台账。</strong>
</p>

<p align="center">
  <a href="https://github.com/1622354895/JobTool/releases/latest"><img alt="Release" src="https://img.shields.io/github/v/release/1622354895/JobTool?display_name=tag&sort=semver"></a>
  <a href="https://github.com/1622354895/JobTool/releases"><img alt="Downloads" src="https://img.shields.io/github/downloads/1622354895/JobTool/total"></a>
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white">
  <img alt="Tests" src="https://img.shields.io/badge/tests-41%20passed-2ea44f">
  <a href="LICENSE"><img alt="License" src="https://img.shields.io/github/license/1622354895/JobTool"></a>
</p>

<p align="center">
  <a href="https://github.com/1622354895/JobTool/releases/latest"><strong>下载 Windows 版</strong></a>
  ·
  <a href="#快速开始">快速开始</a>
  ·
  <a href="#输入示例">输入示例</a>
  ·
  <a href="#参与贡献">参与贡献</a>
</p>

JobTool 是一款面向校招、实习和社招求职者的桌面投递管理工具。你可以通过快速表单或批量消息输入公司、岗位、投递时间和进度，程序会在确认后将信息结构化写入 Excel，并提供搜索筛选、跟进提醒、状态更新和数据看板。

**无需数据库、服务器、云端账号或 API Key。** 数据默认只保存在本地 Excel 文件中；Windows 用户可以直接下载打包版本，解压即用。

## 差异化定位

GitHub 上已有不少 Job Application Tracker、Excel Tracker、AI 自动投递和简历 Copilot 项目。JobTool 的定位不是自动投递，而是**本地优先、开箱即用、适合中文求职记录的桌面 Excel 台账**：EXE 负责录入、选项管理、搜索、跟进和看板；Excel 负责本地数据承载、公式和图表展示。它更适合希望把数据留在本机、又不想手动维护复杂表格的用户。

## 为什么使用 JobTool

| 常见问题 | JobTool 的处理方式 |
| --- | --- |
| 投递记录散落在聊天、备忘录和招聘平台 | 快速表单和批量消息统一录入 |
| 手动维护 Excel 字段多、容易漏填 | 自动解析、分类、校验并追加到工作簿 |
| 忘记笔试、面试和 HR 跟进时间 | 跟进中心同步待办日期并标记逾期事项 |
| 投了很多岗位，却看不清转化情况 | 桌面看板和 Excel 图表实时统计 |
| 不希望求职数据上传到第三方服务 | 本地 Excel 存储，不主动发送网络请求 |

## 核心功能

- **快速录入**：记录公司、岗位、状态、类型、方向、渠道、地点、优先级和招聘链接。
- **批量解析**：支持键值文本、常见自然语言表达和一行一条的批量岗位信息。
- **写入前预览**：编辑或移除待写入记录，校验必填项并提示同批次重复数据。
- **投递管理**：按关键词、状态和岗位方向检索，更新进度并打开招聘链接。
- **选项管理**：在 EXE 内新增、重命名或删除状态、岗位类型、岗位方向、渠道、优先级和跟进类型，并自动同步 Excel。
- **跟进提醒**：记录沟通、笔试、面试、下一步行动和日期，按逾期、今日、未来 7 天或全部安排筛选。
- **可视化看板**：统计累计投递、待跟进、回复率、面试转化、状态、岗位方向、渠道和优先级分布。
- **Excel 自动化**：Excel 作为本地数据文件和看板文件，内置筛选、下拉选项、条件格式、指标卡、待办清单和四张图表。
- **内置帮助**：EXE 侧栏提供“使用帮助”弹窗，覆盖首次使用、录入、选项管理、跟进、看板、备份和分享给别人使用。
- **备份保护**：每次写入前自动备份，默认保留最近 30 份。

## 工作流程

```mermaid
flowchart LR
    A[快速表单或批量消息] --> B[解析与岗位分类]
    B --> C[预览、校验与去重提醒]
    C --> D[追加到本地 Excel]
    D --> E[搜索、跟进与状态更新]
    D --> F[桌面看板与 Excel 图表]
```

## 快速开始

### Windows 免安装版

1. 前往 [Releases](https://github.com/1622354895/JobTool/releases/latest) 下载 `JobTool-Windows-x64.zip`。
2. 完整解压 ZIP，不要只复制其中的 EXE。
3. 双击 `JobTracker.exe`。
4. 需要操作说明时，点击左侧侧栏的“使用帮助”。

首次启动会在程序目录自动创建：

```text
求职投递管理工具.xlsx
config.json
backups/
```

建议解压到桌面、文档等具有写权限的目录，不要放入 `Program Files`。程序写入数据前，请先关闭 Excel/WPS 中正在打开的目标工作簿。

### 源码运行

需要 Python 3.10 或更高版本。

```powershell
git clone https://github.com/1622354895/JobTool.git
cd JobTool
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

macOS 和 Linux 可以运行源码，但需要使用对应平台的 Python/Tk 环境；Windows EXE 不能直接在其他操作系统运行。

## 输入示例

快速表单适合单条录入；“智能消息 / 批量录入”支持一行一条记录：

```text
公司：字节跳动；岗位：Agent开发实习生；日期：今天；状态：已投递；渠道：Boss直聘；地点：北京；优先级：高
公司：腾讯；岗位：大模型应用实习生；日期：2026-06-19；状态：待投递；渠道：公司官网；地点：深圳
```

新增数据会先进入预览区，确认后才写入 Excel。更多可识别格式见 [消息输入示例](examples/消息示例.txt)。

## Excel 工作簿

| 工作表 | 用途 |
| --- | --- |
| 使用说明 | 快速开始和使用注意事项 |
| 数据看板 | 核心指标、近期待办和趋势图表 |
| 投递记录 | 公司、岗位、渠道、状态等主数据 |
| 跟进记录 | 沟通、笔试、面试和复盘记录 |
| 选项配置 | 程序自动维护的下拉选项来源 |

请把编辑操作放在 EXE 中完成。Excel 适合作为本地数据文件和看板文件查看；请勿修改工作表名称、主表表头或公式列，否则程序会拒绝读取不兼容的工作簿。

## 技术实现

- Python 3.10+
- ttkbootstrap / Tkinter 桌面界面
- openpyxl Excel 读写、格式和图表
- matplotlib 数据可视化
- PyInstaller Windows 打包
- pytest 自动化测试

项目采用“解析与分类 → 数据模型 → Excel 存储 → 统计服务 → 桌面界面”的分层结构，核心逻辑不依赖 GUI，便于测试和扩展。

## 测试与构建

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q --basetemp=.pytest_tmp
.\.venv\Scripts\python.exe scripts\build_template.py
.\.venv\Scripts\python.exe scripts\verify_workbook.py
```

测试覆盖消息解析、岗位分类、自定义选项同步、Excel 追加与更新、重复检查、删除恢复、跟进日期同步、指标计算和工作簿结构。

构建 Windows 发布包：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\build_windows.ps1
```

构建产物：

```text
dist/JobTracker/                 # 完整运行目录，EXE 位于该目录
dist/JobTool-Windows-x64.zip     # 可直接发给别人使用的发布压缩包
```

发布包不包含本机配置、个人求职记录或备份文件。

## 项目结构

```text
app.py                  程序入口
job_tracker/            解析、分类、Excel 存储、统计和桌面界面
tests/                  自动化测试
scripts/                模板验证与 Windows 打包脚本
examples/               消息输入示例
```

## 路线图

- [ ] 支持 CSV/Excel 历史记录导入
- [ ] 增加面试日历视图和桌面提醒
- [x] 支持在 EXE 内维护状态、类型、方向、渠道、优先级和跟进类型
- [ ] 提供可配置的自定义字段与更多统计维度
- [ ] 补充 macOS/Linux 打包与使用验证

欢迎通过 [Issues](https://github.com/1622354895/JobTool/issues) 提交问题或功能建议。

## 参与贡献

1. Fork 本仓库并创建功能分支。
2. 完成修改并补充相应测试。
3. 确保测试通过后提交 Pull Request。

如果这个工具对你的求职记录有帮助，可以给项目一个 Star，让更多求职者看到它。

## 隐私说明

JobTool 不会主动上传求职信息，也不包含后台网络同步功能。招聘链接仅在用户点击“打开链接”后交由系统浏览器处理。分享运行目录前，请删除个人 Excel、`config.json` 和 `backups`。

## License

本项目采用 [MIT License](LICENSE)。
