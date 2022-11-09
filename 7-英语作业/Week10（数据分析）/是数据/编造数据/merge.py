import pandas as pd
import numpy as np

title = ["序号", "所用时间", "1.您所属的年级是？", "2.您的性别", "3.您平时是否玩网络游戏", "4.请问您平时玩什么类型的网络游戏？", "5.您一周内玩网络游戏的频率一般是", "6.您平均每天玩多少个小时网络游戏", "7.您在近一个月以来玩游戏最晚的时间为：", "8.您平均每个月在网络游戏中花费多少钱", "9.您玩网络游戏的目的是什么", "10.如果玩网络游戏的时间和学习冲突，您会", "11.您在游玩网络游戏时的状态，下列哪些描述和您符合？", "12.您认为网络游戏给您带来了什么？", "13.您是否认为网络游戏已经成为您生活中不可或缺的一部分？", "14.您是否会因为游玩游戏而熬夜？", "15.您是否会因为玩游戏而耽误吃饭？", "16.您的学习习惯和下列哪种描述最为符合？", "17.您一周的锻炼频次大约在？", "18.您在临近期末考试时，以下哪种描述和您最为相符？"]
title_quan = ["序号", "所用时间", "1.您所属的年级是？", "2.您的性别", "3.您平时是否玩网络游戏", "5.您一周内玩网络游戏的频率一般是", "6.您平均每天玩多少个小时网络游戏", "7.您在近一个月以来玩游戏最晚的时间为：", "8.您平均每个月在网络游戏中花费多少钱", "10.如果玩网络游戏的时间和学习冲突，您会", "13.您是否认为网络游戏已经成为您生活中不可或缺的一部分？", "14.您是否会因为游玩游戏而熬夜？", "15.您是否会因为玩游戏而耽误吃饭？", "16.您的学习习惯和下列哪种描述最为符合？", "17.您一周的锻炼频次大约在？", "18.您在临近期末考试时，以下哪种描述和您最为相符？"]
title_convert = ["年级", "性别","时长评分","睡眠习惯","虚拟消费", "饮食","锻炼","学习习惯"]
# "时长评分"    5, 6
# "睡眠习惯"    7, 14
# "虚拟消费"    8
# "饮食"        15
# "锻炼"        17
# "学习习惯"    10, 16, 18
src = "编造的量化分析（序号版）.xlsx"
tar = "编造的量化分析（mergeDim）.xlsx"


def process(index, val, dic):
    if index == 1:
        dic["年级"] = val
    elif index == 2:
        dic["性别"] = val
    elif index in [5, 6]:
        dic["时长评分"] += val
    elif index in [7,14]:
        dic["睡眠习惯"] += val
    elif index in [8]:
        dic["虚拟消费"] += val
    elif index in [15]:
        dic["饮食"] += val
    elif index in [17]:
        dic["锻炼"] += val
    elif index in [10, 16, 18]:
        dic["学习习惯"] += val
    return dic        
        
df = pd.read_excel(src)
wbData = []
for row in range(len(df)):
    appendFlag = True
    state = {}
    for title in title_convert:
        state[title] = 0
    for col in df.columns:
        if df[col][row] == "(跳过)":
            appendFlag = False
            break
        lst = col.split(".")
        if len(lst) > 1:
            index = int(lst[0])
            state = process(index, df[col][row], state)
    if appendFlag == True:
        wbSample = []
        for key in title_convert:
            wbSample.append(state[key])
        wbData.append(wbSample)

wbDf = pd.DataFrame(wbData, columns = title_convert)
wbDf.to_excel(tar, index = False)