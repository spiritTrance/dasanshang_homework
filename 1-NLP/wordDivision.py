def wordDic(src, tar):
    dic = []
    with open(src, 'r', encoding = "utf-8") as f:
        datas = f.readlines()
        for i in datas:
            lst = i.split(":")
            dic.append(lst[0])
    with open(tar, 'w', encoding="utf-8") as f:
        for word in dic:
            f.writelines(word+"\n")
    with open(tar, "r", encoding="utf-8") as f:
        datas = f.readlines()
    s = set()
    for data in datas:
        word = data.split("\n")
        s.add(word[0])
    return s    

def forwardDivision(s: str, dic: set, maxSize: int = 10):       # 正向
    l = 0
    r = min(len(s), l + maxSize)   
    ans = []
    while l < len(s) and r > 0:
        sub_str = s[l: r]
        if l == r - 1:  
            ans.append(sub_str)
            l = r
            r = min(len(s), l + maxSize)
        elif sub_str in dic:      
            ans.append(sub_str)
            l = r
            r = min(len(s), l + maxSize)
        else:                   
            r -= 1              
    return ans
    
def backwardDivision(s: str, dic: set, maxSize: int = 10):      # 后向
    l = 0
    r = min(len(s), l + maxSize)
    s = s[::-1]                 
    ans = []
    while l < len(s) and r > 0:
        sub_str = s[l: r][::-1] 
        if l == r - 1:  
            ans = [sub_str] + ans
            l = r
            r = min(len(s), l + maxSize)
        elif sub_str in dic:      
            ans = [sub_str] + ans
            l = r
            r = min(len(s), l + maxSize)
        else:                   
            r -= 1              
    return ans

def singleWordCount(lst: list):        
    ans = 0
    for word in lst:
        if len(word) == 1:
            ans += 1
    return ans

def bidirectioonalDivision(s: str, dic: set, maxSize: int = 10):        # 双向
    ans_forward = forwardDivision(s, dic, maxSize)
    ans_backward = backwardDivision(s, dic, maxSize)
    if ans_forward == ans_backward:     
        return ans_backward
    elif len(ans_backward) == len(ans_forward):     
        forward_cnt = singleWordCount(ans_forward)
        backward_cnt = singleWordCount(ans_backward)
        ans = ans_forward if forward_cnt < backward_cnt else ans_backward
        return ans
    elif len(ans_backward) < len(ans_forward):  
        return ans_backward
    else:
        return ans_forward

def readTestCase(src):      
    with open(src, "r", encoding = "utf-8") as f:
        datas = f.readlines()
        testcase = [data.split("\n")[0] for data in datas]
    return testcase

def solve(i, testcase, dic, maxSize = 10):      
    ans_forward = forwardDivision(testcase, dic, maxSize)
    ans_backward = backwardDivision(testcase, dic, maxSize)
    ans_bidirect = bidirectioonalDivision(testcase, dic, maxSize)
    print("【测试用例 {:2d}】".format(i))
    print("\t正向最大匹配：","/".join(ans_forward))
    print("\t逆向最大匹配：","/".join(ans_backward))
    print("\t双向最大匹配：","/".join(ans_bidirect))

dic = wordDic("large_pinyin.txt", "dict.txt")
testcases = readTestCase("testcase.txt")
for i, testcase in enumerate(testcases):
    solve(i + 1, testcase, dic)