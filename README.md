This is a Chinese game which is not so common.

## 更新说明

暂无

## 游戏说明

`play-6.0` 是人机对战

`play-5.2.0` 是多人混战，最高和19个电脑一起打

`team-0.1` 是团战，其中 `TA` 和 `You` 为一组，`TB` 为一组。

`data.exe` 是数据，不要运行，需要保证和 `play` 或 `team` 在同一文件夹下

将会增加一些其它技能。

总共有20种操作，分别为：

| 编号 | 名称     | 消耗点数    | 攻击力 | 防御性质                                  | 攻击性质                           |
| ---- | -------- | ----------- | ------ | ----------------------------------------- | ---------------------------------- |
| 0    | 世界末日 | 15          | 15     | 无敌                                      | 无敌                               |
| 1    | 笑波     | 1           | 1      | 能防住除了【反弹】外所有攻击力1以下的武器 |                                    |
| 2    | 电波     | 2           | 2      | 能防住攻击力2以下的武器                   |                                    |
| 3    | 致命     | 3           | 3      | 能防住攻击力3以下的武器                   |                                    |
| 4    | 地波     | 4           | 4      | 能防住攻击力4以下的武器                   |                                    |
| 5    | 骗波     | 5           | 5      | 能防住攻击力5以下的武器                   |                                    |
| 6    | 派波     | 6           | 6      | 能防住攻击力6以下的武器                   |                                    |
| 7    | 气波     | 7           | 7      | 能防住攻击力7以下的武器                   |                                    |
| 8    | 青龙波   | 8           | 8      | 能防住攻击力8以下的武器                   |                                    |
| 9    | 收       | 1           | 0      | 能防住攻击力6或7的武器                    | 无攻击力                           |
| 10   | 金龙波   | 10          | 10     | 能防住除世界末日外所有武器                |                                    |
| 11   | 小防     | 0           | 0      | 能防住攻击力2以下的武器                   | 无攻击力                           |
| 12   | 大防     | 0           | 0      | 能防住攻击力0、3、4、5的武器              | 无攻击力                           |
| 13   | 反弹     | 0           | 0      | 能防住【笑波】、【免单】和无攻击力武器    | 对方出【笑波】或【免单】将反弹伤害 |
| 14   | 吸       | 0           | 0      | 能防住除了【拉】外攻击力5以下的武器       | 无攻击力                           |
| 15   | 拉       | 0           | 0      | 无防御力                                  | 无攻击力                           |
| 16   | 免单     | 0           | 1      | 限用一次，能防住【笑波】和无攻击力武器    |                                    |
| 17   | 结       | -1（得1点） | 0      | 无防御力                                  | 无攻击力                           |
| 18   | 青龙收   | 1           | 0      | 只能防住【青龙波】                        | 无攻击力                           |
| 19   | 金龙收   | 1           | 0      | 只能防住【金龙波】                        | 无攻击力                           |

### 特殊

1. 对于编号1~8和10的武器，如果打到攻击力比自己少1的武器，则对方血量-1，如果打到攻击力相同的武器，则血量不变.如果打到攻击力0且防不住当前武器的，则对方直接死亡
2. 【免单】在面对1~8和10的武器时相当于【笑波】，其他时候攻击只能血量-1
3. 【吸】能获得对方武器消耗点数的点

## 游戏预设

开局时，每人有2血量和2点，当一方血量为0时游戏结束。

