import numpy as np
import pandas as pd

dic = {"java": 30, "python": 40, "c": 100}
dic_a = dic
dic_a["java"] = 3000
print(dic["java"])
# pf = pd.DataFrame(np.ones((3,3)),index=dic.keys(),columns=dic.keys())
# iav = pd.Series(list(dic.values()),index=dic.keys())
# iav = iav + 4
# print(iav)
# pf.at["java","java"] = -10
# pf.at["java","python"] = 100
# pf.at["java","c"] = 10000
# sr = pf.loc["java"].sort_values(ascending=False) # 降序排列
# print(list(sr.index))
# print(sr[0:2])
# print(pf.div(iav,axis=0))