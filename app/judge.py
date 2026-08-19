"""多语言判题器：编译（可选）→ 逐用例运行 → 对比输出 → 打分。

设计要点：
- 每个提交在独立临时目录里编译/运行，互不干扰（并发安全）
- 语言通过 LANGUAGES 注册表扩展：加一门语言 = 加一个 profile
- 所有子进程显式 UTF-8 解码，中文输出/报错不乱码
- 超时用 taskkill /T /F 杀掉整个进程树，不留孤儿进程
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
EXERCISES = BASE / "data" / "exercises"

CFLAGS = ["-std=c11", "-Wall", "-Wextra", "-O1"]
COMPILE_TIMEOUT = 30  # 编译超时（秒）
RUN_TIMEOUT = 5       # 单用例默认运行超时（秒）

NO_WINDOW = subprocess.CREATE_NO_WINDOW


def find_gcc() -> str:
    """优先用 PATH 里的 gcc，找不到就退回 MSYS2 默认安装路径。"""
    found = shutil.which("gcc")
    if found:
        return found
    env = os.environ.get("CC")
    if env and Path(env).exists():
        return env
    default = Path(r"C:\msys64\ucrt64\bin\gcc.exe")
    return str(default) if default.exists() else "gcc"


def find_gpp() -> str:
    """C++ 编译器，逻辑同 find_gcc。"""
    found = shutil.which("g++")
    if found:
        return found
    default = Path(r"C:\msys64\ucrt64\bin\g++.exe")
    return str(default) if default.exists() else "g++"


def toolchain_env() -> dict:
    """gcc 编译和生成的 exe 运行都依赖 ucrt64 的 DLL（如 libgcc_s_seh-1.dll），
    它们靠 PATH 查找，这里把工具链 bin 目录注入子进程环境，避免静默失败。"""
    env = dict(os.environ)
    bin_dir = str(Path(find_gcc()).parent)
    if bin_dir not in env.get("PATH", ""):
        env["PATH"] = bin_dir + os.pathsep + env.get("PATH", "")
    return env


# ---------- 语言注册表：加新语言在这里加一个 profile ----------

LANGUAGES = {
    "c": {
        "ext": "c",
        "display": "C",
        "compile": lambda src, out: [find_gcc(), *CFLAGS, "-o", str(out), str(src)],
        "run": lambda exe: [str(exe)],
        "timeout": RUN_TIMEOUT,
    },
    "python": {
        "ext": "py",
        "display": "Python",
        "compile": None,  # 解释执行，跳过编译
        "run": lambda src: [sys.executable, str(src)],
        "timeout": 10,
    },
    "cpp": {
        "ext": "cpp",
        "display": "C++",
        "compile": lambda src, out: [find_gpp(), "-std=c++17", "-Wall", "-Wextra", "-O2", "-o", str(out), str(src)],
        "run": lambda exe: [str(exe)],
        "timeout": RUN_TIMEOUT,
    },
}

DEFAULT_LANG = "c"


def resolve_lang(language: str | None) -> str:
    return language if language in LANGUAGES else DEFAULT_LANG


def lesson_lang(lesson_id: str, lessons_data: dict) -> str:
    """课时所属语言：课时字段 > 章节字段 > 默认 c。"""
    for chapter in lessons_data["chapters"]:
        for lesson in chapter["lessons"]:
            if lesson["id"] == lesson_id:
                return lesson.get("language") or chapter.get("language") or DEFAULT_LANG
    return DEFAULT_LANG


def load_tests(lesson_id: str) -> list:
    tests_file = EXERCISES / lesson_id / "tests.json"
    if not tests_file.exists():
        return []
    data = json.loads(tests_file.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else []


def normalize(text: str) -> str:
    """统一换行、去掉每行行尾空格和首尾空行，让判题对格式宽容。"""
    lines = [line.rstrip() for line in text.replace("\r\n", "\n").split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    while lines and lines[0] == "":
        lines.pop(0)
    return "\n".join(lines)


def _spawn(cmd, **kwargs):
    """带统一编码/无窗口的子进程调用。"""
    kwargs.setdefault("capture_output", True)
    kwargs.setdefault("text", True)
    kwargs.setdefault("encoding", "utf-8")
    kwargs.setdefault("errors", "replace")
    kwargs.setdefault("creationflags", NO_WINDOW)
    kwargs.setdefault("env", toolchain_env())
    return subprocess.run(cmd, **kwargs)


def compile_code(workdir: Path, code: str, lang: str) -> dict:
    """在 workdir 里写源码并编译（解释型语言跳过编译）。"""
    profile = LANGUAGES[lang]
    src = workdir / f"main.{profile['ext']}"
    src.write_text(code, encoding="utf-8")

    if profile["compile"] is None:
        return {"ok": True, "output": "", "exe_path": str(src)}

    out = workdir / "main.exe"
    try:
        proc = _spawn(profile["compile"](src, out), timeout=COMPILE_TIMEOUT)
    except subprocess.TimeoutExpired:
        return {"ok": False, "output": "编译超时（超过 30 秒）"}
    if proc.returncode != 0:
        return {"ok": False, "output": (proc.stderr or proc.stdout).strip()}
    return {"ok": True, "output": (proc.stdout or "").strip(), "exe_path": str(out)}


def kill_tree(proc) -> None:
    """subprocess 超时后 kill 只杀直接子进程，这里用 taskkill 杀整棵树。"""
    try:
        subprocess.run(
            ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
            capture_output=True, creationflags=NO_WINDOW, timeout=10,
        )
    except (subprocess.TimeoutExpired, OSError):
        pass


def run_one(profile: dict, exe: str, test_input: str) -> dict:
    try:
        proc = _spawn(profile["run"](exe), input=test_input, timeout=profile["timeout"])
        return {"timeout": False, "error": None, "stdout": proc.stdout, "stderr": proc.stderr}
    except subprocess.TimeoutExpired as e:
        kill_tree(e)  # TimeoutExpired 带 .pid
        return {"timeout": True, "error": f"运行超时（超过 {profile['timeout']} 秒）", "stdout": "", "stderr": ""}
    except OSError as e:
        return {"timeout": False, "error": f"程序无法启动：{e}", "stdout": "", "stderr": ""}


def judge(lesson_id: str, code: str, lang: str | None = None) -> dict:
    """编译并判题，返回结果字典。"""
    lang = resolve_lang(lang)
    profile = LANGUAGES[lang]
    result = {"lesson_id": lesson_id, "language": lang, "compile": None, "tests": [], "score": -1}

    tmp_root = BASE / "data" / "tmp"
    tmp_root.mkdir(parents=True, exist_ok=True)
    workdir = Path(tempfile.mkdtemp(prefix=f"{lesson_id}-", dir=tmp_root))
    try:
        comp = compile_code(workdir, code, lang)
        result["compile"] = comp
        if not comp["ok"]:
            result["score"] = 0
            return result

        tests = load_tests(lesson_id)
        passed = 0
        for i, test in enumerate(tests, 1):
            name = test.get("name", f"用例{i}")
            expected = test.get("expected", "")
            run = run_one(profile, comp["exe_path"], test.get("input", ""))
            if run["timeout"] or run["error"]:
                result["tests"].append({
                    "name": name, "passed": False,
                    "reason": run["error"] or "运行超时", "expected": expected, "actual": "",
                })
                continue
            actual = run["stdout"]
            ok = normalize(actual) == normalize(expected)
            if ok:
                passed += 1
            result["tests"].append({
                "name": name, "passed": ok,
                "reason": "" if ok else "输出不匹配",
                "expected": expected, "actual": actual,
            })

        total = len(tests)
        result["score"] = round(100 * passed / total) if total else -1
        result["passed"] = passed
        result["total"] = total
        return result
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def run_manual(lesson_id: str, code: str, stdin_text: str, lang: str | None = None) -> dict:
    """只编译 + 跑一次，返回 stdout/stderr（不判题），用于手动调试。"""
    lang = resolve_lang(lang)
    profile = LANGUAGES[lang]

    tmp_root = BASE / "data" / "tmp"
    tmp_root.mkdir(parents=True, exist_ok=True)
    workdir = Path(tempfile.mkdtemp(prefix=f"{lesson_id}-", dir=tmp_root))
    try:
        comp = compile_code(workdir, code, lang)
        if not comp["ok"]:
            return {"compile_ok": False, "output": comp["output"]}
        run = run_one(profile, comp["exe_path"], stdin_text)
        if run["timeout"] or run["error"]:
            return {"compile_ok": True, "output": run["error"], "timed_out": True}
        return {
            "compile_ok": True,
            "output": run["stdout"] + (run["stderr"] if run["stderr"] else ""),
            "timed_out": False,
        }
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
