# C 语言学习平台（本地版）

配合翁恺《程序设计入门—C语言》课程的进度跟踪 + 练习判题工具。**多语言判题架构**：目前已内置 C 与 Python，加新语言只需在 `app/judge.py` 的 `LANGUAGES` 注册表加一个 profile。

## 功能

- 按章节/课时组织课程，勾选"标记学完"跟踪进度（侧边栏显示进度条）
- 每课一个练习文件（自动生成模板 + `template.*` 备份，可一键"重置模板"）
- **判题**：编译/解释你的代码 → 跑测试用例 → 输出对比 → 打分（0~100，记录最高分）
- **运行**：手动输入 stdin，看程序输出（没测试用例的课时用它验证）
- 并发安全：每次判题在独立临时目录执行，互不干扰
- 进度存 SQLite，重启不丢；中文输出/中文报错不乱码

## 启动

双击 `start.bat`，或命令行：

```bat
cd c-learning-platform
.venv\Scripts\python -m uvicorn app.main:app --port 8000
```

浏览器打开 http://127.0.0.1:8000

## 目录结构

```
c-learning-platform/
├── app/
│   ├── main.py           # FastAPI 后端 + SQLite 进度
│   ├── judge.py          # 多语言判题器（LANGUAGES 注册表 + 独立临时目录）
│   └── seed_exercises.py # 练习种子（可重跑，不覆盖已有代码）
├── data/
│   ├── lessons.json      # 课程结构（改课时名/加语言课程在这里）
│   ├── exercises/        # 每课的 main.* + template.* + tests.json
│   └── progress.db       # 进度库（自动生成）
├── static/               # 前端（无任何外部依赖）
├── test_e2e.py           # 端到端测试（含并发/多语言）
├── test_encoding.py      # 中文编码测试
└── requirements.txt
```

## 自定义

- 课时名和视频对不上？编辑 `data/lessons.json`（重启生效）
- 给课时加测试用例：在 `data/exercises/<课时id>/tests.json` 写：

```json
[{"name": "用例名", "input": "输入\n", "expected": "期望输出\n"}]
```

- **加一门新语言课程**：`lessons.json` 里给章节或课时加 `"language": "python"` 字段；若语言未注册，在 `app/judge.py` 的 `LANGUAGES` 加一个 profile（ext/compile/run/timeout）
- 判题 C 用 `-std=c11 -Wall -Wextra -O1`（`app/judge.py` 的 `CFLAGS`）

## 依赖

- Python 3.14 + FastAPI + uvicorn（`uv venv` 创建，`uv pip install -r requirements.txt`）
- MSYS2 gcc（判题器会自动找 `C:\msys64\ucrt64\bin\gcc.exe`），Python 判题直接用 venv 的解释器
