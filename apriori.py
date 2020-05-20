
# coding: utf-8

# In[1]:

import sys
import operator
from itertools import chain, combinations
from collections import defaultdict
from optparse import OptionParser


# In[2]:

def subsets(arr):
    """ Returns non empty subsets of arr"""
    return chain(*[combinations(arr, i + 1) for i, a in enumerate(arr)])


# In[3]:

def returnItemsWithMinSupport(itemSet, transactionList, minSupport, freqSet):
        """calculates the support for items in the itemSet and returns a subset
       of the itemSet each of whose elements satisfies the minimum support"""
        _itemSet = set()
        localSet = defaultdict(int)

        for item in itemSet:
                for transaction in transactionList:
                        if item.issubset(transaction):
                                freqSet[item] += 1
                                localSet[item] += 1

        for item, count in localSet.items():
                support = float(count)/len(transactionList)

                if support >= minSupport:
                        _itemSet.add(item)

        return _itemSet


# In[4]:

def joinSet(itemSet, length):
        """Join a set with itself and returns the n-element itemsets"""
        return set([i.union(j) for i in itemSet for j in itemSet if len(i.union(j)) == length])


# In[5]:

def getItemSetTransactionList(data_iterator):
    transactionList = list()
    itemSet = set()
    for record in data_iterator:
        transaction = frozenset(record)
        transactionList.append(transaction)
        for item in transaction:
            itemSet.add(frozenset([item]))              # Generate 1-itemSets
    return itemSet, transactionList


# In[6]:

def runApriori(data_iter, minSupport, minConfidence):
    """
    run the apriori algorithm. data_iter is a record iterator
    Return both:
     - items (tuple, support)
     - rules ((pretuple, posttuple), confidence)
    """
    itemSet, transactionList = getItemSetTransactionList(data_iter)

    freqSet = defaultdict(int)
    largeSet = dict()
    # Global dictionary which stores (key=n-itemSets,value=support)
    # which satisfy minSupport

    assocRules = dict()
    # Dictionary which stores Association Rules

    oneCSet = returnItemsWithMinSupport(itemSet,
                                        transactionList,
                                        minSupport,
                                        freqSet)

    currentLSet = oneCSet
    k = 2
    while(currentLSet != set([])):
        largeSet[k-1] = currentLSet
        currentLSet = joinSet(currentLSet, k)
        currentCSet = returnItemsWithMinSupport(currentLSet,
                                                transactionList,
                                                minSupport,
                                                freqSet)
        currentLSet = currentCSet
        k = k + 1

    def getSupport(item):
            """local function which Returns the support of an item"""
            return float(freqSet[item])/len(transactionList)

    toRetItems = []
    for key, value in largeSet.items():
        toRetItems.extend([(tuple(item), getSupport(item))
                           for item in value])

    toRetRules = []
    for key, value in list(largeSet.items())[1:]:
        for item in value:
            _subsets = map(frozenset, [x for x in subsets(item)])
            for element in _subsets:
                remain = item.difference(element)
                if len(remain) > 0:
                    confidence = getSupport(item)/getSupport(element)
                    rule_support=getSupport(item)
                    lift = getSupport(item)/(getSupport(element)*getSupport(remain))
                    all_conf= getSupport(item)/(max(getSupport(element),getSupport(remain)))
                    if confidence >= minConfidence and rule_support>=minSupport:
                        toRetRules.append(((tuple(element), tuple(remain)),
                                           confidence,rule_support,lift,all_conf))
    return toRetItems, toRetRules


# In[10]:

def printResults(items, rules):
    """prints the generated itemsets sorted by support and the confidence rules sorted by confidence"""
    print("\n------------------------ Frequence Items:")
    for item, support in sorted(items, key=operator.itemgetter(1)):
        print("item: %s ,Support: %.3f" % (str(item), support))
    print("\n------------------------ RULES:")
    for rule, confidence ,rule_support,lift,all_conf in sorted(rules, key=operator.itemgetter(1)):
        pre, post = rule
        print("Rule: %s ==> %s ,Confidence: %.3f, Support:%.3f" % (str(pre), str(post), confidence,rule_support))

def evaluation(items,rules,etype):
    if(etype=='lift'):
        no_corr=[]
        positive_corr=[]
        negative_corr=[]
        print("\n------------------------ EVALUATION---lift--range(0,∞):")
        for rule, confidence ,rule_support,lift,all_conf in sorted(rules, key=operator.itemgetter(1)):
            pre, post = rule
            if(lift in (0.97,1.03)):
                no_corr.append(((tuple(pre), tuple(post)),lift))
            elif(lift>1.03):
                positive_corr.append(((tuple(pre), tuple(post)),lift))
            else:
                negative_corr.append(((tuple(pre), tuple(post)),lift))
        print('lift>1,项集之间呈正相关的规则如下:\n')            
        for rule,lift in sorted(positive_corr, key=operator.itemgetter(1)):
            pre, post = rule
            print("Rule: %s ==> %s ,lift: %.3f Positve rules" % (str(pre), str(post), lift))

        print('lift≈1,项集之间无关的规则如下:\n')            
        for rule,lift in sorted(no_corr, key=operator.itemgetter(1)):
            pre, post = rule
            print("Rule: %s ==> %s ,lift: %.3f no correlation rules" % (str(pre), str(post), lift))

        print('lift<1,项集之间呈负相关的规则如下:\n')            
        for rule,lift in sorted(negative_corr, key=operator.itemgetter(1)):
            pre, post = rule
            print("Rule: %s ==> %s ,lift: %.3f negative rules" % (str(pre), str(post), lift))
        
    else:
        print("\n------------------------ EVALUATION---all_conf--range(0,1):")
        for rule, confidence ,rule_support,lift,all_conf in sorted(rules, key=operator.itemgetter(1)):
            pre, post = rule
            print("Rule: %s ==> %s, all_conf:%.3f" % (str(pre), str(post),all_conf))        
# In[11]:

def dataFromFile(fname):
        """Function which reads from the file and yields a generator"""
        file_iter = open(fname, 'rU')
        for line in file_iter:
                line = line.strip().rstrip(',')                         # Remove trailing comma
                record = frozenset(line.split(','))
                yield record


