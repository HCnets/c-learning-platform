"""C 代码判题器：编译 main.c -> 跑测试用例 -> 对比输出打分。

依赖 MSYS2/MinGW 的 gcc，路径可通过 CC 环境变量或下方 GCC 常量覆盖。
"""
import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
EXERCISES = BASE / "data" / "exercises"
BUILD_DIR = BASE / "data" / "build"

CFLAGS = ["-std=c11", "-Wall", "-Wextra", "-O1"]
TEST_TIMEOUT = 5  # 单个测试用例超时（秒）


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


def toolchain_env() -> dict:
    """gcc 编译和生成的 exe 运行都依赖 ucrt64 的 DLL（如 libgcc_s_seh-1.dll），
    它们靠 PATH 查找，这里把工具链 bin 目录注入子进程环境，避免静默失败。"""
    env = dict(os.environ)
    bin_dir = str(Path(find_gcc()).parent)
    if bin_dir not in env.get("PATH", ""):
        env["PATH"] = bin_dir + os.pathsep + env.get("PATH", "")
    return env


def normalize(text: str) -> str:
    """统一换行、去掉每行行尾空格和首尾空行，让判题对格式宽容。"""
    lines = [line.rstrip() for line in text.replace("\r\n", "\n").split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    while lines and lines[0] == "":
        lines.pop(0)
    return "\n".join(lines)


def load_tests(lesson_id: str) -> list:
    tests_file = EXERCISES / lesson_id / "tests.json"
    if not tests_file.exists():
        return []
    data = json.loads(tests_file.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else []


def compile_code(lesson_id: str, code: str) -> dict:
    """保存代码并编译，返回 {ok, exe_path, output}。"""
    workdir = EXERCISES / lesson_id
    workdir.mkdir(parents=True, exist_ok=True)
    (workdir / "main.c").write_text(code, encoding="utf-8")

    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    exe = BUILD_DIR / f"{lesson_id}.exe"
    cmd = [find_gcc(), *CFLAGS, "-o", str(exe), str(workdir / "main.c")]
    proc = subprocess.run(
        cmd, capture_output=True, text=True,
        creationflags=subprocess.CREATE_NO_WINDOW,
        env=toolchain_env(),
    )
    if proc.returncode != 0:
        return {"ok": False, "output": (proc.stderr or proc.stdout).strip()}
    return {"ok": True, "output": (proc.stdout or "").strip(), "exe_path": str(exe)}


def run_one(exe: str, test_input: str) -> dict:
    try:
        proc = subprocess.run(
            [exe],
            input=test_input,
            capture_output=True,
            text=True,
            timeout=TEST_TIMEOUT,
            creationflags=subprocess.CREATE_NO_WINDOW,
            env=toolchain_env(),
        )
        return {"timeout": False, "stdout": proc.stdout, "stderr": proc.stderr}
    except subprocess.TimeoutExpired:
        return {"timeout": True, "stdout": "", "stderr": ""}


def judge(lesson_id: str, code: str) -> dict:
    """编译并判题，返回结果字典。"""
    result = {"lesson_id": lesson_id, "compile": None, "tests": [], "score": -1}
    comp = compile_code(lesson_id, code)
    result["compile"] = comp
    if not comp["ok"]:
        result["score"] = 0
        return result

    tests = load_tests(lesson_id)
    passed = 0
    for i, test in enumerate(tests, 1):
        name = test.get("name", f"用例{i}")
        expected = test.get("expected", "")
        run = run_one(comp["exe_path"], test.get("input", ""))
        if run["timeout"]:
            result["tests"].append({
                "name": name, "passed": False,
                "reason": "运行超时", "expected": expected, "actual": "",
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


def run_manual(lesson_id: str, code: str, stdin_text: str) -> dict:
    """只编译 + 跑一次，返回 stdout/stderr（不判题），用于手动调试。"""
    comp = compile_code(lesson_id, code)
    if not comp["ok"]:
        return {"compile_ok": False, "output": comp["output"]}
    run = run_one(comp["exe_path"], stdin_text)
    if run["timeout"]:
        return {"compile_ok": True, "output": "（运行超时）", "timed_out": True}
    return {
        "compile_ok": True,
        "output": run["stdout"] + (run["stderr"] if run["stderr"] else ""),
        "timed_out": False,
    }
