from cProfile import label
from pypinyin import pinyin, Style

class DataPreprocessor:
    def __init__(self, size: int = 1e7, checkPoint = "data/checkpoint.txt"):
        self.__data = None
        self.__label = None
        self.__MAXSIZE = size
        self.__shootingProb = {}
        self.__statusTransProb = {}
        self.__initDistri = {}
        self.__checkpoint = checkPoint
    
    def getShootingProb(self):
        return self.__shootingProb
    
    def getStatusTransProb(self):
        return self.__statusTransProb
    
    def getInitDistri(self):
        return self.__initDistri
        
    def setMaxSize(self, size: int):
        self.__MAXSIZE = size
    
    def loadData(self, srcPath: str) -> None:
        if (self.__loadCheckPoint() == False):
            print("Load stage")
            self.__loadData(srcPath)
            print("Pinyin stage")
            self.__labelPinyin()
            print("Compute stage")
            self.__computeInitialDistribution()
            self.__computeStatusTransformationProbablity()
            self.__computeShootingProbablity()
            self.__setCheckPoint()
        else:
            pass
        
    def __loadData(self, srcPath: str) -> None:
        self.__data = []
        rec = {}
        with open(srcPath, "r",encoding = "UTF-8") as f:
            datas = f.readlines()
            for idx, data in enumerate(datas):
                data = data.split("_!_")          # 以分隔符切分字符串
                data = data[3]
                if (rec.get(data) is None):     # 去重
                    rec[data] = 1
                self.__data.append(data)
                if (len(self.__data) == self.__MAXSIZE):
                    return
    
    def __labelPinyin(self) -> None:           # 打标签，去重
        self.__label = []
        for idx, data in enumerate(self.__data):
            label = pinyin(data, style = Style.NORMAL, errors = lambda item:  [c for c in item])
            for idx, ele in enumerate(label):
                label[idx] = label[idx][0]
            self.__label.append(label)
    
    def __computeStatusTransformationProbablity(self):
        for data in self.__data:
            for i in range(len(data)):
                if (i+1 == len(data)):
                    break
                ch_pre = data[i]
                ch_nxt = data[i+1]
                self.__statusTransProb = self.__updDictDict(self.__statusTransProb, ch_pre)
                self.__statusTransProb[ch_pre] = self.__updDictVal(self.__statusTransProb[ch_pre], ch_nxt)
        for key, mapVal in self.__statusTransProb.items():
            self.__statusTransProb[key] = self.__dictNorm(mapVal)

    def __computeShootingProbablity(self):
        for data, label in zip(self.__data, self.__label):
            for i in range(len(data)):
                ch = data[i]
                pinyin = label[i]
                if (ch == pinyin):
                    continue
                self.__shootingProb = self.__updDictDict(self.__shootingProb, ch)
                self.__shootingProb[ch] = self.__updDictVal(self.__shootingProb[ch], pinyin)
        for key, mapVal in self.__shootingProb.items():
            self.__shootingProb[key] = self.__dictNorm(mapVal)
    
    def __computeInitialDistribution(self):
        for data, label in zip(self.__data, self.__label):
            ch = data[0]
            label = label[0]
            self.__initDistri = self.__updDictDict(self.__initDistri, label)
            self.__initDistri[label] = self.__updDictVal(self.__initDistri[label], ch)
        for key, mapVal in self.__initDistri.items():
            self.__initDistri[key] = self.__dictNorm(mapVal)

    def __updDictVal(self, mapping: dict, key) -> dict:
        if (mapping.get(key) is None):
            mapping[key] = 1
        else:
            mapping[key] = mapping[key] + 1
        return mapping
    
    def __updDictDict(self, mapping: dict, key):
        if (mapping.get(key) is None):
            mapping[key]={}
        return mapping
    
    def __dictNorm(self, mapping: dict) -> dict:
        tot = 0
        for key, val in mapping.items():
            tot += val
        for key, val in mapping.items():
            mapping[key] = val / tot
        return mapping
    
    def __setCheckPoint(self):
        writeData = [self.__shootingProb, self.__statusTransProb, self.__initDistri]
        with open(self.__checkpoint,"w", encoding="UTF-8") as f:
            f.write(str(writeData))
        
    def __loadCheckPoint(self) -> bool:
        try:
            with open(self.__checkpoint, "r", encoding="UTF-8") as f:
                self.__shootingProb, self.__statusTransProb, self.__initDistri = eval(f.read())
                print("Check Point读取成功！")
            return True
        except Exception as e:
            print("Check Point不存在！")
            return False
    
    @staticmethod
    def getDictOfPinyin2Hanzi(srcDataPath: str):
        with open(srcDataPath, "r", encoding="UTF-8") as f:
            mapping = {}
            datas = f.readlines()
            for data in datas:
                pinyin, words = data.split(" ")
                if words[-1]=="\n":
                    words = words[:-1]
                mapping[pinyin] = words
        return mapping
        
class HMM:
    def __init__(self, shootingProb: dict = {}, statusTransProb: dict = {}, initDistri: dict = {}, pinyin2hanzi: dict = {}) -> None:
        self.__shootingProb = shootingProb          # 汉字 -> 拼音，发射概率
        self.__statusTransProb = statusTransProb    # 汉字 -> 汉字，转移概率
        self.__initDistri = initDistri              # 拼音 -> 文字列表，初始概率
        self.__pinyin2hanzi = pinyin2hanzi
        
    def viterbi(self, pinyinSeries: list):        # 接受字符串列表，元素为拼音，注意隐状态为汉字！
        wordLen = len(pinyinSeries)
        # print(pinyinSeries, wordLen)
        dp = [{} for _ in range(wordLen)]   # 第一维为句子长度维度；第二维即字典为状态维度，记录维特比变量
        pre = [{} for _ in range(wordLen)]  # 记录前驱
        initPinyin = pinyinSeries[0]
        # dp初始化
        for word, prob in self.__initDistri[initPinyin].items():
            pre[0][word] = "<BOS>"
            dp[0][word] = prob * self.__shootingProb[word][initPinyin]
        # dp计算
        for idx in range(1, wordLen):
            pinyin_j = pinyinSeries[idx]
            if (self.__pinyin2hanzi.get(pinyin_j) is None):
                continue                                # 存在性判断
            for word_j in self.__pinyin2hanzi[pinyin_j]:
                maxVal = 0
                for word_i, val in dp[idx - 1].items():
                    if (self.__statusTransProb.get(word_i) is None or self.__statusTransProb[word_i].get(word_j) is None):
                        continue                        # 存在性判断
                    elif (self.__shootingProb.get(word_j) is None or self.__shootingProb[word_j].get(pinyin_j) is None):
                        continue                        # 存在性判断
                    newVal = val * self.__statusTransProb[word_i][word_j] * self.__shootingProb[word_j][pinyin_j]
                    if (newVal > maxVal):
                        maxVal = newVal
                        pre[idx][word_j] = word_i
                if maxVal != 0:
                    dp[idx][word_j] = maxVal
        #回溯
        bestWord = ""
        maxVal = 0
        # for mapping in dp:
        #     print(mapping)
        for word, val in dp[wordLen - 1].items():   # 找到argmax word
            if val > maxVal:
                maxVal = val
                bestWord = word
        ans = bestWord
        idx = wordLen - 1
        pre_word = pre[idx][bestWord]
        while pre_word != "<BOS>":
            ans = pre_word + ans
            bestWord = pre_word
            idx -= 1
            pre_word = pre[idx][bestWord]
        return ans
    
    def eval(self, features, labels):
        tot = len(features)
        totLen = 0
        accLen = 0
        acc = 0
        count = 0
        for feature, label in zip(features, labels):
            count += 1
            pred = self.viterbi(feature)
            print("[testcase {:2d}]\t\n\tfeature: {}\n\tpredict result: {}\n\tactual result: {}".format(count, " ".join(feature), pred, label))
            if (pred==label):
                acc += 1
            totLen += len(pred)
            for i in range(len(pred)):
                if (pred[i] == label[i]):
                    accLen += 1
        print("逐句准确率为：{:.2f}%".format(100 * acc / tot))
        print("逐字准确率为：{:.2f}%".format(100 * accLen / totLen))

# 数据预处理
processor = DataPreprocessor()
processor.loadData("./data/toutiao_cat_data.txt")
pinyin2hanziMapping = processor.getDictOfPinyin2Hanzi("./data/pinyin2hanzi.txt")
shootingProb = processor.getShootingProb()
statusTransProb = processor.getStatusTransProb()
initDistri = processor.getInitDistri()

# 模型生成
model=HMM(shootingProb,statusTransProb,initDistri,pinyin2hanziMapping)
features = []
labels = []
TESTSET_PATH = "./data/测试集.txt"
with open(TESTSET_PATH, "r", encoding="gbk") as f:
    datas = f.readlines()
    for i in range(len(datas)):
        if (i % 2 == 1):
            continue
        feature = datas[i]
        if (feature[-1] == "\n"):
            feature = feature[:-1]
        feature = feature.split(" ")
        feature = [s.lower() for s in feature]
        label = datas[i + 1]
        if label[-1] == "\n":
            label = label[:-1]
        features.append(feature)
        labels.append(label)
model.eval(features, labels)