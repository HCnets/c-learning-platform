"""C++ 判题端到端测试。"""
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


# 1. A+B 正确解 -> 100 分
ab = """#include <bits/stdc++.h>
using namespace std;

int main() {
    int a, b;
    cin >> a >> b;
    cout << a + b << endl;
    return 0;
}
"""
r = post("/api/lesson/cpp1-2/judge", {"code": ab})
assert r["compile"]["ok"], r["compile"]["output"]
assert r["score"] == 100, r
print(f"[PASS] C++ A+B 满分: {r['score']} 分 ({r['passed']}/{r['total']})")

# 2. 排序正确解 -> 100 分
sort_code = """#include <bits/stdc++.h>
using namespace std;

int main() {
    int n;
    cin >> n;
    vector<int> a(n);
    for (int i = 0; i < n; i++) cin >> a[i];
    sort(a.begin(), a.end());
    for (int i = 0; i < n; i++) {
        if (i) cout << ' ';
        cout << a[i];
    }
    cout << endl;
    return 0;
}
"""
r2 = post("/api/lesson/cpp1-3/judge", {"code": sort_code})
assert r2["compile"]["ok"], r2["compile"]["output"]
assert r2["score"] == 100, r2
print(f"[PASS] C++ 排序满分: {r2['score']} 分")

# 3. 语法错误 -> 有诊断
bad = "int main() { cout << ; return 0; }\n"
r3 = post("/api/lesson/cpp1-2/judge", {"code": bad})
assert not r3["compile"]["ok"] and r3["compile"]["output"], r3
print("[PASS] C++ 语法错误有诊断")

# 4. 章节语言标识
r4 = post("/api/lesson/cpp1-2/run", {"code": ab, "input": "1 2\n"})
assert r4["compile_ok"] and r4["output"].strip() == "3", r4
print("[PASS] C++ 手动运行 1+2 =", r4["output"].strip())

print("\nC++ 判题全部通过 ✅")
