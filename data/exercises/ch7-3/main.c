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
    printf("%d\n", factorial(n));
    return 0;
}
