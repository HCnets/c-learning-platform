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
    printf("%d %d\n", a, b);
    return 0;
}
