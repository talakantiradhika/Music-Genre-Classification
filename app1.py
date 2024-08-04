import pickle
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from matplotlib import cm
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVC
df = pd.read_csv("features_3_sec.csv_path")
df['class_name'] = df['class_name'].astype('category')
df['class_label'] = df['class_name'].cat.codes
lookup_genre_name = dict(zip(df.class_label.unique(),
df.class_name.unique()))
cols = list(df.columns)
cols.remove('label')
cols.remove('class_label')
cols.remove('class_name')
X = df.iloc[:,1:28]
y = df['class_label']
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=0)
scaler = MinMaxScaler()
X_train_scaled = scaler.fit_transform(X_train)
# we must apply the scaling to the test set that we computed for the trainingset
X_test_scaled = scaler.transform(X_test)
pickle.dump(scaler,open('scaler.pkl','wb'))
knn = KNeighborsClassifier(n_neighbors = 10)
knn.fit(X_train_scaled, y_train)
#print(knn.score(X_test_scaled, y_test))
pickle.dump(knn, open("model_knn.pkl_path",'wb'))
svm = SVC(kernel='linear', C = 10).fit(X_train_scaled, y_train)
pickle.dump(svm, open("model_svm.pkl_path", 'wb'))
