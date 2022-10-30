'''
定义DataSet类，用于封装数据集，以及进行数据预处理
定义DataClass枚举类，用于定义数据类型
'''

from email import iterators
from typing import Iterator
import numpy as np
from enum import Enum
import random
from logging import warning
from copy import deepcopy

from soupsieve import select

class DataClass(Enum):  # 枚举类，定义数据类型
    value = 1   # 数值数据
    order = 2   # 定序数据
    tag = 3     # 类别数据

class DataSet(object):
    def __init__(self, feature: np.array, label: np.array, title: list = None, dataClassList: list = None, labelConvert = False):
        '''
        传入的feature的dtype为object，允许混合类型传入
        注意dataClassList需要使用DataClass的枚举类
        '''
        self.__feature = feature
        self.__label = label.reshape((len(label),1))        # 送进来直接reshape成二维的了，很糟糕的做法
        self.__title = title
        self.__sample_num, self.__attr_num = feature.data.shape
        if title is None:
            self.__title = ["undefined_" + str(i) for i in range(1, self.__attr_num + 1)]
            warning("未定义属性名，默认为undefined_<index>。")
        self.__orderMapping = None
        self.__tagMapping = None
        self.__isConverted = False
        self.__convertedFeature = None
        self.__convertedTitle = None
        self.__labelMapping = None
        self.__invLabelMapping = None
        self.__isLabelConverted = False
        
        if dataClassList is None:
            warning("未定义数据类型，非字符串数据将被标记为数值数据，字符串类型数据标记为分类数据")
            self.__dataClassList = []
            sample = feature[0]
            for i in sample:
                if type(i) == type("str"):
                    self.__dataClassList.append(DataClass.tag)
                else:
                    self.__dataClassList.append(DataClass.value)
        else:
            self.__dataClassList = dataClassList
            
        if labelConvert == True:
            self.convertLabel()
    
    def __createTempOrderMappingList(self):
        '''
        制造定序数据的mapping，返回格式为dict：{str(title): dict( str(attrName), int(order) ) }
        '''
        mapping = dict()
        for idx, dataType in enumerate(self.__dataClassList):
            if dataType != DataClass.order:
                continue
            s = set()
            for attrVal in self.__feature[:,idx]:
                s.add(attrVal)
            subMapping = dict()
            for orderVal, attrName in enumerate(s):
                subMapping[attrName] = orderVal
            attr = self.__title[idx]
            mapping[attr] = subMapping
        self.__orderMapping = mapping
    
    def __createTagMapping(self):
        '''
        制作分类数据的tagging，返回格式为dict：{str(title): dict {str("attrNewName"): np.array(onehot), ... , str("__info__"): dict{str("length"): int, str("attrTitle"): list(str)} } }
        例：color{red, blue}, weight{thin, fat}，返回为
        {"color":
            {
                "red": [1,0],
                "blue": [0,1],
                "__info__":
                {
                    "length": 2,
                    "newtitle": ["color_red", "color_blue"]
                }
            }
        "weight":
            {
                ...
            }
        }
        
        注意onehot是二维数据
        '''
        ans = dict()
        for attr_idx, dt in enumerate(self.__dataClassList):
            if (dt != DataClass.tag):
                continue
            mapping = dict()
            attrNewTitleList = []
            attrName = self.__title[attr_idx]
            attrValSet = set()
            # 统计取值数量
            for attrVal in self.__feature[:, attr_idx]:
                attrValSet.add(attrVal)
            # 组装mapping
            for i, attrVal in enumerate(attrValSet):        
                onehot = np.zeros((1, len(attrValSet)))
                onehot[0][i] = 1
                attrNewTitle = attrName + '_' + attrVal
                attrNewTitleList.append(attrNewTitle)
                mapping[attrVal] = onehot
            # 组装__info__的mapping
            infoMapping = dict()
            infoMapping ["length"] = len(attrValSet)
            infoMapping ["newtitle"] = attrNewTitleList
            mapping["__info__"] = infoMapping
            ans[attrName] = mapping
        self.__tagMapping = ans
            
    def __convertFeatureByAttr(self, feature: np.array, attrName: str, dtype: DataClass) -> np.array:
        '''
        注意传入的feature必须是一列，不能是多列。
        '''
        if dtype == DataClass.order:
            newFeature = np.zeros((0,1))
            for i in feature:
                attrVal = i[0]
                concatFeature = np.array([self.__orderMapping[attrName][attrVal]]).reshape(1,1)
                newFeature = np.concatenate((newFeature, concatFeature), axis=0)
        elif dtype == DataClass.tag:
            attrNum = self.__tagMapping[attrName]["__info__"]["length"]
            newFeature = np.zeros((0, attrNum))
            for i in feature:
                attrVal = i[0]
                newFeature = np.concatenate((newFeature, self.__tagMapping[attrName][attrVal]), axis=0)
        else:
            newFeature = feature
        return newFeature
        
    def rescaling(self) -> None:
        '''
        Note that convert should be before feature converting
        '''
        for idx, val in enumerate(self.__dataClassList):
            if val == DataClass.value:
                self.__feature[:, idx] = (self.__feature[:, idx] - np.mean(self.__feature[:, idx]))/np.std(self.__feature[:, idx])
                
    def __spawnNewTitle(self) -> None:
        '''
        生成转换后的新标题
        '''
        title = []
        for idx, dt in enumerate(self.__dataClassList):
            if dt != DataClass.tag:
                title.append(self.__title[idx])
            else:
                attrName = self.__title[idx]
                attrNewTitleList = self.__tagMapping[attrName]["__info__"]["newtitle"]
                title = title + attrNewTitleList
        self.__convertedTitle = title
    
    def __shuffleSample(self, is_converted = False):
        randidx = [i for i in range(self.__sample_num)]
        random.shuffle(randidx)
        if is_converted == False:
            self.__feature = self.__feature[randidx,:]
        else:    
            if self.__isConverted == False:
                self.convertFeature()
            self.__convertedFeature = self.convertFeature[randidx,:]
        self.__label = self.__label[randidx,:]
        
    def convertFeature(self, orderMappingDict: dict = None):
        '''
        mappingList是字典的字典，外层字典的键为属性值，内层字典的键为属性取值，值为定序的大小。要求传入定序类数据的映射
        '''
        # 是否转换过
        if self.__isConverted == True:
            return
        self.__isConverted == True
        # 生成mapping
        if orderMappingDict is None:
            self.__createTempOrderMappingList()
        else:
            self.__orderMapping = orderMappingDict
        self.__createTagMapping()
        # 生成标题
        self.__spawnNewTitle()  
        # 生成Feature
        newFeature = np.zeros((self.__sample_num, 0))
        for idx in range(len(self.__title)):
            dt = self.__dataClassList[idx]
            col_feature = self.__feature[:, idx].reshape(self.__sample_num,1)
            attrName = self.__title[idx]
            col_newFeature = self.__convertFeatureByAttr(col_feature, attrName, dt)
            newFeature = np.concatenate((newFeature, col_newFeature), axis=1)
        self.__convertedFeature = newFeature
    
    def getDataIterWithBatch(self, batchsize, is_shuffle = True, is_converted = True):
        '''
        注意返回迭代器的第一维是批次数，第二维是样本索引
        '''
        if self.__isConverted == False and is_converted:
            self.convertFeature()
            warning("数据未转化，执行默认转化方法。请检查定序数据是否存在问题")
        if is_shuffle == True:
            self.__shuffleSample()
        feature = self.__feature if is_converted == False else self.__convertedFeature
        ret_feature = []
        ret_label = []
        st = 0
        while st < self.__sample_num:
            ed = min(st + batchsize, self.__sample_num)
            batchSample = feature[st:ed]
            batchLabel = self.__label[st:ed]
            ret_feature.append(batchSample)
            ret_label.append(batchLabel.reshape(ed - st))
            st += batchsize
        ret_feature = np.array(ret_feature, dtype=object)
        ret_label = np.array(ret_label, dtype=object)
        return zip(ret_feature, ret_label)
        
    def getDataIterWithoutBatch(self, is_shuffle = True, is_converted = True):
        '''
        不分batch，注意返回迭代器的第一维就是样本索引
        '''
        if is_shuffle == True:
            self.__shuffleSample()
        if is_converted == True:
            if self.__isConverted == False:
                self.convertFeature()
                warning("数据未转化，执行默认转化方法。请检查定序数据是否存在问题。")
            return zip(self.__convertedFeature, self.__label.reshape(self.__sample_num))
        else:
            return zip(self.__feature, self.__label.reshape(self.__sample_num))
        
    def getFeatureAndLabel(self, is_converted = True):
        if is_converted == False:
            return self.__feature, self.__label.reshape(self.__sample_num)
        elif self.__isConverted == False:
            self.convertFeature()
        return self.__convertedFeature, self.__label.reshape(self.__sample_num)
        
    def getTitle(self, is_converted = True):
        '''
        返回title
        '''
        if is_converted == True:
            if self.__isConverted == False:
                warning("数据未转化，执行默认转化方法。请检查定序数据是否存在问题。")
                self.convertFeature()
            return self.__convertedTitle
        else:
            return self.__title
        
    def getOrderDataMapping(self):
        '''
        返回定序数据映射
        '''
        return self.__orderMapping
    
    def getTagDataMapping(self):
        '''
        返回分类数据映射
        '''
        return self.__tagMapping
    
    def convertLabel(self):
        '''
        将标签数据映射为数值
        '''
        if self.__isLabelConverted == True:
            warning("标签已转化为数值类型，不再进行转化")
            return
        if type(self.__label[0]) != type("str"):
            warning("标签类型为数值类型，不进行转化")
            return
        self.__labelMapping = {}
        s = set()
        for idx, val in enumerate(self.__label):
            s.add(val)
        # 生成映射
        for idx, val in enumerate(s):
            self.__labelMapping[val] = idx
            self.__invLabelMapping[idx] = val
        # 修改标签
        for idx, val in enumerate(self.__label):
            self.__label[idx] = self.__labelMapping[val]
        self.__isLabelConverted = True
    
    def invConvertLabel(self):
        '''
        标签还原为输入类型
        '''
        if self.__invLabelMapping is None or self.__isLabelConverted == False:
            warning("标签未转化为数值，不进行转化") 
            return
        for idx, val in enumerate(self.__label):
            self.__label[idx] = self.__invLabelMapping[val]
        self.__isLabelConverted = False
    
    def getLabelMapping(self):
        '''
        返回标签映射
        '''
        return self.__labelMapping
    
class DataSpliter(object):
    '''
    作用：分出训练集和测试集
    '''
    @staticmethod
    def __subClassDivision(feature: np.array, label: np.array, trainRatio = 0.7, is_shuffle = True):
        '''
        要求分层抽样
        '''
        tot = len(label)
        train_tot = int(tot * trainRatio)
        test_tot = tot - train_tot
        if is_shuffle == True:
            randIdx = [i for i in range(tot)]
            random.shuffle(randIdx)
            feature = feature[randIdx]
            label = label[randIdx]
        trainFeatureSet = feature[0: train_tot]
        trainLabelSet = label[0: train_tot]
        testFeatureSet = feature[train_tot:]
        testLabelSet = label[train_tot:]
        return trainFeatureSet, trainLabelSet, testFeatureSet, testLabelSet
    
    def __extractArray(lst: list):
        s = set()
        for i, j in lst:
            s.add(j[0])
        ans_feature = []
        ans_label = []
        for l in s:
            subAns = list(filter(lambda x: x[1][0] == l, lst))
            attrNum = subAns[0][0].data.shape[0]
            arrAns = np.zeros((0, attrNum))
            labAns = np.zeros((0, 1))
            for i, j in subAns:
                arrAns = np.concatenate((arrAns, i.reshape(1, attrNum)), axis=0)
                labAns = np.concatenate((labAns, j.reshape(1,1)), axis=0)
            ans_feature.append(arrAns)
            ans_label.append(labAns)
        return ans_feature, ans_label
        
    def trainAndTestSetSpliter_bareData(feature: np.array, label: np.array, trainRatio = 0.7, is_shuffle = True):
        '''
        注意label是二维的，不是一维的
        是分层抽样
        return trainFeatureSet, trainLabelSet, testFeatureSet, testLabelSet
        '''
        sampleNum, attrNum = feature.data.shape
        label = label.reshape(sampleNum, 1)
        lst = [(f, l) for f, l in zip(feature, label)]
        lst.sort(key=lambda x:x[1])
        featureLst, labelLst = DataSpliter.__extractArray(lst)
        tot_trainFeatureSet = np.zeros((0, attrNum))
        tot_trainLabelSet = np.zeros((0, 1))
        tot_testFeatureSet = np.zeros((0, attrNum))
        tot_testLabelSet = np.zeros((0, 1))
        # 分层抽样
        for f, l in zip(featureLst, labelLst):
            trainFeatureSet, trainLabelSet, testFeatureSet, testLabelSet = DataSpliter.__subClassDivision(f, l ,trainRatio, is_shuffle)
            tot_trainFeatureSet = np.concatenate((tot_trainFeatureSet, trainFeatureSet), axis = 0)
            tot_trainLabelSet = np.concatenate((tot_trainLabelSet, trainLabelSet), axis = 0)
            tot_testFeatureSet = np.concatenate((tot_testFeatureSet, testFeatureSet), axis = 0)
            tot_testLabelSet = np.concatenate((tot_testLabelSet, testLabelSet), axis = 0)
        if is_shuffle == True:
            # 训练集
            l = len(tot_trainLabelSet)
            idx = [i for i in range(l)]
            random.shuffle(idx)
            tot_trainFeatureSet = tot_trainFeatureSet[idx]
            tot_trainLabelSet = tot_trainLabelSet[idx].astype(dtype = int)
            # 测试集
            l = len(tot_testLabelSet)
            idx = [i for i in range(l)]
            random.shuffle(idx)
            tot_testLabelSet = tot_testLabelSet[idx].astype(dtype = int)
            tot_testFeatureSet = tot_testFeatureSet[idx]
        trainLabelNum, _ = tot_trainLabelSet.data.shape
        testLabelNum, _ = tot_testLabelSet.data.shape
        return tot_trainFeatureSet, tot_trainLabelSet.reshape(trainLabelNum), tot_testFeatureSet, tot_testLabelSet.reshape(testLabelNum)
    
    @staticmethod
    def trainAndTestSetSpliter_dataIter(data_iter: Iterator, trainRatio = 0.7, is_shuffle = True, isBatchDivided = True):
        '''
        isBatchDivided如果为True,则第一维是batch_idx，否则为feature_idx
        return trainIter, testIter
        注意如果分batch的话，测试集是不分batch的
        '''
        if not isinstance(data_iter, Iterator):
            raise Exception("Wrong data type: data_iter must be iterator!")
        if isBatchDivided == False:         # 第一维为样本
            iter = deepcopy(data_iter)
            feature = np.concatenate(tuple(f.reshape(1, 3) for f, _ in iter), axis=0)
            iter = deepcopy(data_iter)
            label = np.concatenate(tuple(np.array(l).reshape(1,) for _, l in iter), axis = 0)
            trainFeatureSet, trainLabelSet, testFeatureSet, testLabelSet = DataSpliter.trainAndTestSetSpliter_bareData(feature, label, trainRatio, is_shuffle)
            return zip(trainFeatureSet, trainLabelSet), zip(testFeatureSet, testLabelSet)
        else:       # 第一维度为batch
            iter = deepcopy(data_iter)
            for sample, _ in iter:
                break
            batchSize, attrNum = sample.data.shape
            iter = deepcopy(data_iter)
            feature = np.concatenate(tuple(sample for sample, _ in iter), axis=0)
            iter = deepcopy(data_iter)
            label = np.concatenate(tuple(label for _ , label in iter), axis=0)
            trainFeatureSet, trainLabelSet, testFeatureSet, testLabelSet = DataSpliter.trainAndTestSetSpliter_bareData(feature, label, trainRatio, is_shuffle)
            lst_feature = []
            lst_label = []
            st = 0
            # 拼接batch
            while True:
                ed = min(st + batchSize, len(trainLabelSet))
                lst_feature.append(trainFeatureSet[st:ed])
                lst_label.append(trainLabelSet[st:ed])
                st += batchSize
                if st >= len(trainLabelSet):
                    break
            return zip(lst_feature, lst_label), zip(testFeatureSet, testLabelSet)