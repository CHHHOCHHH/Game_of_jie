#include<bits/stdc++.h>
using namespace std;
const int jie=17,xf=11,df=12,ft=13,xi=14,la=15,md=16;
const int xb=1,db=2,zm=3,dib=4,pb=5,pib=6,qb=7,qlb=8,jlb=10;
const int sh=9,qls=18,jls=19,sjmr=0;
int costx[25]={15,1,2,3,4,5,6,7,8,1,10,0,0,0,0,0,0,-1,1,1};
int costy[25]={15,1,2,3,4,5,6,7,8,1,10,0,0,0,0,0,0,-1,1,1};
const int biao[20][20]={0, 0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0,

						2, 0,1,2,2, 2,2,2,2,0, 2,0,0,2,0, 0,0,0,0,0,
						2, 0,0,1,2, 2,2,2,2,0, 2,0,0,0,0, 0,0,0,0,0,
						2, 0,0,0,1, 2,2,2,2,0, 2,0,0,0,0, 0,0,0,0,0,
						2, 0,0,0,0, 1,2,2,2,0, 2,0,0,0,0, 0,0,0,0,0, 
						2, 0,0,0,0, 0,1,2,2,0, 2,0,0,0,0, 0,0,0,0,0,
						
						2, 0,0,0,0, 0,0,1,2,0, 2,0,0,0,0, 0,0,0,0,0,
						2, 0,0,0,0, 0,0,0,1,0, 2,0,0,0,0, 0,0,0,0,0,
						2, 0,0,0,0, 0,0,0,0,0, 2,0,0,0,0, 0,0,0,0,0,
						2, 2,2,2,2, 2,0,0,2,0, 2,0,0,0,0, 0,0,0,0,0,
						2, 0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0,
						
						2, 0,0,2,2, 2,2,2,2,0, 2,0,0,0,0, 0,0,0,0,0,
						2, 2,2,0,0, 0,2,2,2,0, 2,0,0,0,0, 0,1,0,0,0,
						2, 0,2,2,2, 2,2,2,2,0, 2,0,0,0,0, 0,0,0,0,0,
						2, 0,0,0,0, 0,2,2,2,0, 2,0,0,0,0, 2,0,0,0,0,
						2, 2,2,2,2, 2,2,2,2,0, 2,0,0,0,0, 0,1,0,0,0,
						
						2, 0,1,2,2, 2,2,2,2,0, 2,0,0,1,0, 0,0,0,0,0,
						2, 2,2,2,2, 2,2,2,2,0, 2,0,0,0,0, 0,1,0,0,0,
						2, 2,2,2,2, 2,2,2,0,0, 2,0,0,0,0, 0,1,0,0,0,
						2, 2,2,2,2, 2,2,2,2,0, 0,0,0,0,0, 0,1,0,0,0,
						
};//biao[x][y]: A use x B use y A lose blood? 
char s[20][15]={"[世界末日 -15]","[笑波 -1]","[电波 -2]","[致命 -3]","[地波 -4]","[骗波 -5]","[派波 -6]","[气波 -7]","[青龙波 -8]","[收 -1]","[金龙波 -10]","[小防 0]","[大防 0]","[反弹 0]","[吸 0]","[拉 0]","[免单 0]","[结 +1]","[青龙收 -1]","[金龙收 -1]"};
int bldx=2,bldy=2;
int ptx=2,pty=2;
bool usex_md=0,usey_md=0;
int lose_blood(int x,int y)
{
	bldx-=x;
	bldy-=y;
	if(bldx<=0) return -1;
	if(bldy<=0) return 1;
	return 0;
}
int check(int x,int y)//x win 1  y win -1
{
	if(x==xi&&(y>=1&&y<=5)) ptx+=y;
	if(y==xi&&(x>=1&&x<=5)) pty+=x;
	return lose_blood(biao[x][y],biao[y][x]);
}
bool zuobi=0;
void play()
{
	printf("你的血量：%d/2 电脑血量：%d/2\n",bldx,bldy);
	printf("你的点数：%d 电脑点数：%d\n",ptx,pty);
	printf("请你选择：\n");
	for(int i=0;i<=19;i++)
		if(costx[i]<=ptx) printf("%d: %s\n",i,s[i]);
	int xx,yy;
	srand(time(0));
	while(1)
	{
		yy=rand()%20;
//		printf("yy=%d\n",yy);
		if(costy[yy]>pty) continue;
		if(ptx<=5&&yy==sh) continue;
		if(ptx<=7&&yy==qls) continue;
		if(ptx<=9&&yy==jls) continue;
		if(ptx<=2&&yy==df) continue;
		if(pty==0&&yy==la) continue;
		if((ptx==0&&costx[md])&&yy==xi) continue;
		if((ptx==0&&costx[md])&&yy==ft) continue;
		if((ptx==0&&costx[md])&&yy==xf) continue;
		if(costy[yy]<=pty) break;
	}
	if(pty>=15) yy=0;
	if(zuobi) printf("电脑：%s\n",s[yy]);
	scanf("%d",&xx);
	if(xx==1919810)
	{
		zuobi=1;
		printf("已开启作弊模式\n");
		return;
	}
	if(xx<0||xx>19||costx[xx]>ptx)
	{
		printf("你自爆了。\n");
		system("pause");
		exit(0);
	}
	
	printf("你选择了 %s, 电脑选择了 %s\n",s[xx],s[yy]);
	ptx-=costx[xx];
	pty-=costy[yy];
	if(xx==16) costx[16]=100000000;
	if(yy==16) costy[16]=100000000;
	int tmp=check(xx,yy);
	if(tmp==1)
	{
		printf("You Win!!!");
		system("pause");
		exit(0);
	}
	if(tmp==-1)
	{
		printf("You Lose!!!");
		system("pause");
		exit(0);
	}
}
int main()
{ 
	srand(time(0));
	printf("输入1919810进入作弊模式\n");
	system("pause");
	while(1) play();
	return 0;
}

