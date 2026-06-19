# JobTool 求职投递记录助手

JobTool 是一个本地运行的求职投递管理工具。用户通过快速表单或批量消息输入公司、岗位、投递日期和进度，程序在确认后将信息结构化写入 Excel，并提供搜索筛选、跟进提醒、状态更新和数据看板。

数据默认只保存在本地 Excel 文件中，不需要 SQLite、服务器或云端账号，适合个人长期记录，也便于将 Windows 运行包分享给其他求职者。

## 功能

- 快速表单：逐条录入公司、岗位、状态、方向、渠道、地点和优先级
- 智能消息：解析键值文本、常见自然语言和一行一条的批量岗位信息
- 写入前预览：支持编辑、移除、必填校验和同批次重复提醒
- 投递管理：按关键词、状态和岗位方向搜索，更新进度并打开招聘链接
- 跟进中心：记录沟通过程和下一步行动，同步下一步日期并生成待办提醒
- 数据看板：展示投递数量、面试转化、状态分布、渠道分布和近期跟进事项
- Excel 报表：内置筛选、数据验证、条件格式、指标卡、待办清单和四张图表
- 本地安全：每次写入前自动备份，最多保留最近 30 份

## 使用方式

### Windows 运行包

从 GitHub Releases 下载 `JobTool-Windows-x64.zip`，解压后双击：

```text
JobTracker.exe
```

必须保留压缩包中的完整目录，不能只复制 EXE。首次启动会在程序目录自动创建：

```text
求职投递管理工具.xlsx
config.json
backups/
```

请将程序解压到桌面、文档等具有写权限的目录，不要放到 `Program Files`。写入数据前需关闭 Excel/WPS 中打开的当前数据文件。

### 源码运行

要求 Python 3.10 或更高版本。

```powershell
git clone https://github.com/1622354895/JobTool.git
cd JobTool
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

macOS 和 Linux 可以运行源码，但需要使用对应平台的 Python 环境。Windows EXE 不能直接在其他操作系统运行。

## 输入示例

快速表单适合单条录入；“智能消息 / 批量录入”支持一行一条记录：

```text
公司：字节跳动；岗位：Agent开发实习生；日期：今天；状态：已投递；渠道：Boss直聘；地点：北京；优先级：高
公司：腾讯；岗位：大模型应用实习生；日期：2026-06-19；状态：待投递；渠道：公司官网；地点：深圳
```

所有新增数据都会先进入预览区，确认后才写入 Excel。更多格式见 [消息示例](examples/消息示例.txt)。

## 数据文件

工作簿包含以下工作表：

| 工作表 | 用途 |
| --- | --- |
| 使用说明 | 快速开始和注意事项 |
| 数据看板 | 指标、近期待办和趋势图表 |
| 投递记录 | 求职投递主数据 |
| 跟进记录 | 沟通、面试和复盘记录 |
| 选项配置 | 状态、方向、渠道等下拉选项 |

不要修改工作表名称、主表表头或公式列，否则程序会拒绝读取该文件。

## 测试

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q --basetemp=.pytest_tmp
.\.venv\Scripts\python.exe scripts\build_template.py
.\.venv\Scripts\python.exe scripts\verify_workbook.py
```

测试覆盖消息解析、岗位分类、Excel 追加与更新、重复检查、删除恢复、跟进日期同步、指标计算和工作簿结构。

## Windows 打包

```powershell
powershell -ExecutionPolicy Bypass -File scripts\build_windows.ps1
```

构建产物：

```text
dist/JobTracker/                 # 解压后的完整运行目录
dist/JobTool-Windows-x64.zip     # 可上传到 GitHub Releases 的发布包
```

发布 ZIP 不包含本机配置、个人求职记录或备份文件。

## 项目结构

```text
app.py                  程序入口
job_tracker/            解析、分类、Excel 存储、统计和桌面界面
tests/                  自动化测试
scripts/                模板验证与 Windows 打包脚本
examples/               消息输入示例
```

## 隐私说明

JobTool 不会主动上传求职信息，也不包含网络请求。招聘链接仅在用户点击“打开链接”时交由系统浏览器处理。分享运行目录前，请删除其中的个人 Excel、`config.json` 和 `backups`。

## License

本项目使用 [MIT License](LICENSE)。
