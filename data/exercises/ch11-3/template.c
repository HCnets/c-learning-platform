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
