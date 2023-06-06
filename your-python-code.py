#!/usr/bin/env python3

import os, sys
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

df = pd.DataFrame(np.random.randn(100))
print(f'DataFrame={df}')
histogram = df.hist()
plt.show()
aa=5