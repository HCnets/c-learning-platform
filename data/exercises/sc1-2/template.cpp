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
            cout << -1 << '\n';
            continue;
        }
        for (int r = 0; r < n; r++)
            cout << owner[r] << (r + 1 == n ? '\n' : ' ');
    }
    return 0;
}
