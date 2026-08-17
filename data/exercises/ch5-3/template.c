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
        printf("Yes\n");
    else
        printf("No\n");

    return 0;
}
