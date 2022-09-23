from random import random
import numpy as np
feature=np.array([
    [0.697,0.460],
    [0.774,0.376],
    [0.634,0.264],
    [0.608,0.318],
    [0.556,0.215],
    [0.403,0.237],
    [0.481,0.149],
    [0.437,0.211],
    [0.666,0.091],
    [0.243,0.267],
    [0.245,0.057],
    [0.343,0.099],
    [0.639,0.161],
    [0.657,0.198],
    [0.360,0.370],
    [0.593,0.042],
    [0.719,0.103]
],dtype=float)

label=np.concatenate((np.ones((8,1),dtype=int),np.zeros((9,1),dtype=int)))

w=np.array([random(),random()]).reshape(2,1)
b=np.array(random()).reshape(1,1)

beta=np.concatenate((w,b),axis=0)
sampleNum=feature.data.shape[0]
x=np.concatenate((feature,np.ones(sampleNum).reshape(sampleNum,1)),axis=1)

def beta_sec_diff():
    