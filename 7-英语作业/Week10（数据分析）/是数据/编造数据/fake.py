import pandas as pd
import numpy as np

title = ["序号", "所用时间", "1.您所属的年级是？", "2.您的性别", "3.您平时是否玩网络游戏", "4.请问您平时玩什么类型的网络游戏？", "5.您一周内玩网络游戏的频率一般是", "6.您平均每天玩多少个小时网络游戏", "7.您在近一个月以来玩游戏最晚的时间为：", "8.您平均每个月在网络游戏中花费多少钱", "9.您玩网络游戏的目的是什么", "10.如果玩网络游戏的时间和学习冲突，您会", "11.您在游玩网络游戏时的状态，下列哪些描述和您符合？", "12.您认为网络游戏给您带来了什么？", "13.您是否认为网络游戏已经成为您生活中不可或缺的一部分？", "14.您是否会因为游玩游戏而熬夜？", "15.您是否会因为玩游戏而耽误吃饭？", "16.您的学习习惯和下列哪种描述最为符合？", "17.您一周的锻炼频次大约在？", "18.您在临近期末考试时，以下哪种描述和您最为相符？"]
title_quan = ["序号", "所用时间", "1.您所属的年级是？", "2.您的性别", "3.您平时是否玩网络游戏", "5.您一周内玩网络游戏的频率一般是", "6.您平均每天玩多少个小时网络游戏", "7.您在近一个月以来玩游戏最晚的时间为：", "8.您平均每个月在网络游戏中花费多少钱", "10.如果玩网络游戏的时间和学习冲突，您会", "13.您是否认为网络游戏已经成为您生活中不可或缺的一部分？", "14.您是否会因为游玩游戏而熬夜？", "15.您是否会因为玩游戏而耽误吃饭？", "16.您的学习习惯和下列哪种描述最为符合？", "17.您一周的锻炼频次大约在？", "18.您在临近期末考试时，以下哪种描述和您最为相符？"]
src = "编造的量化分析（剔除问卷后并改性别后）.xlsx"
tar = "编造的量化分析（序号版）.xlsx"

def getMapping(index):
    if index == 1:
        mapping_grade = {"大一":1,"大二":2,"大三":3,"大四":4}
        return mapping_grade
    if index == 2:
        mapping_gender = {"男":0,"女":1}
        return mapping_gender
    elif index == 5:
        mapping_freq_week = {"几乎每天玩":1 ,"两三天玩一次":2 ,"一周玩一次":3 ,"很少玩":4}
        return mapping_freq_week
    elif index == 6:
        mapping_freq_day = {"一个小时以下":4,"一到三个小时":3,"三到六个小时":2,"六个小时以上": 1}
        return mapping_freq_day
    elif index == 7:
        mapping_staytime = {"晚上九点前": 5,"晚上十二点前": 4,"凌晨一点前": 3,"凌晨三点前": 2,"通宵":1}
        return mapping_staytime
    elif index == 8:
        mapping_cost = {"50-100元":1 ,"100-200元":2 ,"200-500元":3 ,"500元以上":4 ,"从不花钱":5}
        return mapping_cost
    elif index == 10:
        mapping_freq_collison = {"专心学习，网络游戏可以暂时不玩":4 ,"以学习为主，空闲时间玩网络游戏": 3,"以网络游戏为主，玩累了再去学习": 2,"专心玩网络游戏，不学习":1}
        return mapping_freq_collison
    elif index == 13:
        mapping_necessary = {"非常符合": 1,"符合": 2,"不符合": 3,"非常不符合":4}
        return mapping_necessary
    elif index == 14:
        mapping_stayup = {"非常符合": 1,"符合": 2,"不符合": 3,"非常不符合":4}
        return mapping_stayup
    elif index == 15:
        mapping_diet = {"非常符合": 1,"符合": 2,"不符合": 3,"非常不符合":4}
        return mapping_diet
    elif index == 16:
        mapping_review = {"平时不怎么学习，等到期末考试时进行突击": 1, "平时也认真学习，考试前保持平时的节奏": 5}
        return mapping_review
    elif index == 17:
        mapping_exercise = {"从不锻炼": 1,"一周1-2次": 2,"一周3-5次": 3,"一周7次": 4,"7次以上": 5}
        return mapping_exercise
    elif index == 18:
        mapping_review_2 = {"考试要紧，先通过考试，考试周少打游戏":3, "平时学得够扎实了，该学学，该玩玩":5, "反正考不过了，先玩了再说，等补考的时候再好好学习": 1}
        return mapping_review_2
    else:
        return dict()
    
def convert(index, val):
    mapping = getMapping(index)
    try:
        ans = mapping[val]
    except Exception as e:
        ans = val
    return ans



df = pd.read_excel(src)
wbData = []
for row in range(len(df)):
    wbSample = []
    appendFlag = True
    for col in df.columns:
        lst = col.split(".")
        if len(lst) > 1:
            index = int(lst[0])
            wbSample.append(convert(index, df[col][row]))
        else:
            wbSample.append(df[col][row])
        if df[col][row] == "(跳过)":
            appendFlag = False
            break
    if appendFlag == True:
        wbData.append(wbSample)

wbDf = pd.DataFrame(wbData, columns = title_quan)
wbDf.to_excel(tar, index = False)