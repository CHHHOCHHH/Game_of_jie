#include<bits/stdc++.h>
using namespace std;
#define KO 500
const int jie=17,xf=11,df=12,ft=13,xi=14,la=15,md=16;
const int xb=1,db=2,zm=3,dib=4,pb=5,pib=6,qb=7,qlb=8,jlb=10;
const int sh=9,qls=18,jls=19,sjmr=0;
const int fib[25]={0,1,2,3,5,8, 13,21,34,55,89, 144,233,377,610,987, 1597,2584,4181,6765,10946, 17711,28657,46368};
int cost[25]={15,1,2,3,4,5,6,7,8,1,10,0,0,0,0,0,0,-1,1,1};
int costx[25]={15,1,2,3,4,5,6,7,8,1,10,0,0,0,0,0,0,-1,1,1};
const int biao[21][21]={0, 0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0,0,

						2, 0,1,2,2, 2,2,2,2,0, 2,0,0,2,0, 0,0,0,0,0,0,
						2, 0,0,1,2, 2,2,2,2,0, 2,0,0,0,0, 0,0,0,0,0,0,
						2, 0,0,0,1, 2,2,2,2,0, 2,0,0,0,0, 0,0,0,0,0,0,
						2, 0,0,0,0, 1,2,2,2,0, 2,0,0,0,0, 0,0,0,0,0,0,
						2, 0,0,0,0, 0,1,2,2,0, 2,0,0,0,0, 0,0,0,0,0,0,
						
						2, 0,0,0,0, 0,0,1,2,0, 2,0,0,0,0, 0,0,0,0,0,0,
						2, 0,0,0,0, 0,0,0,1,0, 2,0,0,0,0, 0,0,0,0,0,0,
						2, 0,0,0,0, 0,0,0,0,0, 2,0,0,0,0, 0,0,0,0,0,0,
						2, 2,2,2,2, 2,0,0,2,0, 2,0,0,0,0, 0,0,0,0,0,0,
						2, 0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0,0,
						
						2, 0,0,2,2, 2,2,2,2,0, 2,0,0,0,0, 0,0,0,0,0,0,
						2, 2,2,0,0, 0,2,2,2,0, 2,0,0,0,0, 0,1,0,0,0,0,
						2, 0,2,2,2, 2,2,2,2,0, 2,0,0,0,0, 0,0,0,0,0,0,
						2, 0,0,0,0, 0,2,2,2,0, 2,0,0,0,0, 2,0,0,0,0,0,
						2, 2,2,2,2, 2,2,2,2,0, 2,0,0,0,0, 0,1,0,0,0,0,
						
						2, 0,1,2,2, 2,2,2,2,0, 2,0,0,1,0, 0,0,0,0,0,0,
						2, 2,2,2,2, 2,2,2,2,0, 2,0,0,0,0, 0,1,0,0,0,0,
						2, 2,2,2,2, 2,2,2,0,0, 2,0,0,0,0, 0,1,0,0,0,0,
						2, 2,2,2,2, 2,2,2,2,0, 0,0,0,0,0, 0,1,0,0,0,0,
						2, 2,2,2,2, 2,2,2,2,0, 2,0,0,0,0, 0,1,0,0,0,0
};//biao[x][y]: A use x B use y A lose blood? 
struct tt{
	int num;
	double p;
	bool operator <(const tt& pp) const{
		return p>pp.p;
	}
}tmp[33];
char s[21][20]={"[世界末日 -15]","[笑波 -1]","[电波 -2]","[致命 -3]","[地波 -4]","[骗波 -5]","[派波 -6]","[气波 -7]","[青龙波 -8]","[收 -1]","[金龙波 -10]","[小防 0]","[大防 0]","[反弹 0]","[吸 0]","[拉 0]","[免单 0]","[结 +1]","[青龙收 -1]","[金龙收 -1]","Dead"};
bool typp[20]={1, 1,1,1,1,1, 1,1,1,0,1, 0,0,0,0,0, 1,0,0,0};
int bld[25];
int pt[25];
bool use_md[25];
bool zb=0;
bool dd[25];
int win[30][30][20],lose[30][30][20];
double pc[30][30][20];
int KKK=0;
struct kkksc03{
	int num;
	int id;
	bool operator <(const kkksc03& pp) const{
		return num>pp.num;
	}
}tttmp[33];
struct node{
	int ptx,pty,yy;
}ttt[505];
int qq=0;
int a[30],cnt;
double mn;
int sum[21];
int cc1[25],cc2[25];
int n;
void lose_blood(int xx,int yy,int x,int y)
{
//	bld[xx]-=x;
	bld[yy]-=y;
	if(cc1[yy]==ft&&cc1[xx]==xb) bld[xx]-=2;
	if(cc1[yy]==ft&&cc1[xx]==md) bld[xx]-=1;
//	if(bld[xx]<=0) return -1;
//	if(bld[yy]<=0) return 1;
//	return 0;
}
void check(int xx,int yy,int x,int y)//x win 1  y win -1
{
	if(y==20) printf("%d 用 %s 攻击 %d，%d 向别人进攻\n",xx,s[x],yy,yy);
	else printf("%d 用 %s 攻击 %d，%d 出 %s\n",xx,s[x],yy,yy,s[y]);
	if(y==xi&&(x>=1&&x<=5)) pt[yy]+=x;
	if(y==20)
	{
		bld[yy]-=biao[20][x];
		return;
	}
	lose_blood(xx,yy,biao[x][y],biao[y][x]);
}
void p_lose_blood(int x,int y,int tmp)
{
	bld[x]-=x;
	bld[y]-=y;
	if(bld[x]<=0) sum[tmp]+=KO;
	if(bld[y]<=0) sum[tmp]-=KO;
	bld[x]+=x;
	bld[y]+=y;
}
void p_check(int x,int y,int tmp)//x win 1  y win -1
{
	if(x==xi&&(y>=1&&y<=5)) sum[tmp]-=y;
	if(y==xi&&(x>=1&&x<=5)) sum[tmp]+=x;
	p_lose_blood(biao[x][y],biao[y][x],tmp);
}
int cp_choose1(int num,int to)
{
	memset(sum,-1,sizeof(sum));
	for(int i=0;i<=19;i++)
	{
		if(cost[i]>pt[num]) continue;
		sum[i]=10000;
		for(int j=0;j<=19;j++)
		{
			if(cost[j]>pt[to]) continue;
			sum[i]=sum[i]+cost[j]-cost[i];
			p_check(j,i,i);
		}
		tttmp[i].num=sum[i];
		tttmp[i].id=i;
	}
	sort(tttmp,tttmp+20);
	int cnt=23;
	for(int i=1;i<=7;i++)  a[i]=tttmp[1].id;
	for(int i=8;i<=12;i++)  a[i]=tttmp[2].id;
	for(int i=13;i<=16;i++)  a[i]=tttmp[3].id;
	for(int i=17;i<=19;i++)  a[i]=tttmp[4].id;
	for(int i=20;i<=21;i++)  a[i]=tttmp[5].id;
	a[22]=17;
	a[23]=tttmp[6].id;
	int www;
	while(1)
	{
		www=rand()%20;
		int yy=a[www];
		if(cost[yy]>pt[num]) continue;
		if(use_md[num]&&yy==md) continue;
		/*if(ptx<=5&&yy==sh) continue;
		if(ptx<=7&&yy==qls) continue;
		if(ptx<=9&&yy==jls) continue;
		if(ptx<=2&&yy==df) continue;
		if(pty==0&&yy==la) continue;*/
		if(cost[yy]<=pt[num])
		{
			pt[num]-=cost[yy];
			return yy;
		}
	}
}
void down_load()
{
//	printf("正在加载...\n");
	ifstream ff;
	ff.open("data.exe");
	int ta,tb,tc;
//	fclose(stdin);
//	system("pause");
//	system("pause");
	for(int i=0;i<=25;i++)
	{
		for(int j=0;j<=25;j++)
		{
			for(int k=0;k<=19;k++)
			{
				ff>>win[i][j][k]>>lose[i][j][k]>>pc[i][j][k];
			}
		}
	}
	/*for(int i=0;i<=25;i++)
	{
		for(int j=0;j<=25;j++)
		{
			for(int k=0;k<=19;k++)
			{
				printf("%d %d %lf\n",win[i][j][k],lose[i][j][k],pc[i][j][k]);
			}
		}
	}*/
//	fclose(stdin);
	ff.close();
//	printf("加载完毕！\n");
}
int cp_choose2(int num,int to)
{
	for(int i=0;i<=19;i++)
	{
		if(i==md&&use_md[num]) continue;
		if(cost[i]>pt[num]) continue;
		tmp[i].p=pc[pt[num]][pt[to]][i];
		tmp[i].num=i;
	}
	sort(tmp,tmp+20);
	cnt=23;
	for(int i=1;i<=7;i++)  a[i]=tmp[1].num;
	for(int i=8;i<=12;i++)  a[i]=tmp[2].num;
	for(int i=13;i<=16;i++)  a[i]=tmp[3].num;
	for(int i=17;i<=19;i++)  a[i]=tmp[4].num;
	for(int i=20;i<=21;i++)  a[i]=tmp[5].num;
	a[22]=17;
	a[23]=tmp[6].num;
	int www,yy;
	while(1)
	{
		www=rand()%cnt+1;
		yy=a[www];
		if(cost[yy]>pt[num]) continue;
		if(pt[num]<=5&&yy==sh) continue;
		if(pt[num]<=7&&yy==qls) continue;
		if(pt[num]<=9&&yy==jls) continue;
		if(pt[num]<=2&&yy==df) continue;
		if(pt[to]==0&&yy==la) continue;
		if(cost[yy]<=pt[num])
		{
			pt[num]-=cost[yy];
			break;
		}
	}
	return yy;
}
void play()
{
	for(int i=0;i<n;i++)
	{
		if(bld[i]<=0) dd[i]=1;
	}
	int xx,yy;
	int ccc=0;
	printf("Player: 血量  点数  是否使用免单  选择\n");
	printf("You:    %d/2  %2d        %d\n",bld[0],pt[0],use_md[0]);
	for(int i=1;i<n;i++)
	{
		if(bld[i]<=0) 
		{
			if(i<n/2) printf("TA%02d: Dead\n",i);
			else printf("TB%02d: Dead\n",i);
		}
		else
		{
			if(i<n/2) printf("TA%02d:   %d/2  %2d        %d\n",i,bld[i],pt[i],use_md[i]);
			else 
			{
				ccc++;
				printf("TB%02d:   %d/2  %2d        %d\n",i,bld[i],pt[i],use_md[i]);
			}
			
		}
	}
	printf("对方剩余人数：%d\n",ccc);
	if(ccc<=0)
	{
		printf("You win!!!\n");
		system("pause");
		exit(0);
	}
	for(int i=1;i<n;i++)
	{
		if(bld[i]<=0)
		{
			cc1[i]=20;
			cc2[i]=0;
			continue;
		}
		int tttt;
		while(1)
		{
			tttt=rand()%(n/2);
			if(i<n/2) tttt+=n/2;
			if(tttt==i) continue;
			if(bld[tttt]>0) break;
		}
		cc2[i]=tttt;
		cc1[i]=cp_choose2(i,cc2[i]);
		if(cc1[i]==md) use_md[i]=1;
 	}
	printf("请你选择：\n");
	for(int i=0;i<=19;i++)
		if(costx[i]<=pt[0]) printf("%d: %s\n",i,s[i]);
	while(1)
	{
		scanf("%d",&cc1[0]);
		if(cc1[0]>=20||cc1[0]<0)
			printf("无效！请重选\n");
		else
		{
			if(costx[cc1[0]]>pt[0])
			{
				printf("你的点数不足，无法使用 %s\n",s[cc1[0]]);
			}
			else
			{
				if(cc1[0]==md&&use_md[0])
				{
					printf("你已使用过 [免单 0]，不能重复使用\n");
				}
				else break;
			}
		}
	}
	if(typp[cc1[0]])
	{
		printf("请你选择攻击对象：（一个正整数，表示CP编号）\n");
		scanf("%d",&cc2[0]);
	}
	else cc2[0]=0;
	pt[0]-=cost[cc1[0]];
	if(cc1[0]==md) use_md[0]=1;
	bool tmp1=0;
	for(int i=0;i<n;i++)
	{
		if(bld[i]>0 && cc1[i]==la)
		{
			tmp1=1;
			break;
		}
	}
	if(tmp1)
	{
		for(int i=0;i<=n;i++)
		{
			if(cc1[i]==xi)
			{
				bld[i]-=2;
				if(i==0) printf("0 ");
				else printf("%d ",i);
				printf("被 [拉 0] 攻击\n");
				if(cc1[0]==la) KKK++;
			}

		}
	}
	for(int i=0;i<n;i++)
	{
		if(cc2[i]==-1||!typp[cc1[i]]) continue;
		if(!typp[cc1[cc2[i]]] || cc2[cc2[i]]==i) check(i,cc2[i],cc1[i],cc1[cc2[i]]);
		else check(i,cc2[i],cc1[i],20);
	}
	if(typp[cc1[0]])
		if(bld[cc2[0]]<=0) KKK++;
	printf("Player: 血量  点数  是否使用免单  选择\n");
	printf("You:    %d/2  %2d        %d        %s",bld[0],pt[0],use_md[0],s[cc1[0]]);
	if(typp[cc1[0]]) printf(" To %d\n",cc2[0]);
	else printf("\n");
	for(int i=1;i<n;i++)
	{
		if(dd[i])
		{
			if(i<n/2) printf("TA%02d: Dead\n",i);
			else printf("TB%02d: Dead\n",i);
			continue;
		}
		else 
		{
			if(i<n/2) printf("TA%02d:   %d/2  %2d        %d        %s",i,bld[i],pt[i],use_md[i],s[cc1[i]],cc2[i]);
			else printf("TB%02d:   %d/2  %2d        %d        %s",i,bld[i],pt[i],use_md[i],s[cc1[i]],cc2[i]);
		}
		if(typp[cc1[i]]) printf(" To %d\n",cc2[i]);
		else printf("\n");
	}
	
/*	yy=cp_choose();
	
	
//	if(zb) printf("电脑选择 %s\n",s[yy]);
	
	if(xx==114514)
	{
		printf("作弊模式开始！\n");
		zb=1;
		return;
	}
	if(costx[xx]>ptx||xx<0||xx>19)
	{
		printf("你自爆了。\n");
		system("pause");
		exit(0);
	}
	mn=-0.1;
	
	ttt[++qq]=node{ptx,pty,yy};
	printf("你选择了 %s, 电脑选择了 %s\n",s[xx],s[yy]);
	ptx-=costx[xx];
	pty-=costy[yy];
	if(xx==16) costx[16]=100000000;
	if(yy==16) costy[16]=100000000;
	int ggg=check(xx,yy);
	if(ggg==1)
	{
		printf("You Win!!!");
		system("pause");
		exit(0);
	}
	if(ggg==-1)
	{
		printf("You lose!!!");
		system("pause");
		exit(0);
	}
	if(ptx>=25)
	{
		printf("你已达点数上限：25\n");
		ptx=25; 
	}
	if(pty>=25)
	{
		printf("电脑已达点数上限：25\n");
		pty=25; 
	}*/
	if(bld[0]<=0)
	{
		printf("You lose!!\n");
		system("pause");
		exit(0);
	}
	system("pause");
	system("cls");
}
void init()
{
	down_load();
	for(int i=0;i<n;i++)
	{
		pt[i]=2;
		use_md[i]=0;
		bld[i]=2;
	}
}
int main()
{ 
	srand(time(0));
//	int ta;
	printf("请输入一个团队的人数：\n");
	scanf("%d",&n);
	while(n>10||n<1)
	{
		printf("人数不得超过10，且最低为1\n");
		scanf("%d",&n);
	}
	n*=2;
//	printf("提示：输入114514进入作弊模式！\n");
//	system("pause");
	system("cls");
	init();
	while(1) play();
	return 0;
}

