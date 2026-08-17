"""端到端测试：启动平台后运行本脚本验证所有接口。"""
import json
import urllib.request

BASE = "http://127.0.0.1:8000"


def post(url, payload):
    req = urllib.request.Request(
        BASE + url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    return json.load(urllib.request.urlopen(req))


def get(url):
    return json.load(urllib.request.urlopen(BASE + url))


def test(name, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {name} {detail}")
    if not cond:
        raise SystemExit(1)


# 1. 正确解 -> 100 分
correct = (
    "#include <stdio.h>\n"
    "int main(void) {\n"
    "    int n, i, sum = 0;\n"
    "    scanf(\"%d\", &n);\n"
    "    for (i = 1; i <= n; i++) sum += i;\n"
    "    printf(\"%d\\n\", sum);\n"
    "    return 0;\n"
    "}\n"
)
r = post("/api/lesson/ch4-4/judge", {"code": correct})
test("正确解满分", r["compile"]["ok"] and r["score"] == 100, f"({r['score']} 分)")

# 2. 能编译但输出错 -> 0 分 + 3 个失败用例
wrong = '#include <stdio.h>\nint main(void){ printf("0\\n"); return 0; }\n'
r = post("/api/lesson/ch4-4/judge", {"code": wrong})
test("错误解 0 分", r["score"] == 0 and len(r["tests"]) == 3, f"({r['score']} 分, {len(r['tests'])} 用例)")

# 3. 语法错误 -> 编译失败 + 诊断
broken = '#include <stdio.h>\nint main(void){ printf(; return 0; }\n'
r = post("/api/lesson/ch4-4/judge", {"code": broken})
test("语法错误有诊断", r["compile"]["ok"] is False and len(r["compile"]["output"]) > 0)

# 4. 进度：标记学完 + best_score 持久化
post("/api/lesson/ch1-3/done", {"done": True})
post("/api/lesson/ch4-4/done", {"done": True})
p = get("/api/lessons")["progress"]
test("done 标记", p["ch1-3"]["done"] == 1 and p["ch4-4"]["done"] == 1)
test("best_score 记录", p["ch4-4"]["best_score"] == 100 and p["ch4-4"]["attempts"] >= 3)

# 5. 手动运行
r = post("/api/lesson/ch4-4/run", {"code": correct, "input": "3\n"})
test("手动运行", r["compile_ok"] and r["output"].strip() == "6", f"({r['output'].strip()})")

# 6. 静态页面
for path, tag in [("/", "index"), ("/app.js", "app.js"), ("/style.css", "style.css")]:
    code = urllib.request.urlopen(BASE + path).status
    test(f"{tag} 可访问", code == 200)

# 7. 进度回读（重启后仍在 -> SQLite 持久化）
p = get("/api/lesson/ch4-4")["progress"]
test("进度持久化", p["best_score"] == 100)

print("\n全部测试通过 ✅")
