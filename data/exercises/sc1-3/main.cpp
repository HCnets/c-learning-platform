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
        if (odds == 0 || odds == n) cout << mx << '\n';
        else cout << sum - (odds - 1) << '\n';
    }
    return 0;
}
