'''
决策树算法要求输入和输出都是连续值
'''
import numpy as np
from math import log
from copy import deepcopy
INF = 1e108


class TreeNode:
    def __init__(self, feature: np.array, label: np.array, validX: np.array, validY: np.array, validAttr: list, height: int, cmFeature = None) -> None:
        self.TRX = feature    # train set
        self.TRY = label      
        self.VAX = validX     # valid set
        self.VAY = validY
        self.validAttr = validAttr    # 有效属性对应下标
        # 注意：样本会进行分割，但属性不会分割，只会用title进行有效置位。
        self.sampleNum, self.attrNum = feature.data.shape
        self.classTag = label[np.argmax(label)]    # 该节点划分到的类种类
        self.validInfo = 0       # 使用验证集测试时，准确个数，总数和正确率信息
        for y in validY:
            if y == self.classTag:
                self.validInfo += 1
        self.validInfo = (self.validInfo, len(validY))    
        self.trainInfo = 0       # 记录训练集，准确个数，总数和正确率信息
        for y in label:
            if y == self.classTag:
                self.trainInfo += 1
        self.trainInfo = (self.trainInfo, len(label))    
        self.divFeatureIdx = None  # 该节点子树的分类特征对应的下标
        self.cmFeature = cmFeature   # 该子树共有特征，注意如果是数值类数据，就是二叉节点，左小右大，只会记录数据分界点；标签数据那就是字符串，左小右大地搜寻
        self.son = []           # 儿子节点
        self.height = height         # 节点高度
    
    def isLeaf(self):
        return len(self.son) == 0
    
    def __metaVal(self, boolIdx: np.array = None, criteria = "entropy"):     # boolIdx 是 numpy 的布尔下标，把要计算的子属性找出来，如果为None，视为整个训练集的gini系数
        l = self.TRY if boolIdx is None else self.TRY[boolIdx]
        s = set(i for i in l)
        mapping = {}
        for i in s:
            mapping[i] = 0
        tot = 0
        for i in l:
            tot += 1
            mapping[i] += 1
        if criteria == "entropy":
            ans = 0
            for val in mapping.values():
                p = val / tot
                ans -= p * log(p)
        elif criteria == "gini":
            ans = 1
            for val in mapping.values():
                p = val / tot
                ans -= p * p
        else:
            Exception("Wrong criteria!")
        # print("Ans:",ans, criteria)
        return ans
    
    def __rate(self, idxList, pts = None, criteria = "entropy"):                  # 计算某个属性下能获得的增益, pts为None，则视为标签型
        # print(criteria)
        tot = len(self.TRY)
        ans = 0
        for idx, num in idxList:
            ans += num / tot * self.__metaVal(boolIdx = idx,criteria = criteria)
        ans = ans if criteria == "gini" else self.__metaVal(criteria = criteria) - ans
        return ans
    
    def __split_tag_data(self, attrIdx, criteria = "entropy"):   # 标签型拆分
        s = set(i for i in self.TRX[:, attrIdx])
        s = list(s).sort()
        idxList = []
        for val in s:
            idx = self.TRX[:, attrIdx] == val
            num = len(self.TRY[idx])
            idxList.append((idx, num))
        return self.__rate(attrIdx, idxList, criteria=criteria), idxList

    def __split_numerical_data(self, attrIdx, pts, criteria = "entropy"):         # 数值型数据拆分
        attrView = self.TRX[:, attrIdx]
        lessIdx = attrView <= pts            
        greaterIdx = attrView > pts
        lessNum = len(self.TRY[lessIdx])
        greaterNum = len(self.TRY[greaterIdx])
        idxList = [(lessIdx, lessNum), (greaterIdx, greaterNum)]
        return self.__rate(idxList = idxList, pts = pts, criteria = criteria), idxList
        
    def __bestNumericalDivision(self, attrIdx):         # 按照信息增益的原则进行划分
        sample = deepcopy(self.TRX[:, attrIdx])
        sample.sort()
        interp = [(sample[i] + sample[i + 1]) / 2 for i in range(len(sample) - 1)]
        bestPts = interp[0]
        bestGain = -INF
        for pts in interp:
            gain, _ = self.__split_numerical_data(attrIdx, pts, "entropy")
            if gain > bestGain:
                bestPts = pts
                bestGain = gain
        return bestPts
    
    def __split_attr_data(self, attrIdx, criteria):        # 对单个属性进行拆分，返回两个参数，第一个是计算出的值，第二个是划分结果的坐标列表和数量的元组
        sample = self.TRX[0, :]
        pts = None
        if type(sample[attrIdx]) == type("str"):
            rate, idxList = self.__split_tag_data(attrIdx, criteria)
        else:
            pts = self.__bestNumericalDivision(attrIdx)
            rate, idxList = self.__split_numerical_data(attrIdx, pts, criteria)
        if criteria == "gini":
            rate = - rate   # 正向化，最大化即可
        retList = []
        for idx, _ in idxList:          # 这里的idxList的元素还是元组，第二个是数量
            retList.append(idx)
        return rate, retList, pts

    def __findBestSplitAttr(self, criteria = "entropy"):    # 找到最适合划分的属性和划分方案
        bestAttrIdx = -1
        bestDivIdxList = []
        bestVal = -INF      # 越大越好，在__split_attr_data做正向化
        bestPts = None
        for idx, flag in enumerate(self.validAttr):
            if flag == 0:
                continue
            val, lst, pts = self.__split_attr_data(idx, criteria)
            if val > bestVal:
                bestVal = val
                bestAttrIdx = idx
                bestDivIdxList = lst
                bestPts = pts
        return bestAttrIdx, bestDivIdxList, bestPts

    def __isSplitNeeded(self):
        if sum(self.validAttr) <= 1:    # 只有一个属性，不用再划分了
            return False
        s = set(i for i in self.TRY)
        if len(s) == 1:                 # 只有一个种类，无需划分
            return False
        return True

    def __splitValidSet(self, attrIdx, targetVal, cmp = None):  # 小于是Yes，大于是No
        if cmp is None:
            return self.VAX[:, attrIdx] == targetVal
        elif cmp == True:
            return self.VAX[:, attrIdx] <= targetVal
        else:
            return self.VAX[:, attrIdx] > targetVal

    def split(self, criteria = "entropy", pre_prun = False):
        if self.__isSplitNeeded() == False:
            return
        splitAttrIdx, splitList, pts = self.__findBestSplitAttr(criteria = criteria)
        # print("height:",self.height)
        # print("res:",splitAttrIdx, pts)
        son_validAttr = deepcopy(self.validAttr)
        son_validAttr[splitAttrIdx] = 0
        # print("here:",pts, splitAttrIdx)
        for idx in splitList:
            sample = self.TRX[idx]
            if len(sample) == 0:
                continue
            # print(sample)
            sample = sample[0]
            cmFeature = sample[splitAttrIdx]
            validIdx = self.__splitValidSet(splitAttrIdx, cmFeature)
            if type(cmFeature)!=type("str"):
                # print(cmFeature, pts)
                # print("det:",cmFeature, pts)
                validIdx = self.__splitValidSet(splitAttrIdx, pts, cmFeature <= pts)
                cmFeature = pts
            # print(validIdx)
            if len(self.TRY[idx]) == 0:     # 数据集为空则不生长
                continue
            # print(self.TRX[idx])
            son = TreeNode(deepcopy(self.TRX[idx]), deepcopy(self.TRY[idx]), deepcopy(self.VAX[validIdx]), deepcopy(self.VAY[validIdx]), deepcopy(son_validAttr), self.height + 1, cmFeature = cmFeature)
            self.son.append(son)
        if len(self.son) <= 1:  # 单个儿子，不生长了，剪枝
            self.son = []
            return
        self.divFeatureIdx = splitAttrIdx
        if pre_prun == True:
            fa_tot = self.validInfo[0]
            son_tot = 0
            for son in self.son:
                son_tot += son.validInfo[0]
            if son_tot <= fa_tot:
                self.son = []   # 准确率不高，别分了，没卵用
        
class DecisionTree:
    def __init__(self, feature: np.array, label: np.array, validX: np.array, validY: np.array) -> None:
        self.__sampleNum, self.__attrNum = feature.data.shape
        self.__TR_TOT, self.__VA_TOT = len(label), len(validY)
        lst = [1 for i in range(self.__attrNum)]
        self.__root = TreeNode(feature, label, validX, validY, lst, 0, "Root")
    
    def __buildTree(self, node: TreeNode, criteria = "entropy", pre_prun = False):
        node.split(criteria = criteria, pre_prun = pre_prun)
        for son in node.son:
            self.__buildTree(son, criteria = criteria, pre_prun = pre_prun)
    
    def buildTree(self, criteria = "entropy", pre_prun = False):
        self.__buildTree(self.__root, criteria = criteria, pre_prun = pre_prun)
        
    def __getTrainAccAndValidAcc(self, node: TreeNode):
        if node.isLeaf() == True:
            return node.trainInfo[0], node.validInfo[0]
        acc_train, acc_valid = 0, 0
        for son in node.son:
            a, b = self.__getTrainAccAndValidAcc(son)
            acc_train += a
            acc_valid += b
        return acc_train, acc_valid
    
    def getTrainAccAndValidAcc(self):
        tot_train, tot_valid = self.__TR_TOT, self.__VA_TOT
        acc_train, acc_valid = self.__getTrainAccAndValidAcc(self.__root)
        return acc_train / tot_train, acc_valid / tot_valid
    
    def pred(self, feature):
        p = self.__root
        while p.isLeaf() == False:
            attr = feature[p.divFeatureIdx]
            if type(attr) == type("str"):
                for son in p.son:
                    if son.cmFeature == attr:
                        p = son
                        break
            else:
                pts = p.son[0].cmFeature
                if attr <= pts:
                    p = p.son[0]
                else:
                    p = p.son[1]
        return p.classTag

    def __post_prun(self, node: TreeNode):
        if node.isLeaf() == True:
            return
        for son in node.son:
            self.__post_prun(son)
        acc_valid = 0
        for son in node.son:
            acc_valid += son.validInfo[0]
        # print(node.height,acc_valid, node.validInfo[0])
        if acc_valid < node.validInfo[0]:
            node.son = []
            
    def post_prun(self):
        self.__post_prun(self.__root)
        
    def __printTree(self, node: TreeNode):
        print("------------第{:d}层------------".format(node.height))
        print("div:", node.divFeatureIdx)
        print("commom:", node.cmFeature)
        print("tag:", node.classTag)
        print("leaf:", node.isLeaf())
        print("trainInfo:", node.trainInfo)
        print("validInfo:", node.validInfo)
        for son in node.son:
            self.__printTree(son)
        
    def printTree(self):
        self.__printTree(self.__root)