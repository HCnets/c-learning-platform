"""编码修复验证：中文输出程序 + 中文期望值 + 中文报错诊断。"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from app.judge import judge  # noqa: E402

GOOD_CODE = """\
#include <stdio.h>
int main(void) {
    int s;
    scanf("%d", &s);
    if (s >= 60) printf("及格\\n");
    else printf("不及格\\n");
    return 0;
}
"""

BAD_CODE = "int main(void) { 中文标识符; return 0; }\n"

tests = [
    {"name": "及格", "input": "80\n", "expected": "及格\n"},
    {"name": "不及格", "input": "40\n", "expected": "不及格\n"},
]

d = Path("data/exercises/_enc_test")
d.mkdir(parents=True, exist_ok=True)
(d / "tests.json").write_text(json.dumps(tests, ensure_ascii=False), encoding="utf-8")

r = judge("_enc_test", GOOD_CODE)
assert r["compile"]["ok"], f"编译失败: {r['compile']['output']}"
assert r["score"] == 100, f"应满分，实际 {r['score']}"
for t in r["tests"]:
    assert t["passed"], f"用例失败: {t}"
print(f"[PASS] 中文程序判题: {r['score']} 分, 输出正确 -> {r['tests'][0]['actual'].strip()}")

r2 = judge("_enc_test", BAD_CODE)
assert not r2["compile"]["ok"] and "undeclared" in r2["compile"]["output"], r2["compile"]["output"]
print("[PASS] 中文报错诊断可正常显示（无乱码/无崩溃）")
