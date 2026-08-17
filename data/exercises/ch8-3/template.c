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
