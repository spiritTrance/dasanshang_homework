from pypinyin import pinyin, Style

# 数据预处理类
class DataPreprocessor:
    def __init__(self, checkPoint = "data/checkpoint.txt", size: int = 1e20):
        self.__data = None                  # 句子或词语的数据
        self.__label = None                 # 与__data一一对应的拼音
        self.__MAXSIZE = size               # data的最大值，默认为1e20
        self.__shootingProb = {}            # 发射概率，类型为 dict{str（拼音）: dict{str（汉字）: str（拼音）}}
        self.__statusTransProb = {}         # 转移概率，类型为 dict{str（汉字）: dict{str（汉字）: float（转移概率）}}
        self.__initDistri = {}              # 初始分布，类型为 dict{str（拼音）：dict{str（汉字）: float（概率）}}
        self.__checkpoint = checkPoint      # checkpoint的存放路径，设置checkpoint的目的的防止数据处理的时间过长，防止重复处理
    
    def getShootingProb(self):              # 返回发射概率
        return self.__shootingProb
    
    def getStatusTransProb(self):           # 返回状态转移概率
        return self.__statusTransProb
    
    def getInitDistri(self):                # 返回初始分布
        return self.__initDistri
        
    def setMaxSize(self, size: int):        # 设置数据最大数量
        self.__MAXSIZE = size
    
    def loadData(self, srcPath: str) -> None:   # 读取数据
        '''
        : params srcPath: 语料存放位置
        '''
        if (self.__loadCheckPoint() == False):
            self.__loadData(srcPath)
            self.__labelPinyin()
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
                data = data.split("_!_")            # 以分隔符切分字符串
                words = data[4]
                data = data[3]
                if (rec.get(data) is None):         # 去重, 如果句子是相同的，我们认为大概率采集到重复的数据，应该去重
                    rec[data] = 1
                    self.__data.append(data)
                    if (words[-1] == "\n"):
                        words = words[:-1]
                    words = words.split(",")
                    if (words[0] != ""):
                        for word in words:
                            self.__data.append(word)
                if (len(self.__data) == self.__MAXSIZE):
                    return
    
    def __labelPinyin(self) -> None:           # 标注拼音，同时去重
        self.__label = []
        for idx, data in enumerate(self.__data):
            if (idx % 10000 == 0 and idx != 0):
                print("已处理", idx, "条单句及词语")
            label = pinyin(data, style = Style.NORMAL, errors = lambda item:  [c for c in item])
            for idx, ele in enumerate(label):
                label[idx] = label[idx][0]
            self.__label.append(label)
    
    def __computeStatusTransformationProbablity(self):  # 计算状态转移概率
        for data in self.__data:
            for i in range(len(data)):
                try:
                    if (i+1 == len(data)):
                        break
                    ch_pre = data[i]
                    ch_nxt = data[i+1]
                    self.__statusTransProb = self.__updDictDict(self.__statusTransProb, ch_pre)
                    self.__statusTransProb[ch_pre] = self.__updDictVal(self.__statusTransProb[ch_pre], ch_nxt)
                except Exception as e:      # 不存在的键值对，忽略掉
                    continue
        for key, mapVal in self.__statusTransProb.items():
            self.__statusTransProb[key] = self.__dictNorm(mapVal)

    def __computeShootingProbablity(self):      # 计算发射概率
        for data, label in zip(self.__data, self.__label):
            for i in range(len(data)):
                try:
                    ch = data[i]
                    pinyin = label[i]
                    if (ch == pinyin):
                        continue
                    self.__shootingProb = self.__updDictDict(self.__shootingProb, ch)
                    self.__shootingProb[ch] = self.__updDictVal(self.__shootingProb[ch], pinyin)
                except Exception as e:              # 不存在的键值对，忽略掉
                    continue
        for key, mapVal in self.__shootingProb.items():
            self.__shootingProb[key] = self.__dictNorm(mapVal)
    
    def __computeInitialDistribution(self):     # 计算初始分布概率
        for data, label in zip(self.__data, self.__label):
            try:
                ch = data[0]
                label = label[0]
                self.__initDistri = self.__updDictDict(self.__initDistri, label)
                self.__initDistri[label] = self.__updDictVal(self.__initDistri[label], ch)
            except Exception as e:                  # 不存在的键值对，忽略掉
                continue
        for key, mapVal in self.__initDistri.items():
            self.__initDistri[key] = self.__dictNorm(mapVal)

    def __updDictVal(self, mapping: dict, key) -> dict:     # 字典统计
        if (mapping.get(key) is None):
            mapping[key] = 1
        else:
            mapping[key] = mapping[key] + 1
        return mapping
    
    def __updDictDict(self, mapping: dict, key):            # 将指定值设置为 字典
        if (mapping.get(key) is None):
            mapping[key]={}
        return mapping
    
    def __dictNorm(self, mapping: dict) -> dict:            # 数据归一化处理
        tot = 0
        for key, val in mapping.items():
            tot += val
        for key, val in mapping.items():
            mapping[key] = val / tot
        return mapping
    
    def __setCheckPoint(self):                              # 设置检查点
        writeData = [self.__shootingProb, self.__statusTransProb, self.__initDistri]
        with open(self.__checkpoint,"w", encoding="UTF-8") as f:
            f.write(str(writeData))
        
    def __loadCheckPoint(self) -> bool:                     # 读取检查点
        try:
            with open(self.__checkpoint, "r", encoding="UTF-8") as f:
                self.__shootingProb, self.__statusTransProb, self.__initDistri = eval(f.read())
                print("Check Point读取成功！")
            return True
        except Exception as e:
            print("Check Point 不存在，将生成 checkpoint 文件。")
            return False
    
    @staticmethod
    def getDictOfPinyin2Hanzi(srcDataPath: str):            # 返回拼音转换为汉字的字典，返回格式为：dict{str（拼音）:list(str（汉字）)}
        try:
            with open(srcDataPath, "r", encoding="UTF-8") as f:
                mapping = {}
                datas = f.readlines()
                for data in datas:
                    pinyin, words = data.split(" ")
                    if words[-1]=="\n":
                        words = words[:-1]
                    mapping[pinyin] = words
            return mapping
        except Exception as e:
            print("读取文件时发生以下错误: ", e, "程序即将退出！")
            exit(-1)
        
# HMM模型
class HMM:
    def __init__(self, shootingProb: dict = {}, statusTransProb: dict = {}, initDistri: dict = {}, pinyin2hanzi: dict = {}) -> None:
        self.__shootingProb = shootingProb          # 汉字 -> 拼音，发射概率
        self.__statusTransProb = statusTransProb    # 汉字 -> 汉字，转移概率
        self.__initDistri = initDistri              # 拼音 -> 文字列表，初始概率
        self.__pinyin2hanzi = pinyin2hanzi
        
    def predict(self, pinyinSeries: list):        # 使用维特比算法，接受字符串列表，每一项为单个字的拼音，注意隐状态为汉字
        wordLen = len(pinyinSeries)
        # print(pinyinSeries, wordLen)
        dp = [{} for _ in range(wordLen)]   # 第一维为句子长度维度；第二维即字典为状态维度，记录维特比变量
        pre = [{} for _ in range(wordLen)]  # 记录前驱
        initPinyin = pinyinSeries[0]
        # dp初始化
        self.__dp_init(dp, pre, initPinyin)
        # dp计算
        self.__dp_forward(pinyinSeries, wordLen, dp, pre)
        #回溯
        ans = self.__dp_traceback(wordLen, dp, pre)
        return ans

    def __dp_traceback(self, wordLen, dp, pre):     # dp回溯
        bestWord = ""
        maxVal = 0
        for word, val in dp[wordLen - 1].items():   # 找到argmax word
            if val > maxVal:
                maxVal = val
                bestWord = word
        ans = bestWord
        idx = wordLen - 1
        pre_word = pre[idx][bestWord]
        while pre_word != "<BOS>":                  # 回溯阶段
            ans = pre_word + ans
            bestWord = pre_word
            idx -= 1
            pre_word = pre[idx][bestWord]
        return ans

    def __dp_forward(self, pinyinSeries, wordLen, dp, pre):     # 计算dp
        for idx in range(1, wordLen):
            pinyin_j = pinyinSeries[idx]
            try:                              # 存在性判断
                for word_j in self.__pinyin2hanzi[pinyin_j]:
                    maxVal = 0
                    for word_i, val in dp[idx - 1].items():
                        try:
                            newVal = val * self.__statusTransProb[word_i][word_j] * self.__shootingProb[word_j][pinyin_j]
                            if (newVal > maxVal):
                                maxVal = newVal
                                pre[idx][word_j] = word_i
                        except Exception as e:          # 键值对不存在，忽略掉
                            continue
                    if maxVal != 0:
                        dp[idx][word_j] = maxVal
            except Exception as e:      # 外层for循环的键值对可能不存在，忽略即可
                continue

    def __dp_init(self, dp, pre, initPinyin):       # dp内容初始化
        for word, prob in self.__initDistri[initPinyin].items():
            pre[0][word] = "<BOS>"
            dp[0][word] = prob * self.__shootingProb[word][initPinyin]
    
    def eval(self, features, labels, printMiddleAns = False, printFinalAns = False):               # 模型评估，其中features的格式为list(list(str（拼音）)), labels的格式为list(str（汉字）)
        tot = len(features)
        totLen = 0                                  # 进行统计
        accLen = 0
        acc = 0
        count = 0
        for feature, label in zip(features, labels):
            count += 1
            pred = self.predict(feature)
            if (printMiddleAns == True):
                print("[testcase {:2d}]\t\n\tfeature: {}\n\tpredict result: {}\n\tactual result: {}".format(count, " ".join(feature), pred, label))
            if (pred==label):
                acc += 1
            totLen += len(pred)
            for i in range(len(pred)):
                if (pred[i] == label[i]):
                    accLen += 1
        if (printFinalAns == True):
            print("逐句准确率为：{:.2f}%".format(100 * acc / tot))
            print("逐字准确率为：{:.2f}%".format(100 * accLen / totLen))
        return acc / tot, accLen / totLen

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
        
# 模型评估
model.eval(features, labels, True, True)