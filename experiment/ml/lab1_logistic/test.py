import numpy as np
import random
from utils.Data import DataClass, DataSet
import logistic

feature=[["青绿","蜷缩","浊响","清晰","凹陷","硬滑",0.697,0.46],
["乌黑","蜷缩","沉闷","清晰","凹陷","硬滑",0.774,0.376],
["乌黑","蜷缩","浊响","清晰","凹陷","硬滑",0.634,0.264],
["青绿","蜷缩","沉闷","清晰","凹陷","硬滑",0.608,0.318],
["浅白","蜷缩","浊响","清晰","凹陷","硬滑",0.556,0.215],
["青绿","稍蜷","浊响","清晰","稍凹","软粘",0.403,0.237],
["乌黑","稍蜷","浊响","稍糊","稍凹","软粘",0.481,0.149],
["乌黑","稍蜷","浊响","清晰","稍凹","硬滑",0.437,0.211],
["乌黑","稍蜷","沉闷","稍糊","稍凹","硬滑",0.666,0.091],
["青绿","硬挺","清脆","清晰","平坦","软粘",0.243,0.267],
["浅白","硬挺","清脆","模糊","平坦","硬滑",0.245,0.057],
["浅白","蜷缩","浊响","模糊","平坦","软粘",0.343,0.099],
["青绿","稍蜷","浊响","稍糊","凹陷","硬滑",0.639,0.161],
["浅白","稍蜷","沉闷","稍糊","凹陷","硬滑",0.657,0.198],
["乌黑","稍蜷","浊响","清晰","稍凹","软粘",0.36,0.37],
["浅白","蜷缩","浊响","模糊","平坦","硬滑",0.593,0.042],
["青绿","蜷缩","沉闷","稍糊","稍凹","硬滑",0.719,0.103]]
label=[1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0]
feature_title=["色泽","根蒂","敲声","纹理","脐部","触感","密度","含糖率"]

feature = np.array(feature,dtype=object)
label = np.array(label,dtype=object)
feature_title = np.array(feature_title,dtype=object)
dataset = DataSet(feature, label, feature_title)
dataset.convertFeature()
data_iter = dataset.getDataIterWithBatch(batchsize=3, is_shuffle=True,is_converted=True)