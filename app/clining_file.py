
import pandas as pd

file =r'C:\Users\L0030959\Documents\Mes fichiers reçus\test\zpp md stock 90vu 27 mars.xls'


df = pd.read_csv(file,encoding='UTF-16 LE',sep='\t') 