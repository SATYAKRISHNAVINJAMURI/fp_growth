
# coding: utf-8

# In[2]:


import csv
import sys
import itertools


# In[21]:


class treeNode:
    def __init__(self, id, counter, parentNode):
        self.id = id
        self.counter = counter
        self.nextLink = None
        self.parent = parentNode
        self.children = []
    def inc(self, numOccur):
        '''
        Increments the counter attribute with a given value.  
        '''
        self.counter += numOccur
    #display tree in text. Useful for debugging        
    def disp(self,file,ind=1):
        '''
        Displays the node and it's children recursively.
        Outputs the tree to a file.
        '''
#         print (' |'*ind, self.id, '-', self.counter)
        print (' |'*ind, self.id, '-', self.counter,file=file)
        for child in self.children:
            child.disp(file,ind+1)


# In[22]:


class FP_tree:
    def __init__(self):
        '''
        header_table is a dictionary where keys are item names and values are a list of support value and nextNode LInk.
        Conventional Header_Table.
        '''
        self.header_table = {}
        self.root =  treeNode('root',0,None)
        self.nodeCount = 1
        
    def insert(self,itemset,counter):
        '''
        Insert the entire item set into FP Tree.
        Input : 1) itemset - List of items to be inserted.
                2) Counter - No of such itemsets. i,e., no of times the itemset to be inserted.
        
        '''
        parent = self.root
        itemset = list(itemset) # Just to make it list given in anyform
        for item in itemset:
            flag = 0
            for node in parent.children:
                if(node.id == item):
                    node.inc(counter)
                    self.header_table[node.id][0] += counter
                    parent = node
                    flag = 1
                    break
            if(flag != 1):
                node = treeNode(item,counter,parent)
                self.nodeCount += 1
                parent.children.append(node)
                self.update_header_table(node,counter)
                parent = node
        return
    
    
    def findPrefixPath(self,node):
        '''
        Returns all the id's of the nodes in the path from root to this node.
        Input: Node to which the path to be found.
        Output: A List of 2d tuples with path as 1st value and counter as second value.
        '''
        all_paths = []
        while(node):
            plist = []
            pnode = node.parent
            while(pnode.id != 'root'):
                plist.append(pnode.id)
                pnode = pnode.parent
            plist.reverse()
            all_paths.append((plist,node.counter))
            node = node.nextLink
        return all_paths
    
    
    def find_coditional_pattern_base(self):
        '''
        Output: Dictionary with item as key and tuple of list of paths returned by findPrefix Path method.
        This coditional_pattern_base is later used for generating frequent patterns.
        '''
        conditional_pattern_base = {}
        for values in self.header_table.values():
            conditional_pattern_base[values[1].id] = self.findPrefixPath(values[1])
        return conditional_pattern_base
    
    
    def update_header_table(self,node,counter):
        '''
        Updates the header_table with the given node. Just adds the node at the end of its linked list.
        header_table is a dictionary with item_id as key and list of support count and link to next node as values.
        '''
        if node.id not in self.header_table.keys():
            self.header_table[node.id] = [counter,None]
        else:
            self.header_table[node.id][0] += counter
        nextNode = self.header_table[node.id][1]
        if(nextNode == None):
            self.header_table[node.id][1] = node
        else:
            while(nextNode.nextLink):
                nextNode = nextNode.nextLink
            nextNode.nextLink = node
            
            
    def sum_of_nodes(self,item):
        '''
        function:sum_of_nodes(item)
        Calculates the sum of counter values in all nodes and returns the same. Usefull for debugging.
        '''
        sum = 0
        nextNode = self.header_table[item][1]
        while(nextNode):
            sum += nextNode.counter
            nextNode = nextNode.nextLink
        return sum


# In[23]:


def generate_patterns(root,prefix,prefix_sup,minsup):
    '''
    Generate all the Frequent Patterns.
    '''
    subsets = {}
    nodes_list = {}
    subsets[tuple(prefix)]= prefix_sup
    if not root.children:
        return len(subsets),subsets
    while(root.children):
        node = root.children[0]
        nodes_list[node.id] = node.counter
        root = node
    p_nodes = list(nodes_list.keys())
    for item in prefix:                     
        nodes_list[item] = prefix_sup
    for i in range(1,len(p_nodes) + 1):
        apex = list(itertools.combinations(p_nodes, i))
        after_list = [tuple([x for x in prefix] + list(tup)) for tup in apex]
        for fpattern in after_list:
            all_sup = []
            for item in fpattern:
                all_sup.append(nodes_list[item])
            sup = min(all_sup)
            subsets[fpattern] = sup
    return len(subsets),subsets


# In[24]:


def check_for_single_prefix_path(parent):
    '''
    Checks if FP Tree has only one single path like linked list.
    '''
    while(parent):
        if(len(parent.children) > 1):
            return False
        elif(len(parent.children) == 0):
            break
        else:
            parent = parent.children[0]
    return True


# In[25]:


def del_infrequent(conditional_pattern_base,minsup):
    '''
    From the conditional pattern base, support count of all items is calculated and items with less support are removed.
    This is an enhancing the conditional Pattern Base before building Tree.
    Because of this conditional patterns are modified such that node with high support appears first just to 
    satisfy the property of FP Tree.
    '''
    result = {}
    for key,values in conditional_pattern_base.items():
        item_support = {}
        for ttuple in values:
            itemset = ttuple[0]
            counter = ttuple[1]
            for item in itemset:
                if item in item_support.keys():
                    item_support[item] += counter
                else:
                    item_support[item] = counter
        item_support = dict(sorted(item_support.items(), key=lambda x: x[1],reverse = True))
        itemslist = list(item_support.keys())
        for tkey ,tvalue in item_support.items():
            if(tvalue < minsup):
                itemslist.remove(tkey)
        patterns = []
        for qtuple in values:
            item_list = list(qtuple[0])
            counter = qtuple[1]
            new_list = []
            for k in itemslist:
                if k in item_list:
                    new_list.append(k)
            patterns.append((tuple(new_list),counter))
        result[key] = patterns
    return result


# In[26]:


def FP_growth(fp_tree,prefix,prefix_sup,file,minsup,toPrint):
    '''
    Final FP Growth Alogrithm.
    Generates Patterns if Tree is a single prefix path.
    If tree is not a single prefix path then conditional pattern base is generated and key is added to the 
    Prefix. Again FP tree is build on the conditional Pattern Base. A recursive step.
    '''
    count = 0;
    no_of_nodes = 0;
    if(check_for_single_prefix_path(fp_tree.root)):
        count,frequent_patterns = generate_patterns(fp_tree.root,prefix,prefix_sup,minsup)
        if frequent_patterns:
            if(toPrint):
                for key,value in frequent_patterns.items():
                    for item in key:
                        print(item,' ',end="",file=file)
                    print(":",value,file=file)
        return count,fp_tree.nodeCount
    else:
        if prefix:
            count += 1
            if(toPrint):
                for item in prefix:
                    print(item,' ',end="",file=file)
                print(":",prefix_sup,file=file)
#                 print({tuple(prefix):prefix_sup})      # Very Important do not delete. Print an important pattern
        conditional_pattern_base = fp_tree.find_coditional_pattern_base();
        conditional_pattern_base = del_infrequent(conditional_pattern_base,minsup)  # Very important step to enhance the code.
        for key,values in conditional_pattern_base.items():
            prefix_sup = fp_tree.header_table[key][0]
            header_table_child = {}
            new_fp_tree = FP_tree()
            for qtuple in values:
                itemset = qtuple[0]
                counter = qtuple[1]
                new_fp_tree.insert(itemset,counter)
            prefix.append(key)
            pre = prefix.copy()
            prefix.remove(key)
            a,b = FP_growth(new_fp_tree,pre,prefix_sup,file,minsup,toPrint)
            count += a
            no_of_nodes += b
            
    return count,no_of_nodes
    



def main(pathToDataSet,minSup,toPrint):
    '''
    Inputs: pathToDataSet - Absolute path to the data set.
            minSup - min support value in percentage.
    '''
    data = []   # Carries list of data and transactions.
    headerTable = {}  # Header Table keeps track of all the nodes of same type.
    itemsSupport = {}
    totalTrans = 0
    with open(pathToDataSet,'r') as csvfile:
        plots = csv.reader(csvfile, delimiter=' ')
        for row in plots:
            data.append(row)
            for item in row:
                if(item == ''):      # Data Cleaning eliminate empty space.
                    continue
                if item in itemsSupport.keys():
                    itemsSupport[item] += 1
                else:
                    itemsSupport[item] = 1
            totalTrans += 1
    minSup = (minSup*totalTrans/100)      # Percentage => to normal.
    print("No of Transactions:",totalTrans)
    print("No of Items:",len(itemsSupport))
    frequentItems = {key:value for key,value in itemsSupport.items() if value >= minSup}
    print("No of Frequent Items:",len(frequentItems))
    fpTree = FP_tree()
    allFrequentItems = frequentItems.keys()
    for transaction in data:
        itemset = list(filter(lambda v: v in allFrequentItems,transaction))
        itemset.sort(key=lambda x:frequentItems[x],reverse=True)
        fpTree.insert(itemset,1)
    if(toPrint):
        print("Printing output to ./output.txt")
        file = open("output.txt","w+")
        totalPatterns,nodeCount = FP_growth(fpTree,[],0,file,minSup,True)
        file.close()
    else:
        totalPatterns,nodeCount = FP_growth(fpTree,[],0,"",minSup,False)
    print("No of Frequent Patterns:",totalPatterns)
    print("No of Nodes:",nodeCount)
   



if(__name__ == "__main__"):
    path = str(sys.argv[1])
    if(sys.argv[3] == 'True'):
        main(path,float(sys.argv[2]),True)         #upport in percentage
    elif(sys.argv[3] == 'False'):
        main(path,float(sys.argv[2]),False)
    else:
        print("Usage 'python3 FP_growth.py <file_name> <minimum_support> True/False'")
