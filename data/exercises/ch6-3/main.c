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

    printf("%d\n", sum);
    return 0;
}
