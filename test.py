from tou.pemv1 import GeneratePEM
import pandas as pd

a = GeneratePEM(non_responsive_hours=[2,3,4,5]).get_pem_matrix()
print(a)
b = {}

pre_hours = [0,1,2,3,4,5,6,7,8,9,10,11,11] + [11]*35
post_hours = [23,22,21,20,19,18,17,16,15,14,13,12,12] + [12]*23 + [11,10,9,8,7,6,5,4,3,2,1,0]

for i in range(48):
    temp = []
    for j in range(48):
        if j in list(range(i-pre_hours[i], i+post_hours[i]+1,1)):
            temp.append(a[i%24][j%24])
        else:
            temp.append(0)
    b[i] = temp

df = pd.DataFrame(b)
df.to_csv('hi.csv')



