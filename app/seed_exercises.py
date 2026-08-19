"""生成练习文件：每个课时一个 main 模板（源码 + template 备份），部分课时附 tests.json。

用法：python -m app.seed_exercises   （可重复运行，不会覆盖已有代码）
"""
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from app.judge import LANGUAGES  # noqa: E402
from app.main import EXERCISES, load_lessons  # noqa: E402

TEMPLATE = """\
/*
 * {title}
 * 在下面编写你的代码。写完后点页面上的"判题"按钮验证。
 */
#include <stdio.h>

int main(void)
{{
    // TODO: 在这里写你的代码

    return 0;
}}
"""

# 带测试用例的练习：lesson_id -> (起始模板, 测试用例列表)
EXERCISE_SPECS = {

    "ch2-3": ("""\
/*
 * 华氏温度转摄氏温度（整数运算）
 * 输入：一个整数 F（华氏温度）
 * 输出：摄氏温度 C = 5 * (F - 32) / 9
 * 例：输入 212，输出 100
 */
#include <stdio.h>

int main(void)
{
    int f;

    scanf("%d", &f);

    // TODO: 计算并输出摄氏温度

    return 0;
}
""", [
        {"name": "沸点 212", "input": "212\n", "expected": "100\n"},
        {"name": "冰点 32", "input": "32\n", "expected": "0\n"},
        {"name": "常温 100", "input": "100\n", "expected": "37\n"},
    ]),

    "ch3-3": ("""\
/*
 * 成绩分级
 * 输入：一个整数成绩 s（0~100）
 * 输出：A（s>=90）、B（s>=80）、C（s>=70）、D（s>=60）、E（其余）
 * 例：输入 95，输出 A
 */
#include <stdio.h>

int main(void)
{
    int s;

    scanf("%d", &s);

    // TODO: 用 if / else if 分级并输出

    return 0;
}
""", [
        {"name": "优秀 95", "input": "95\n", "expected": "A\n"},
        {"name": "良好 80", "input": "80\n", "expected": "B\n"},
        {"name": "及格 60", "input": "60\n", "expected": "D\n"},
        {"name": "不及格 59", "input": "59\n", "expected": "E\n"},
    ]),

    "ch4-4": ("""\
/*
 * 求 1 + 2 + ... + n 的和
 * 输入：一个整数 n（1 <= n <= 1000）
 * 输出：累加和
 * 例：输入 10，输出 55
 */
#include <stdio.h>

int main(void)
{
    int n, i, sum = 0;

    scanf("%d", &n);

    // TODO: 用 while / for 循环累加 1 到 n

    return 0;
}
""", [
        {"name": "n=10", "input": "10\n", "expected": "55\n"},
        {"name": "n=100", "input": "100\n", "expected": "5050\n"},
        {"name": "n=1", "input": "1\n", "expected": "1\n"},
    ]),

    "ch5-3": ("""\
/*
 * 判断素数
 * 输入：一个整数 n（2 <= n <= 10000）
 * 输出：是素数输出 Yes，否则输出 No
 * 例：输入 7，输出 Yes；输入 9，输出 No
 */
#include <stdio.h>

int main(void)
{
    int n, i, is_prime = 1;

    scanf("%d", &n);

    // TODO: 用循环判断 n 是否为素数，修改 is_prime

    if (is_prime)
        printf("Yes\\n");
    else
        printf("No\\n");

    return 0;
}
""", [
        {"name": "素数 7", "input": "7\n", "expected": "Yes\n"},
        {"name": "素数 2", "input": "2\n", "expected": "Yes\n"},
        {"name": "合数 9", "input": "9\n", "expected": "No\n"},
        {"name": "合数 10000", "input": "10000\n", "expected": "No\n"},
    ]),

    "ch6-3": ("""\
/*
 * 数字各位求和
 * 输入：一个非负整数 n（0 <= n <= 1000000000）
 * 输出：各位数字之和
 * 例：输入 12345，输出 15
 */
#include <stdio.h>

int main(void)
{
    int n, sum = 0;

    scanf("%d", &n);

    // TODO: 循环取出 n 的每一位累加（提示：n % 10 取个位，n / 10 去掉个位）

    printf("%d\\n", sum);
    return 0;
}
""", [
        {"name": "12345", "input": "12345\n", "expected": "15\n"},
        {"name": "0", "input": "0\n", "expected": "0\n"},
        {"name": "1000000000", "input": "1000000000\n", "expected": "1\n"},
    ]),

    "ch7-3": ("""\
/*
 * 阶乘函数
 * 输入：一个整数 n（0 <= n <= 12）
 * 输出：n! （0! = 1）
 * 例：输入 5，输出 120
 */
#include <stdio.h>

// TODO: 定义函数 factorial(n)，用循环计算并返回 n!

int main(void)
{
    int n;

    scanf("%d", &n);
    printf("%d\\n", factorial(n));
    return 0;
}
""", [
        {"name": "5!", "input": "5\n", "expected": "120\n"},
        {"name": "0!", "input": "0\n", "expected": "1\n"},
        {"name": "12!", "input": "12\n", "expected": "479001600\n"},
    ]),

    "ch8-3": ("""\
/*
 * 平均值与超过平均的人数（翁恺课堂经典题）
 * 输入：第一行一个整数 n，第二行 n 个整数（成绩，0~100）
 * 输出：两行——平均分（整数，向下取整）、超过平均分的人数
 * 例：输入 5 / 80 90 70 60 100，输出 80 / 2
 */
#include <stdio.h>

int main(void)
{
    int n, i;
    int scores[1000];
    int sum = 0;

    scanf("%d", &n);
    for (i = 0; i < n; i++) {
        scanf("%d", &scores[i]);
        sum += scores[i];
    }

    // TODO: 计算平均分 avg，然后统计 scores 中大于 avg 的个数

    return 0;
}
""", [
        {"name": "样例", "input": "5\n80 90 70 60 100\n", "expected": "80\n2\n"},
        {"name": "全部相同", "input": "4\n60 60 60 60\n", "expected": "60\n0\n"},
        {"name": "n=1", "input": "1\n100\n", "expected": "100\n0\n"},
    ]),

    "ch9-3": ("""\
/*
 * swap 交换函数（指针）
 * 输入：两个整数 a b
 * 输出：交换后的 a b，空格隔开
 * 例：输入 3 5，输出 5 3
 */
#include <stdio.h>

// TODO: 定义函数 swap(int *pa, int *pb)，交换两个指针指向的值

int main(void)
{
    int a, b;

    scanf("%d %d", &a, &b);
    swap(&a, &b);
    printf("%d %d\\n", a, b);
    return 0;
}
""", [
        {"name": "3 5", "input": "3 5\n", "expected": "5 3\n"},
        {"name": "负数", "input": "-7 -2\n", "expected": "-2 -7\n"},
        {"name": "相等", "input": "4 4\n", "expected": "4 4\n"},
    ]),

    "ch10-3": ("""\
/*
 * 统计字符串长度（自己实现 strlen）
 * 输入：一行字符串（不含空格，长度 <= 99）
 * 输出：字符串的长度
 * 例：输入 hello，输出 5
 */
#include <stdio.h>

int my_strlen(char s[])
{
    // TODO: 用循环数出字符个数，直到 '\\0' 为止

}

int main(void)
{
    char s[100];

    scanf("%s", s);
    printf("%d\\n", my_strlen(s));
    return 0;
}
""", [
        {"name": "hello", "input": "hello\n", "expected": "5\n"},
        {"name": "单个字符", "input": "a\n", "expected": "1\n"},
        {"name": "空串", "input": "\\n", "expected": "0\n"},
    ]),

    "ch11-3": ("""\
/*
 * 结构体存成绩求平均
 * 输入：第一行整数 n，之后 n 行每行"姓名 成绩"
 * 输出：平均分（整数，向下取整）
 * 例：输入 3 / Alice 90 / Bob 80 / Cindy 100，输出 90
 */
#include <stdio.h>

struct Student {
    char name[50];
    int score;
};

int main(void)
{
    int n, i, sum = 0;
    struct Student st[100];

    scanf("%d", &n);
    for (i = 0; i < n; i++) {
        scanf("%s %d", st[i].name, &st[i].score);
        sum += st[i].score;
    }

    // TODO: 计算并输出平均分

    return 0;
}
""", [
        {"name": "样例", "input": "3\nAlice 90\nBob 80\nCindy 100\n", "expected": "90\n"},
        {"name": "平均为小数", "input": "2\nA 90\nB 91\n", "expected": "90\n"},
        {"name": "n=1", "input": "1\nSolo 60\n", "expected": "60\n"},
    ]),

    # ---- Python 扩展示例（多语言判题演示）----

    "py1-2": ("""\
# 计算 1 + 2 + ... + n 的和（Python 版）
# 输入：一个整数 n
# 输出：累加和
# 例：输入 10，输出 55
n = int(input())

# TODO: 计算并输出 1 到 n 的累加和

""", [
        {"name": "n=10", "input": "10\n", "expected": "55\n"},
        {"name": "n=100", "input": "100\n", "expected": "5050\n"},
        {"name": "n=1", "input": "1\n", "expected": "1\n"},
    ]),

    # ---- C++ 竞赛入门 ----

    "cpp1-2": ("""\
// A+B Problem —— 竞赛界第一题（洛谷 P1001 / 牛客 / Codeforces 都有它）
// 输入：两个整数 a b
// 输出：a + b
// 例：输入 1 2，输出 3
#include <bits/stdc++.h>
using namespace std;

int main() {
    int a, b;
    cin >> a >> b;
    // TODO: 输出 a + b
    return 0;
}
""", [
        {"name": "1+2", "input": "1 2\n", "expected": "3\n"},
        {"name": "负数", "input": "-5 8\n", "expected": "3\n"},
        {"name": "大数", "input": "100000 200000\n", "expected": "300000\n"},
    ]),

    "cpp1-3": ("""\
// 排序 —— vector + sort（竞赛最常用组合）
// 输入：第一行 n，第二行 n 个整数
// 输出：升序排序，空格分隔
// 例：输入 3 / 3 1 2，输出 1 2 3
#include <bits/stdc++.h>
using namespace std;

int main() {
    int n;
    cin >> n;
    vector<int> a(n);
    for (int i = 0; i < n; i++) cin >> a[i];

    // TODO: 用 sort 排序并输出（空格分隔，末尾换行）

    return 0;
}
""", [
        {"name": "3 1 2", "input": "3\n3 1 2\n", "expected": "1 2 3\n"},
        {"name": "含负数", "input": "4\n10 -2 0 7\n", "expected": "-2 0 7 10\n"},
        {"name": "n=1", "input": "1\n5\n", "expected": "5\n"},
    ]),

    # ---- 校赛真题 ----

    "sc1-1": ("""\
// 校赛真题①：游戏王锦标赛（思维/签到题）
// 题意：n 个玩家排成一行，第 i 和 i+1 名玩家比赛（共 n-1 场）。
//       a[i]=0 表示该玩家没赢过任何比赛；a[i]=1 表示至少赢过一场。
//       若存在"必撒谎"的人（即任何比赛结果都无法同时满足所有报告），输出 YES。
// 输入：第一行 t，每组：n + n 个 a[i]
// 输出：每组一行 YES 或 NO
// 例：输入 3 / 0 1 0 -> NO（2号可连胜1、3号，全部属实）
#include <bits/stdc++.h>
using namespace std;

int main() {
    int t;
    cin >> t;
    while (t--) {
        int n;
        cin >> n;
        vector<int> a(n);
        for (int i = 0; i < n; i++) cin >> a[i];

        // TODO: 判断是否必有人撒谎
        // 提示1：相邻两个 0 -> 他们之间的比赛两人都要输，矛盾
        // 提示2：全部都是 1 -> 1号只打一场必须赢，n号只打一场必须赢，
        //        中间的"胜利链"推到最后一对必然冲突

        cout << "NO" << endl;  // 改这里
    }
    return 0;
}
""", [
        {"name": "官方样例", "input": "6\n3\n0 1 0\n2\n0 0\n2\n1 1\n4\n0 1 1 1\n4\n1 0 0 1\n7\n0 1 0 1 0 1 0\n", "expected": "NO\nYES\nYES\nNO\nYES\nNO\n"},
        {"name": "n=2 全 1", "input": "1\n2\n1 1\n", "expected": "YES\n"},
        {"name": "n=2 单胜", "input": "2\n2\n1 0\n2\n0 1\n", "expected": "NO\nNO\n"},
        {"name": "n=3 全 1", "input": "1\n3\n1 1 1\n", "expected": "YES\n"},
        {"name": "全 1 长链", "input": "1\n5\n1 1 1 1 1\n", "expected": "YES\n"},
        {"name": "左端 1 链", "input": "2\n4\n1 1 1 0\n5\n1 1 1 1 0\n", "expected": "NO\nNO\n"},
        {"name": "中间 0 隔开", "input": "2\n7\n1 1 1 0 1 1 1\n6\n1 0 1 1 0 1\n", "expected": "NO\nNO\n"},
        {"name": "相邻双 0 混合", "input": "2\n8\n1 1 0 0 1 1 1 1\n6\n1 1 1 0 0 1\n", "expected": "YES\nYES\n"},
    ]),

    "sc1-2": ("""\
// 校赛真题②：牛牛卡牌游戏（构造/观察）
// 题意：n 头牛各 m 张牌（0..n*m-1 不重复），每轮按排列 p 依次出牌，
//       所出的牌必须比桌面顶牌大。问能否存在 p 使所有牛出完所有牌。
// 关键观察：整场出的牌必须严格递增 = 0,1,2,...,n*m-1
//           => 第 r 轮第 i 位出的牌 ≡ i-1 (mod n)
//           => 每头牛的牌必须恰好是某个 mod n 剩余类！
// 输出：n 个整数（剩余类 0..n-1 对应的牛），不存在输出 -1
#include <bits/stdc++.h>
using namespace std;

int main() {
    int t;
    cin >> t;
    while (t--) {
        int n, m;
        cin >> n >> m;
        vector<int> owner(n, -1);  // 剩余类 r -> 牛编号
        bool bad = false;

        for (int cow = 1; cow <= n; cow++) {
            int r = -1;
            for (int k = 0; k < m; k++) {
                int x;
                cin >> x;
                if (r == -1) r = x % n;
                if (x % n != r) bad = true;   // 这头牛的牌不属于同一个剩余类
            }
            if (!bad && owner[r] != -1) bad = true;  // 两个牛抢同一个剩余类
            if (!bad) owner[r] = cow;
        }

        if (bad) {
            cout << -1 << '\\n';
            continue;
        }
        for (int r = 0; r < n; r++)
            cout << owner[r] << (r + 1 == n ? '\\n' : ' ');
    }
    return 0;
}
""", [
        {"name": "官方样例1", "input": "1\n2 3\n0 4 2\n1 5 3\n", "expected": "1 2\n"},
        {"name": "官方样例2 单牛", "input": "1\n1 1\n0\n", "expected": "1\n"},
        {"name": "官方样例3 无解", "input": "1\n2 2\n1 2\n0 3\n", "expected": "-1\n"},
        {"name": "官方样例4", "input": "1\n4 1\n1\n2\n0\n3\n", "expected": "3 1 2 4\n"},
        {"name": "三牛正常", "input": "1\n3 2\n0 3\n1 4\n2 5\n", "expected": "1 2 3\n"},
        {"name": "两牛正常", "input": "1\n2 2\n0 2\n1 3\n", "expected": "1 2\n"},
    ]),

    "sc1-3": ("""\
// 校赛真题③：Asuna 的塔楼（奇偶性/思维）
// 题意：操作——选 i!=j，a[i]+a[j] 为奇数且 a[i]>0，则 a[i]-1, a[j]+1。
//       求任意次操作后 max(a) 的最大值。
// 关键观察：操作不改变奇数个数！（源奇->偶、目标偶->奇，或反过来，净变化 0）
// 结论：全同奇偶 -> 无法操作 -> max(a)
//       混合奇偶 -> 答案 = 总和 - (奇数个数 - 1)
#include <bits/stdc++.h>
using namespace std;

int main() {
    int t;
    cin >> t;
    while (t--) {
        int n;
        cin >> n;
        long long sum = 0;
        int odds = 0, mx = 0;
        for (int i = 0; i < n; i++) {
            int x;
            cin >> x;
            sum += x;
            mx = max(mx, x);
            if (x % 2) odds++;
        }
        if (odds == 0 || odds == n) cout << mx << '\\n';
        else cout << sum - (odds - 1) << '\\n';
    }
    return 0;
}
""", [
        {"name": "官方样例1 全奇", "input": "1\n3\n5 3 9\n", "expected": "9\n"},
        {"name": "官方样例2", "input": "1\n2\n3 2\n", "expected": "5\n"},
        {"name": "官方样例3", "input": "1\n4\n1 2 2 1\n", "expected": "5\n"},
        {"name": "官方样例4", "input": "1\n5\n5 4 3 2 9\n", "expected": "21\n"},
        {"name": "双奇双偶", "input": "1\n4\n1 1 2 2\n", "expected": "5\n"},
        {"name": "全偶", "input": "1\n2\n2 2\n", "expected": "2\n"},
        {"name": "全奇 n=3", "input": "1\n3\n1 1 1\n", "expected": "1\n"},
        {"name": "奇多偶少", "input": "1\n4\n1 1 1 2\n", "expected": "3\n"},
    ]),
}


def main():
    lessons = load_lessons()
    created = 0
    for chapter in lessons["chapters"]:
        for lesson in chapter["lessons"]:
            workdir = EXERCISES / lesson["id"]
            workdir.mkdir(parents=True, exist_ok=True)
            lang = lesson.get("language") or chapter.get("language") or "c"
            ext = LANGUAGES[lang]["ext"]

            spec = EXERCISE_SPECS.get(lesson["id"])
            if spec is not None:
                template, tests = spec
            else:
                if lang == "python":
                    template = f"# {lesson['title']}\n# 在这里编写你的 Python 代码\n\n"
                elif lang == "cpp":
                    template = f"// {lesson['title']}\n// 在这里编写你的 C++ 代码\n\n#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {{\n    // TODO\n    return 0;\n}}\n"
                else:
                    template = TEMPLATE.format(title=lesson["title"])
                tests = []

            # template 备份（供"重置模板"恢复），main 是用户当前代码
            (workdir / f"template.{ext}").write_text(template, encoding="utf-8")
            code_file = workdir / f"main.{ext}"
            if not code_file.exists():
                code_file.write_text(template, encoding="utf-8")
                created += 1

            if tests:
                (workdir / "tests.json").write_text(
                    json.dumps(tests, ensure_ascii=False, indent=2), encoding="utf-8"
                )

    print(f"seed 完成：生成 {created} 个 main 模板，{len(EXERCISE_SPECS)} 个课时带测试用例")


if __name__ == "__main__":
    main()
