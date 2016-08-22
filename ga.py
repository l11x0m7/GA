#coding:utf8
import os
import sys
import math
import random
from random import shuffle
import re
import datetime
import logging
import json
import copy
import numpy as np
reload(sys)
sys.setdefaultencoding('utf8')
logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='ga.log',
                filemode='w')


class Generation:
    def __init__(self, aim, groupnum=5, generation=10, var_num=2, crossrate=0.9, variationrate=0.9, var_range=[0, 8], encodebit=5):
        # 适应度函数
        self.aim = aim
        # 种群数量
        self.groupnum = groupnum
        # 变量数
        self.var_num = var_num
        # 繁殖代数
        self.generation = generation
        # 当前代数
        self.curiter = 1
        # 交叉概率
        self.crossrate = crossrate
        # 变异概率
        self.variationrate = variationrate
        # log日志
        self.logger = logging.log
        # 变量取值范围，[a, b]
        self.var_range = var_range
        # 二进制编码位数
        self.encodebit = encodebit
        # 种群结果
        self.population = list()

        for i in range(groupnum):
            p_tmp = list()
            for j in range(self.encodebit*self.var_num):
                p_tmp.append(random.randint(0, 1))
            self.population.append(p_tmp)
        # print self.population
        # 记录最好的结果
        self.best = list()

    # 基因解码
    # pop:list()
    def geneDecode(self, pop):
        cut_p = -1
        decode_pop = list()
        for i in range(self.var_num):
            base = 1
            decimal = 0
            for bit in pop[cut_p:cut_p-self.encodebit:-1]:
                decimal += bit * base
                base *= 2
            cut_p = cut_p - self.encodebit
            decode_pop.append(float(self.var_range[1]-self.var_range[0])*decimal/(2**self.encodebit-1) + self.var_range[0])
        return decode_pop

    # 计算适应度
    def calcSufficiency(self):
        survival_list = list()
        decode_list = list()
        for pop in self.population:
            decode_pop = self.geneDecode(pop)
            decode_list.append(decode_pop)
            survival_rate = self.aim(decode_pop)
            survival_list.append(survival_rate)
        total = float(sum(survival_list))
        rate_survival_list = [rate/total for rate in survival_list]
        index = np.argsort(rate_survival_list)[-1]
        # print self.population, decode_list
        self.best.append((decode_list[index], survival_list[index], copy.copy(self.population[index])))
        # print self.best[-1]
        self.logger(logging.INFO, '{0} The survival rate of each population is: '.format(self.curiter) + '\n' + json.dumps(rate_survival_list))
        self.curiter += 1
        return rate_survival_list

    # 基因选择
    def choosePopulation(self):
        survival_list = self.calcSufficiency()
        for i in xrange(1, len(survival_list)):
            survival_list[i] += survival_list[i-1]
        
        new_population = list()
        for curgroup in range(self.groupnum):
            random_rate = random.random()
            for i, prop in enumerate(survival_list):
                if random_rate <= prop:
                    new_population.append(self.population[i])
                    break
        self.population = new_population
        return new_population

    # 交叉
    def crossCalc(self):
        self.choosePopulation()
        np.random.shuffle(self.population)
        for i in range(0, self.groupnum, 2):
            prop = random.random()
            rand_cross_point = random.randint(1, self.encodebit-1)
            if prop <= self.crossrate:
                self.population[i][rand_cross_point:], self.population[i+1][rand_cross_point:] = \
                    self.population[i+1][rand_cross_point:], self.population[i][rand_cross_point:]
        return self.population

    # 基因突变
    def geneRevolution(self):
        self.crossCalc()
        for i in range(self.groupnum):
            rand_variation_num = random.randint(1, self.encodebit)
            for j in range(rand_variation_num):
                prop = random.random()
                if prop <= self.variationrate:
                    rand_variation_point = random.randint(0, self.encodebit-1)
                    self.population[i][rand_variation_point] = \
                        1 - self.population[i][rand_variation_point]
        return self.population

    # 基因进化
    def geneEvolve(self):
        for i in range(self.generation):
            self.geneRevolution()

        self.best.sort(key=lambda kk:kk[1])
        print self.best[-1]
        return self.best[-1]



if __name__ == '__main__':
    aim = lambda x:x[0]**2+x[1]**2
    g = Generation(aim, groupnum=80, generation=100, var_num=2, var_range=[0, 7], encodebit=5)
    g.geneEvolve()


