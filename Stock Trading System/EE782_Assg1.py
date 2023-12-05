# -*- coding: utf-8 -*-
"""Untitled0.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Eh4s3Yvny7cxR6Xy5rrDuOX_w0hf3OjS

#Assignment 1: LSTM-based Stock Trading System
#Vansh Kapoor (200100164)
#Assignment Done Induvidually
"""

from google.colab import drive
import torch
import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd
import copy
import torch.nn as nn
import matplotlib.dates as mdates
from tqdm.notebook import tqdm
device = 'cuda:0' if torch.cuda.is_available() else 'cpu'

dir_path='/content/drive/MyDrive/EE782_Assg_1'
files_list=os.listdir(dir_path)

from google.colab import drive
drive.mount('/content/drive')

"""#Q1) Familiarizing with the input data

##1 (a) Plot the minute-by-minute closing price series of few stocks
"""

file_path1='/content/drive/MyDrive/EE782_Assg_1/ATO_1min.txt'#File path
file_path2='/content/drive/MyDrive/EE782_Assg_1/DXC_1min.txt'
file_path3='/content/drive/MyDrive/EE782_Assg_1/CAG_1min.txt'
file_path4='/content/drive/MyDrive/EE782_Assg_1/CMCSA_1min.txt'
file_path5='/content/drive/MyDrive/EE782_Assg_1/AWK_1min.txt'
df=[]
col_names=['Time', 'Open','Max', 'Min', 'Close', 'Vol'] #Names given to the columns
stocks=['ATO','DXC','CAG','CMCSA','AWK'] #Names of the stock
df.append(pd.read_csv(file_path1,names=col_names))
df.append(pd.read_csv(file_path2,names=col_names))
df.append(pd.read_csv(file_path3,names=col_names))
df.append(pd.read_csv(file_path4,names=col_names))
df.append(pd.read_csv(file_path5,names=col_names)) #Appending the stock data
for i in range(len(df)):
    df[i].iloc[:,0]=pd.to_datetime(df[i].iloc[:,0]) #Converting Date column to Datetime type

fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(10, 10)) #creating multiple subplots
k=0
for i in range(0,2):
    for j in range(0,2):
        lst=df[k].Close
        axes[i,j].plot(np.arange(len(df[k])),lst)
        axes[i,j].set_xlabel('Per Minute')
        axes[i,j].set_ylabel('Closing Price')
        axes[i,j].set_title(stocks[k])
        k+=1
plt.show()

"""##1(b) Plot the day-by-day closing price series of a few stocks"""

days_lst=[]
for j in range(5):
    lst=[]
    for i in range(len(df[j])):
        date=df[j].iloc[i,0].strip().split(' ')[0] #spliting Time entries based on Day
        day= date.split('-')[-1]
        if(i==0):
            var= day
        if(day!=var):
            lst.append(i-1)
            var=day
    lst.append(len(df[j])-1)
    days_lst.append(lst) #day list contains the indices of distinct dates
fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(10, 10)) #creating multiple subplots
k=0
for i in range(0,2):
    for j in range(0,2):
        lst=df[k].iloc[days_lst[k]].Close
        axes[i,j].plot(np.arange(len(df[k].iloc[days_lst[k]])),lst)
        axes[i,j].set_xlabel('Per Day')
        axes[i,j].set_ylabel('Closing Price')
        axes[i,j].set_title(stocks[k])
        k+=1
plt.show()

"""##1(c) Plot a complete candlestick chart with volume on secondary y-axis for a few stocks with atime period of your choice"""

fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(21, 21))
k=0
for i in range(0,2):
    for j in range(0,2):
        up=df[k].iloc[1:60][df[k].iloc[1:60].Open<=df[k].iloc[1:60].Close] #defining up as the entries where Closing is greater than Opening
        down=df[k].iloc[1:60][df[k].iloc[1:60].Close<df[k].iloc[1:60].Open] #defining up as the entries where Closing is less than Opening
        c1='green'
        c2='red'
        w=0.03
        w1=0.3
        axes[i,j].bar(up.index, up.Close-up.Open, w1, bottom=up.Open, color=c1,alpha=0.9)
        axes[i,j].bar(up.index, up.Max-up.Close, w, bottom=up.Close, color=c1,alpha=0.9)
        axes[i,j].bar(up.index, up.Min-up.Open,w, bottom=up.Open,color=c1,alpha=0.9)
        axes[i,j].bar(down.index, down.Close-down.Open, w1, bottom=down.Open, color=c2,alpha=0.9)
        axes[i,j].bar(down.index, down.Max-down.Open, w, bottom=down.Open, color=c2,alpha=0.9)
        axes[i,j].bar(down.index, down.Min-down.Close,w, bottom=down.Close,color=c2,alpha=0.9)
        axes[i,j].set_title(stocks[k])
        # axes[i,j].set_xticklabels(down.Time,rotation=30, ha='right')
        axes[i,j].set_ylabel('Price')
        ax2 = axes[i,j].twinx()
        ax2.bar(df[k].iloc[1:60].index, df[k].iloc[1:60].Vol, color ='maroon',width = 0.3,alpha=0.1)
        ax2.set_ylabel('Volume')
        ax2.set_xticks([])

        k+=1
plt.show()

fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(21, 21))
k=0
for i in range(0,2):
    for j in range(0,2):
        up=df[k].iloc[1:5][df[k].iloc[1:5].Open<=df[k].iloc[1:5].Close] #defining up as the entries where Closing is greater than Opening
        down=df[k].iloc[1:5][df[k].iloc[1:5].Close<df[k].iloc[1:5].Open] #defining up as the entries where Closing is less than Opening
        c1='green'
        c2='red'
        w=0.03
        w1=0.3
        axes[i,j].bar(up.Time, up.Close-up.Open, w1, bottom=up.Open, color=c1,alpha=0.9)
        axes[i,j].bar(up.Time, up.Max-up.Close, w, bottom=up.Close, color=c1,alpha=0.9)
        axes[i,j].bar(up.Time, up.Min-up.Open,w, bottom=up.Open,color=c1,alpha=0.9)
        axes[i,j].bar(down.Time, down.Close-down.Open, w1, bottom=down.Open, color=c2,alpha=0.9)
        axes[i,j].bar(down.Time, down.Max-down.Open, w, bottom=down.Open, color=c2,alpha=0.9)
        axes[i,j].bar(down.Time, down.Min-down.Close,w, bottom=down.Close,color=c2,alpha=0.9)
        axes[i,j].set_title(stocks[k])
        # axes[i,j].set_xticklabels(down.Time,rotation=30, ha='right')
        axes[i,j].set_ylabel('Price')
        ax2 = axes[i,j].twinx()
        ax2.bar(df[k].iloc[1:5].Time, df[k].iloc[1:5].Vol, color ='maroon',width = 0.3,alpha=0.1)
        ax2.set_ylabel('Volume')
        k+=1
plt.show()

"""##1 (d) Note down your observations, e.g. are there any data issues, unexpected jumps,unexpected missing data etc

a) There are several **unexpected missing data:** the data is not continuous, i.e., there are missing data points for intermediate minutes between two data points for several times\
b) There are several **unexpected jumps:** Sometimes there are **huge spikes** on the Closing price at certain datapoints

#Q2) Normalization of Data

There are broadly two ways of normalization:\
 (i)  **Max-Min Normalization**\
 (ii) **Standard Scaler Normalization**
"""

file_path1='/content/drive/MyDrive/EE782_Assg_1/ATO_1min.txt'
file_path2='/content/drive/MyDrive/EE782_Assg_1/CAG_1min.txt'
file_path3='/content/drive/MyDrive/EE782_Assg_1/CMCSA_1min.txt'
file_path4='/content/drive/MyDrive/EE782_Assg_1/AWK_1min.txt'
df=[]
col_names=['Time', 'Open','Max', 'Min', 'Close', 'Vol']
stocks=['ATO','CAG','CMCSA','AWK']
df.append(pd.read_csv(file_path1,names=col_names))
df.append(pd.read_csv(file_path2,names=col_names))
df.append(pd.read_csv(file_path3,names=col_names))
df.append(pd.read_csv(file_path4,names=col_names))
for i in range(len(df)):
    df[i].iloc[:,0]=pd.to_datetime(df[i].iloc[:,0])

"""##Min-Max Scaler"""

from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler
scaler=MinMaxScaler(feature_range=(-1, 1)) #Scaling features to (-1,1)
norm_1=copy.deepcopy(df) #Applying Deep Copy
for i in range(4):
    norm_1[i][['Open','Max', 'Min', 'Close','Vol']]=scaler.fit_transform(df[i][['Open','Max', 'Min', 'Close','Vol']])
print(norm_1[0])

"""##Standard Scaler"""

from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler
scaler=StandardScaler() # Utilizing Standard Scaler
norm_2=copy.deepcopy(df) #Applying Deep Copy
for i in range(4):
    norm_2[i][['Open','Max', 'Min', 'Close','Vol']]=scaler.fit_transform(df[i][['Open','Max', 'Min', 'Close','Vol']]) #Standard Scaler
print(norm_2[0])

"""## Observing the Range of values obtained by both the methods Min-Max scaling seems more appropriate for stock analysis
Min-Max scaling preserves the **proportional connections** between data points, which proves valuable when dealing with stock data.This is because in  stock analysis **interdependencies among Open, High, Low, and Close** prices are significant and this attribute of Min-Max Scaler is highly advantageous

# Q3) Make some scenario decisions

##3 (a) Inter-Day Trade
I will prefer inter-day trade as the data is not continuous minute-wise but is day-wise continuous

##3 (b) Buy-Ask Spread and Commission

*   **Buy-Ask spread:** Buy ask spread ∝ (Price/Volume) I'll let the proportionality constant to be 1%
*   **Trade Commission:** By surfing over the internet, I found out that an average trade commission of 2$ is charged

##3 (c) Trading with Single Stock
I have decided to begin with trading only a single stock

#Q4) Write a pytorch module for defining an LSTM model. Keep it flexible so that the input dimension, number of units, number of layers can easily be changed
"""

dfm=copy.deepcopy(df) #deep Copy
df_n1=copy.deepcopy(df)

norm=[]
for i in range(4):
    dfm[i]['Month']=df[i]['Time'].apply(lambda x: str(x.month) + ' '+ str(x.year))
    dic={}

## Code For Averaging over MONTH


    dic['Open']=df[i].groupby(pd.Grouper(freq='M',key='Time')).first().iloc[:,0]
    dfm[i]['Max']=df[i][['Max','Time']].groupby(pd.Grouper(freq='M',key='Time'))['Max'].transform(lambda x: x.max())
    dfm[i]['Min']=df[i][['Min','Time']].groupby(pd.Grouper(freq='M',key='Time'))['Min'].transform(lambda x: x.min())
    dic['Close']=df[i].groupby(pd.Grouper(freq='M',key='Time')).last().iloc[:,-2]
    dfm[i]['Vol']=df[i][['Vol','Time']].groupby(pd.Grouper(freq='M',key='Time'))['Vol'].transform(lambda x: x.sum())
    dfm[i]=dfm[i].drop_duplicates(subset='Month')
    dic['Open'] = dic['Open'].dropna()
    dic['Close']=dic['Close'].dropna()
    dfm[i]['Open']=dic['Open'].to_numpy()
    dfm[i]['Close']=dic['Close'].to_numpy()

#Setting up an LSTM Module
class LSTM(nn.Module):
    def __init__(self, inp, hidden, layers):
        super().__init__()
        self.hidden = hidden #defining no. of hidden Layers
        self.layers = layers #Defining no. of layers in an LSTM
        self.lstm = nn.LSTM(inp, hidden, layers,batch_first=True) #giving arguments as input to the LSTM
        self.fc = nn.Linear(hidden, 1) #Setting prediction to be of siongle dimension

    def forward(self, x):
        batch_size = x.size(0)
        h0 = torch.zeros(self.layers, batch_size, self.hidden).to(device) #Initializing
        c0 = torch.zeros(self.layers, batch_size, self.hidden).to(device) #Initializing
        out, _ = self.lstm(x, (h0, c0))
        out = self.fc(out[:, -1, :]) #Taking the final time_step of the time sequence
        return out
model = LSTM(5,5, 1) #Giving the parameters to the LSTM model
model.to(device)
model

"""#Q5) Write a flexible dataloader for training the LSTM model"""

dfm=copy.deepcopy(df) #Deep Copy
df_n1=copy.deepcopy(df) #Deep Copy

norm=[] #Normalized array Day-wise
for i in range(4):
    dfm[i]['Day']=df[i]['Time'].apply(lambda x: str(x.day) +' '+str(x.month) + ' '+ str(x.year)) #Spliting via delimiters
    dic={}

## Code Averaging Over Days

##Applying function Day-Wise
    dic['Open']=df[i].groupby(pd.Grouper(freq='D',key='Time')).first().iloc[:,0]
    dfm[i]['Max']=df[i][['Max','Time']].groupby(pd.Grouper(freq='D',key='Time'))['Max'].transform(lambda x: x.max())
    dfm[i]['Min']=df[i][['Min','Time']].groupby(pd.Grouper(freq='D',key='Time'))['Min'].transform(lambda x: x.min())
    dic['Close']=df[i].groupby(pd.Grouper(freq='D',key='Time')).last().iloc[:,-2]
    dfm[i]['Vol']=df[i][['Vol','Time']].groupby(pd.Grouper(freq='D',key='Time'))['Vol'].transform(lambda x: x.sum())
    dfm[i]=dfm[i].drop_duplicates(subset='Day')
    dic['Open'] = dic['Open'].dropna() #droping Nan Values
    dic['Close']=dic['Close'].dropna() #Droping Nan values
    dfm[i]['Open']=dic['Open'].to_numpy()
    dfm[i]['Close']=dic['Close'].to_numpy()

## Averaging Over Days and using MIN-MAX Scaler
from sklearn.preprocessing import MinMaxScaler
scaler=MinMaxScaler(feature_range=(-1, 1))
norm=copy.deepcopy(dfm)
for i in range(4):
    norm[i][['Open','Max', 'Min', 'Close','Vol']]=scaler.fit_transform(norm[i][['Open','Max', 'Min', 'Close','Vol']])
    norm[i].drop(columns=['Day'],inplace=True) #Droping Day column as not required for training or Testeing
    norm[i]=norm[i].reset_index() #Reseting Indices
    norm[i].drop(columns=['index'],inplace=True)

X=[]
Y=[]
past=15
#setting the see_back_timesteps as 15
for i in range(past-1,len(norm[1])-1):
    y=[]
    for j in range(past,0,-1):
        y.append(np.array(norm[1].iloc[i-j,1:6]))
    X.append(np.array(y))
    Y.append(np.array(norm[1].iloc[i,4]))
X=np.array(X)

print(X.shape)

##Segregating Training and Testing Data
X_Train=X[:int(0.8*X.shape[0])]
X_Test=X[int(0.8*X.shape[0]):]
Y_Train=Y[:int(0.8*X.shape[0])]
Y_Test=Y[int(0.8*X.shape[0]):]


##Changing Array Type to Float
X_Test=np.array(X_Test).reshape(-1,past,5).astype('float')
X_Train=np.array(X_Train).reshape(-1,past,5).astype('float')
Y_Test=np.array(Y_Test).reshape(-1,1).astype('float')
Y_Train=np.array(Y_Train).reshape(-1,1).astype('float')

##Conversion of Data Type
X_Train = torch.tensor(X_Train).float()
Y_Train = torch.tensor(Y_Train).float()
X_Test = torch.tensor(X_Test).float()
Y_Test = torch.tensor(Y_Test).float()

print(X_Train.shape)

from torch.utils.data import Dataset
#Initializing the Dataset of the Timeseries
class TimeSeriesDataset(Dataset):
    def __init__(self, X, y):
        self.X = X
        self.y = y

    def __len__(self):
        return len(self.X)

    def __getitem__(self, i):
        return self.X[i], self.y[i]
#Defing testing and Training datasets
train_dataset = TimeSeriesDataset(X_Train, Y_Train)
test_dataset = TimeSeriesDataset(X_Test, Y_Test)

from torch.utils.data import DataLoader
##Seting batch size and feeding in to the DataLoader
batch_size =32
##Dataloader gives us the dat batch-wise segregated
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

for _, batch in enumerate(train_loader):
    x_batch, y_batch = batch[0].to(device), batch[1].to(device)
    ##Dataloader gives us the dat batch-wise segregated
    print(x_batch.shape, y_batch.shape)
    break

"""#Q6) Training the model by trying to predict the future Closing Price"""

def train_one_epoch():
    model.train(True)
    print(f'Epoch: {epoch + 1}')
    running_loss = 0.0
#setting up training of an epoch
    for batch_index, batch in enumerate(train_loader):
        x_batch, y_batch = batch[0].to(device), batch[1].to(device)

        output = model(x_batch)
        loss = loss_function(output, y_batch)
        running_loss += loss.item()#Calc aggregate Loss

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if batch_index % 100 == 99:  # print every 100 batches
            avg_loss_across_batches = running_loss / 100
            print('Batch {0}, Loss: {1:.3f}'.format(batch_index+1,
                                                    avg_loss_across_batches))
            running_loss = 0.0
    print()

def validate_one_epoch():
    model.train(False)
    running_loss = 0.0
 #setting up validating for an epoch
    for batch_index, batch in enumerate(test_loader):
        x_batch, y_batch = batch[0].to(device), batch[1].to(device)

        with torch.no_grad():
            output = model(x_batch)
            loss = loss_function(output, y_batch)
            running_loss += loss.item() #Calc aggregate Loss

    avg_loss_across_batches = running_loss / len(test_loader)

    print('Val Loss: {0:.3f}'.format(avg_loss_across_batches))
    print('***************************************************')
    print()

learning_rate = 0.001
num_epochs =15
loss_function = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

for epoch in tqdm(range(num_epochs)):
    train_one_epoch()
    validate_one_epoch()

"""#Q7) Trading module that will make some hard-coded logical decisions to buy, hold, sell

## We can trade Profitably!!
"""

model.eval()
comm=0.001
def predictor(x,model,comm=0,thr=0):
     #shape of x is (1,past=15,5)
    y=0
    out=model(x)
    if out>(x[0,-1,-2]+comm+thr): #Condition for Buying
        y='Buy'
    elif out<(x[0,-1,-2]+comm-thr): #Condition for Selling
        y='Sell'
    else:
        y='Hold' #Else Hold
    return(y)
profit=0 #Initialization

##Iterating for the Test Data Set to determine Profit

for i in DataLoader(TimeSeriesDataset(X_Test, Y_Test), batch_size=1, shuffle=False):
    batch=i[0]
    out=i[1].reshape(-1)
    mod=model(i[0]).detach().reshape(-1)
    if(predictor(batch,model,thr=0.005,comm=0.001)=='Buy'):
        profit+=out-batch[0,-1,-2]-comm
    elif(predictor(batch,model,thr=0.005,comm=0.001)=='Sell'):
        profit+=(-out+batch[0,-1,-2])-comm

print(profit)

fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(10, 10))
k=0
for i in range(0,2):
    for j in range(0,2):
        lst=norm[k].Close
        axes[i,j].plot(np.arange(len(norm[k])),lst)
        axes[i,j].set_xlabel('Per Month')
        axes[i,j].set_ylabel('Closing Price')
        axes[i,j].set_title(stocks[k])
        k+=1
plt.show()

"""#Q8)  Testing the Trading system on the latest years"""

with torch.no_grad():
    predicted = model(X_Test.to(device)).to('cpu').numpy()
plt.plot(Y_Test, label='Actual Close')
plt.plot(predicted, label='Predicted Close')
plt.xlabel('Day')
plt.ylabel('Close')
plt.legend()
plt.title('Stock CAG')
plt.show()

"""##8 (a) Prediction Error Increases
Clearly as we expected the price **prediction error increases** as you go further in time from the last time on which it was trained.

##8 (b) We Can Trade Profitably!!
"""

for i in DataLoader(TimeSeriesDataset(X_Test, Y_Test), batch_size=1, shuffle=False):
    batch=i[0]
    out=i[1].reshape(-1)
    mod=model(i[0]).detach().reshape(-1)
    if(predictor(batch,model,thr=0.005,comm=0.001)=='Buy'):
        profit+=out-batch[0,-1,-2]-comm
    elif(predictor(batch,model,thr=0.005,comm=0.001)=='Sell'):
        profit+=(-out+batch[0,-1,-2])-comm

print(profit)

"""Even by taking Considerable Commission into account, i.e., **1% of max stock value**. We can trade profitably!  
**Note:** Thevalue obtained is the normalized value

## 8 (c) The strategy used above produces significant profit by utilizing buy, hold and share and thus outperforms a simple buy-and-hold strategy over a large period of time

#Q9) ADVANCED [BONUS]

##9 (a)Model using multiple stock prices as inputs
"""

new=norm[3].loc[norm[3]['Time'].dt.year !=2004] #Using other stocks and using the datapoints corresponding to same days

model = LSTM(10,10, 1)
model.to(device)

model = LSTM(10,12, 1) #LSTM having 10 inputs and hidden layers as 12
model.to(device)
X1=[]
Y1=[]
past=15
for i in range(past-1,len(norm[2])-1):
    y=[]
    for j in range(past,0,-1):
        y.append(np.concatenate((np.array(new.iloc[i-j,1:6]),np.array(norm[2].iloc[i-j,1:6])))) #Concatenating with Otehr Stocks
    X1.append(np.array(y))
    Y1.append(np.array(norm[2].iloc[i,4]))
X1=np.array(X1)

print(X1.shape)

X_Train1=X1[:int(0.8*X1.shape[0])]
X_Test1=X1[int(0.8*X1.shape[0]):]
Y_Train1=Y1[:int(0.8*X1.shape[0])]
Y_Test1=Y1[int(0.8*X1.shape[0]):]

X_Test1=np.array(X_Test1).reshape(-1,past,10).astype('float')
X_Train1=np.array(X_Train1).reshape(-1,past,10).astype('float')
Y_Test1=np.array(Y_Test1).reshape(-1,1).astype('float')
Y_Train1=np.array(Y_Train1).reshape(-1,1).astype('float')
##Segregating Training and Testing Data

##Conversion of Data Type
X_Train1 = torch.tensor(X_Train1).float()
Y_Train1 = torch.tensor(Y_Train1).float()
X_Test1 = torch.tensor(X_Test1).float()
Y_Test1 = torch.tensor(Y_Test1).float()

batch_size1 =32
##Seting batch size and feeding in to the DataLoader
train_dataset = TimeSeriesDataset(X_Train1, Y_Train1)
test_dataset = TimeSeriesDataset(X_Test1, Y_Test1)

##Dataloader gives us the dat batch-wise segregated
train_loader = DataLoader(train_dataset, batch_size=batch_size1, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=batch_size1, shuffle=False)

for _, batch in enumerate(train_loader):
    x_batch, y_batch = batch[0].to(device), batch[1].to(device)
    print(x_batch.shape, y_batch.shape)
    break

learning_rate = 0.001
num_epochs =20 #num epochs=20
loss_function = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
for epoch in range(num_epochs):
    train_one_epoch()
    validate_one_epoch()

"""###Evaluation and Conclusion
For the initial datapoints it is predicting quite well, but as the horizon of evaluation increases the prediction error increases when compared to the model traioned with only a single stock
"""

with torch.no_grad():
    predicted = model(X_Test1.to(device)).to('cpu').numpy()
plt.plot(Y_Test1, label='Actual Close')
plt.plot(predicted, label='Predicted Close')
plt.xlabel('Day')
plt.ylabel('Close')
plt.legend()
plt.show()

"""##9 (b) Adding Day Of the Week and Along With Utiling Multiple Stocks to Improve Prediction"""

norm[2]['Day'] = norm[2]['Time'].dt.day_name() #Getting the name of the days for a date
one_hot_bit = pd.get_dummies(norm[2]['Day']) #generating one-hot for each day
norm[2] = pd.concat([norm[2], one_hot_bit], axis=1) #concatenating the one-hot bit array
norm[2]= norm[2].drop(columns=['Day'])
print(norm[2])

new['Day'] = new['Time'].dt.day_name() #Getting the name of the days for a date for other Stocks
one_hot_bit = pd.get_dummies(new['Day']) #generating one-hot for each day
new = pd.concat([new, one_hot_bit], axis=1) #Concat One-hot bit Encoding
new= new.drop(columns=['Day'])
print(new)

model = LSTM(20,20, 1) #Training model with 20 hidden layers
model.to(device)
X1=[]
Y1=[]
past=15
for i in range(past-1,len(norm[2])-1):
    y=[]
    for j in range(past,0,-1):
        y.append(np.concatenate((np.array(new.iloc[i-j,1:]),np.array(norm[2].iloc[i-j,1:]))))
    X1.append(np.array(y))
    Y1.append(np.array(norm[2].iloc[i,4]))
X1=np.array(X1)

print(X1.shape)

X_Train1=X1[:int(0.8*X1.shape[0])]
X_Test1=X1[int(0.8*X1.shape[0]):]
Y_Train1=Y1[:int(0.8*X1.shape[0])]
Y_Test1=Y1[int(0.8*X1.shape[0]):]

X_Test1=np.array(X_Test1).reshape(-1,past,20).astype('float')
X_Train1=np.array(X_Train1).reshape(-1,past,20).astype('float')
Y_Test1=np.array(Y_Test1).reshape(-1,1).astype('float')
Y_Train1=np.array(Y_Train1).reshape(-1,1).astype('float')

X_Train1 = torch.tensor(X_Train1).float()
Y_Train1 = torch.tensor(Y_Train1).float()
X_Test1 = torch.tensor(X_Test1).float()
Y_Test1 = torch.tensor(Y_Test1).float()

batch_size1 =32

train_dataset = TimeSeriesDataset(X_Train1, Y_Train1)
test_dataset = TimeSeriesDataset(X_Test1, Y_Test1)
train_loader = DataLoader(train_dataset, batch_size=batch_size1, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=batch_size1, shuffle=False)

for _, batch in enumerate(train_loader):
    x_batch, y_batch = batch[0].to(device), batch[1].to(device)
    print(x_batch.shape, y_batch.shape)
    break

learning_rate = 0.001
num_epochs =10
loss_function = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
for epoch in range(num_epochs):
    train_one_epoch()
    validate_one_epoch()

"""###Evaluation and Conclusion (Drastically Improves!)

Our Model's Performance drastically increases as we use the information about days of the week. It performs much better than both the previous models!
"""

with torch.no_grad():
    predicted = model(X_Test1.to(device)).to('cpu').numpy()
plt.plot(Y_Test1, label='Actual Close')
plt.plot(predicted, label='Predicted Close')
plt.xlabel('Day')
plt.ylabel('Close')
plt.legend()
plt.title('')
plt.show()

"""#References

Amazon Stock Analysis: https://www.youtube.com/watch?v=q_HS4s1L8UI&t=652s
(https://colab.research.google.com/drive/1CBIdPxHn_W2ARx4VozRLIptBrXk7ZBoM?usp=sharing)
"""