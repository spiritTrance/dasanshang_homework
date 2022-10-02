from math import log
import copy
from statistics import mode

from matplotlib.dates import DAILY

class DataWrapperAndProcessor:
    def __init__(self,feature,label,feature_title) -> None:
        self.DATA=copy.deepcopy(feature)
        self.LABEL=copy.deepcopy(label)
        self.TITLE=copy.deepcopy(feature_title)
        self.__continousValueProcess()
    
    def entropy(self, dataIdx: list):
        mapping=self.getClassMapping(dataIdx)
        ans = 0
        tot = len(dataIdx)
        for key , val in mapping.items():
            ans += -val / tot * log (val / tot)
        return ans
    
    def entropy_gain(self, dataIdx: list, subsetDataIdx: list):
        totEnt = self.entropy(dataIdx)
        for subIdx in subsetDataIdx:
            totEnt -= len(subIdx) / len(dataIdx) * self.entropy(subIdx)
        return totEnt
    
    def gini(self, dataIdx: list):
        mapping=self.getClassMapping(dataIdx)
        ans = 1
        for key, val in mapping.items():
            ans -= (val / len(dataIdx)) ** 2
        return ans
    
    def gini_ratio(self, dataIdx: list, subsetDataIdx: list):
        gini_tot = 0
        for subIdx in subsetDataIdx:
            gini_tot += self.gini(subIdx) * len(subIdx) / len(dataIdx)
        return gini_tot
    
    def getMaximumClassAndNum(self, dataIdx: list):
        mapping=self.getClassMapping(dataIdx)
        maxVal , label = 0, ""
        for key, val in mapping.items():
            if (val > maxVal):
                label = key
                maxVal = val
        if (label==""):
            return "", 0
        return label, mapping[label]        
    
    def getClassMapping(self, dataIdx: list):       # the class count
        mapping=dict()
        for idx in dataIdx:
            label = self.LABEL[idx]
            mapping[label] = 1 if mapping.get(label) is None else mapping[label] + 1
        return mapping
    
    def getAttrMapping(self, attrIdx: int, dataIdx: list):        # the attr index list
        mapping=dict()
        for idx in dataIdx:
            attrVal = self.DATA[idx][attrIdx]
            mapping[attrVal]=[idx] if mapping.get(attrVal) is None else mapping[attrVal]+[idx]
        return mapping
    
    def __continousValueProcess(self):
        sample = self.DATA[0]
        for idx, val in enumerate(sample):
            if (type(val)==type("str")):
                continue
            else:
                valList = [(self.DATA[i][idx] , i) for i in range(len(self.DATA))]
                valList.sort(key = lambda x : x[0])
                dataIdx = [i for i in range(len(self.DATA))]
                maxentropy_gain = -1
                bestSplit = 0.0
                for i in range(len(valList)-1):             #binary to get the best split point
                    splitPoint = (valList[i][0] + valList[i+1][0]) / 2
                    subListLeft = []
                    subListRight = []
                    for ele in valList:         # create binary subset of data
                        value, index = ele
                        if (value <= splitPoint):
                            subListLeft.append(index)
                        else:
                            subListRight.append(index)
                    entropy_gainVal=self.entropy_gain(dataIdx, [subListLeft,subListRight])
                    if (maxentropy_gain < entropy_gainVal):
                        maxentropy_gain = entropy_gainVal
                        bestSplit = splitPoint
                for sample in self.DATA:
                    val = sample[idx]
                    if (val<=bestSplit):
                        sample[idx] = "<="+str(bestSplit)
                    else:
                        sample[idx] = ">"+str(bestSplit)

class TreeNode:
    def __init__(self , treeDataPraser: DataWrapperAndProcessor, validDataIdx : list = [] ,validAttrIdx : list = []) -> None:
        self.son=[]
        self.criteria=None          # branch tag
        self.criteriaBranch=[]      # branch list corresponding to son
        self.category=None          # class tag in every node
        self.validDataIndex=validDataIdx
        self.validAttrIndex=validAttrIdx
        self.dataParser = treeDataPraser
    
    def isLeaf(self):
        return (len(self.son)==0)

    def nodeSplit(self, optLoss = "entropy"):
        self.category , tot_right_fa= self.dataParser.getMaximumClassAndNum(self.validDataIndex)
        if (tot_right_fa==len(self.validDataIndex) or len(self.validAttrIndex)==0):      # same category or no feature
            return
        bestAttrIdx, maxVal = 0 , 0
        for attrIdx in self.validAttrIndex:
            attrMapping = self.dataParser.getAttrMapping(attrIdx, self.validDataIndex)
            subsetIndex = [lst for _ , lst in attrMapping.items()]
            if (optLoss == "gini"):         # maximunize the value in order to judge
                lossVal = 1 / (self.dataParser.gini_ratio(self.validDataIndex, subsetIndex) + 1e-7)
            else:
                lossVal = self.dataParser.entropy_gain(self.validDataIndex,subsetIndex)
            if (maxVal < lossVal):
                maxVal = lossVal
                bestAttrIdx = attrIdx
        # update this node's result
        self.criteria = self.dataParser.TITLE[bestAttrIdx]
        attrMapping = self.dataParser.getAttrMapping(bestAttrIdx, self.validDataIndex)
        tot_right_sub = 0
        for attrVal, subsetIdx in attrMapping.items():  #spawn son node
            attrIdxList = copy.deepcopy(self.validAttrIndex)
            attrIdxList.remove(bestAttrIdx)
            node = TreeNode(self.dataParser, subsetIdx, attrIdxList)
            node.category , num = self.dataParser.getMaximumClassAndNum(subsetIdx)
            # print(num)
            tot_right_sub += num
            self.son.append(node)
            self.criteriaBranch.append(attrVal)
    
class DecisionTree:
    def __init__(self,dataPraser: DataWrapperAndProcessor):
        self.dataPraser=dataPraser
        self.root=TreeNode(self.dataPraser,[i for i in range(len(dataPraser.DATA))],[i for i in range(len(dataPraser.TITLE))])
        
    def buildTree(self, node: TreeNode, optLoss="entropy"):
        node.nodeSplit(optLoss=optLoss)
        for son in node.son:
            self.buildTree(son, optLoss)
    
    def post_prun(self, node: TreeNode, dataPraser: DataWrapperAndProcessor):
        if (node.isLeaf()==True):
            attr, tot_right = dataPraser.getMaximumClassAndNum(node.validDataIndex)
            if (attr == node.category):
                return tot_right
            else: 
                return 0
        tot_right_son = 0
        for son in node.son:
            tot_right_son += self.post_prun(son,dataPraser)
        attr, tot_right_fa = dataPraser.getMaximumClassAndNum(node.validDataIndex)
        print(tot_right_fa,tot_right_son,node.criteriaBranch,node.criteria)
        if (tot_right_fa >= tot_right_son):
            node.son = []
            return tot_right_fa
        return tot_right_son

    def pre_prun(self, node: TreeNode, dataPraser: DataWrapperAndProcessor):
        if (node.isLeaf()==True):
            attr, tot_right = dataPraser.getMaximumClassAndNum(node.validDataIndex)
            if (attr == node.category):
                return tot_right
            else: 
                return 0
        tot_right_son = 0
        for son in node.son:
            attr , num = dataPraser.getMaximumClassAndNum(son.validDataIndex)
            tot_right_son += num
        attr, tot_right_fa = dataPraser.getMaximumClassAndNum(node.validDataIndex)
        if (tot_right_fa >= tot_right_son):
            # print(node.criteriaBranch,node.criteria)
            node.son = []
        for son in node.son:
            self.pre_prun(son, dataPraser)
        return tot_right_son
    
    def printTree(self,node: TreeNode, layer = 1, seq = 1):
        if (node.isLeaf()==True):
            print("第 {} 层，第 {} 个【叶子】的信息：\n\t分类类别：{}".format(layer, seq, node.category))
        else:
            print("第 {} 层，第 {} 个【节点】的信息：\n\t分类属性：{}\n\t子节点分支内容：{}\n\t子节点所含样本：{}\n\t分类类别：{}".format(layer, seq, node.criteria, node.criteriaBranch,[son.validDataIndex for son in node.son],node.category))
        for idx, son in enumerate(node.son):
            self.printTree(son, layer+1, idx+1)

    def __predict(self, idx , sample, title, node : TreeNode):
        node.validDataIndex.append(idx)
        if node.isLeaf()==True:
            return node.category
        attrIdx = 0
        for idx, attr in enumerate(title):
            if attr==node.criteria:
                attrIdx = idx
                break
        for idx, cat in enumerate(node.criteriaBranch):
            if sample[attrIdx] == cat:
                return self.__predict(idx , sample, title, node.son[idx])
    
    def tagClean(self, node: TreeNode):
         node.validDataIndex = []
         for son in node.son:
             self.tagClean(son)
    
    def tagWithData(self,node:TreeNode, dataPraser:DataWrapperAndProcessor):
        for idx, sample in enumerate(dataPraser.DATA):
            pred = self.__predict(idx , sample, dataPraser.TITLE, self.root)
    
    def reTag(self, node:TreeNode,dataPraser:DataWrapperAndProcessor):
        self.tagClean(node)
        self.tagWithData(node,dataPraser)
    
    def getAccuracy(self, dataPraser: DataWrapperAndProcessor):     # give tag and get accuracy
        self.tagClean(self.root)
        ans = 0
        rightSet = []
        wrongSet = []
        tot = len(dataPraser.LABEL)
        for idx, sample in enumerate(dataPraser.DATA):
            pred = self.__predict(idx , sample, dataPraser.TITLE, self.root)
            if pred == dataPraser.LABEL[idx]:
                ans += 1
                rightSet.append(idx)
            else:
                wrongSet.append(idx)
        return ans/tot , rightSet , wrongSet
    
    def printAcc(self, dataPraser: DataWrapperAndProcessor):
        acc, _, _=self.getAccuracy(dataPraser)
        print("准确率为：{}%".format(acc * 100))

# 4.3
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
print("========4.3========")
dataPraser_1=DataWrapperAndProcessor(feature,label,feature_title)
model=DecisionTree(dataPraser_1)
model.buildTree(model.root)
model.printTree(model.root)
model.printAcc(dataPraser_1)

# 4.4
feature_train=[["青绿","蜷缩","浊响","清晰","凹陷","硬滑"],
["乌黑","蜷缩","沉闷","清晰","凹陷","硬滑"],
["乌黑","蜷缩","浊响","清晰","凹陷","硬滑"],
["青绿","稍蜷","浊响","清晰","稍凹","软粘"],
["乌黑","稍蜷","浊响","稍糊","稍凹","软粘"],
["青绿","硬挺","清脆","清晰","平坦","软粘"],
["浅白","稍蜷","沉闷","稍糊","凹陷","硬滑"],
["乌黑","稍蜷","浊响","清晰","稍凹","软粘"],
["浅白","蜷缩","浊响","模糊","平坦","硬滑"],
["青绿","蜷缩","沉闷","稍糊","稍凹","硬滑"]]

feature_test=[["青绿","蜷缩","沉闷","清晰","凹陷","硬滑"],
["浅白","蜷缩","浊响","清晰","凹陷","硬滑"],
["乌黑","稍蜷","浊响","清晰","稍凹","硬滑"],
["乌黑","稍蜷","沉闷","稍糊","稍凹","硬滑"],
["浅白","硬挺","清脆","模糊","平坦","硬滑"],
["浅白","蜷缩","浊响","模糊","平坦","软粘"],
["青绿","稍蜷","浊响","稍糊","凹陷","硬滑"],]
label_train=[1,1,1,1,1,0,0,0,0,0]
label_test=[1,1,1,0,0,0,0]
feature_title=["色泽","根蒂","敲声","纹理","脐部","触感"]
print("========4.4========")
dataPraser_train=DataWrapperAndProcessor(feature_train,label_train,feature_title)
dataPraser_test=DataWrapperAndProcessor(feature_test,label_test,feature_title)
# origin
print("origin tree")
model=DecisionTree(dataPraser_train)
model.buildTree(model.root, optLoss="gini")
model.printTree(model.root)
model.printAcc(dataPraser_test)
# pre prunning
print("pre prunning")
model=DecisionTree(dataPraser_train)
model.buildTree(model.root, optLoss="gini")
model.reTag(model.root, dataPraser_test)
model.pre_prun(model.root, dataPraser_test)
model.printTree(model.root)
model.printAcc(dataPraser_test)
# post prunning
print("post prunning")
model=DecisionTree(dataPraser_train)
model.buildTree(model.root, optLoss="gini")
model.reTag(model.root, dataPraser_test)
model.post_prun(model.root, dataPraser_test)
model.printTree(model.root)
model.printAcc(dataPraser_test)