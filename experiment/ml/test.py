import numpy as np
a = np.random.rand(1,6)
print(a)
for idx, val in enumerate(a):
    a[idx] = 9
print(a)
