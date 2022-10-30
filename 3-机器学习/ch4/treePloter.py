import matplotlib.pyplot as plt
from id3tree import ID3DecisionTree
 
class TreePlotter:
 
    def __init__(self, tree, feature_names, label_names):
        self.decision_node = dict(boxstyle="sawtooth", fc="0.8")
        self.leaf_node = dict(boxstyle="round4", fc="0.8")
        self.arrow_args = dict(arrowstyle="<-")
        #保存决策树
        self.tree = tree
        #保存特征名字字典
        self.feature_names=feature_names
        #保存类标记名字字典
        self.label_names=label_names
        self.totalW = None
        self.totalD = None
        self.xOff = None
        self.yOff = None
    
    def _get_num_leafs(self, node):
        '''获取叶节点的个数'''
        if not node.children:
            return 1
        num_leafs = 0
        for key in node.children.keys():
            if node.children[key].children:
                num_leafs += self._get_num_leafs(node.children[key])
            else:
                num_leafs += 1
        return num_leafs
    
    def _get_tree_depth(self, node):
        '''获取树的深度'''
        if not node.children:
            return 1
        max_depth = 0
        for key in node.children.keys():
            if node.children[key].children:
                this_depth = 1 + self._get_tree_depth(node.children[key])
            else:
                this_depth = 1
            if this_depth > max_depth:
                max_depth = this_depth
        return max_depth
        
    def _plot_mid_text(self, cntrpt, parentpt, txtstring, ax1) :
        '''在父子节点之间填充文本信息'''
        x_mid = (parentpt[0] - cntrpt[0])/2.0 + cntrpt[0]
        y_mid = (parentpt[1] - cntrpt[1])/2.0 + cntrpt[1]
        ax1.text(x_mid, y_mid, txtstring)
    
    def _plot_node(self, nodetxt, centerpt, parentpt, nodetype, ax1):
        ax1.annotate(nodetxt, xy= parentpt,\
            xycoords= 'axes fraction',\
            xytext=centerpt, textcoords='axes fraction',\
            va="center", ha="center", bbox=nodetype, arrowprops= self.arrow_args)
        
    def _plot_tree(self, tree, parentpt, nodetxt, ax1):
        #子树的叶节点个数，总宽度
        num_leafs = self._get_num_leafs(tree)
        #子树的根节点名称
        tree_name = self.feature_names[tree.feature_index]['name']
        #计算子树根节点的位置
        cntrpt = (self.xOff + (1.0 + float(num_leafs))/2.0/self.totalW, self.yOff)
        #画子树根节点与父节点中间的文字
        self._plot_mid_text(cntrpt, parentpt, nodetxt, ax1)
        #画子树的根节点，与父节点间的连线，箭头。
        self._plot_node(tree_name, cntrpt, parentpt, self.decision_node, ax1)
        #计算下级节点的y轴位置
        self.yOff = self.yOff - 1.0/self.totalD
        for key in tree.children.keys():
            child = tree.children[key]
            if child.children:
                #如果是子树，递归调用_plot_tree
                self._plot_tree(child, cntrpt, self.feature_names[tree.feature_index]['value_names'][key], ax1)
            else:
                #如果是叶子节点，计算叶子节点的x轴位置
                self.xOff = self.xOff + 1.0/self.totalW
                #如果是叶子节点，画叶子节点，以及叶子节点与父节点之间的连线，箭头。
                self._plot_node(self.label_names[child.value], (self.xOff, self.yOff), cntrpt, self.leaf_node, ax1)
                #如果是叶子节点，画叶子节点与父节点之间的中间文字。
                self._plot_mid_text((self.xOff, self.yOff), cntrpt, self.feature_names[tree.feature_index]['value_names'][key], ax1)
        #还原self.yOff
        self.yOff = self.yOff + 1.0/self.totalD
 
    def create_plot(self):
        fig = plt.figure(1, facecolor='white')
        fig.clf()
        #去掉边框
        axprops=dict(xticks=[], yticks=[])
        ax1 = plt.subplot(111, frameon=False, **axprops)
        #树的叶节点个数，总宽度
        self.totalW = float(self._get_num_leafs(self.tree))
        #树的深度，总高度
        self.totalD = float(self._get_tree_depth(self.tree))
        self.xOff = -0.5/self.totalW
        self.yOff = 1.0
        #树根节点位置固定放在(0.5,1.0)位置，就是中央的最上方
        self._plot_tree(self.tree, (0.5,1.0), '', ax1)
        plt.show()