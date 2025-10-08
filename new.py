import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Bidirectional
from tensorflow.keras.regularizers import l2
import math
from datetime import datetime, timedelta

# --------------------------------------------------
# 1. 加载数据
# --------------------------------------------------
data_path = 'more_test.csv'          # 确保与脚本同目录或写绝对路径
df = pd.read_csv(data_path)
df['ds'] = pd.to_datetime(df['ds'])  # 日期列

# --------------------------------------------------
# 2. 划分训练 / 测试集  70% : 30%
# --------------------------------------------------
train_size = int(len(df) * 0.7)
train_df = df.iloc[:train_size].copy()
test_df  = df.iloc[train_size:].copy()

# --------------------------------------------------
# 3. 提取全部 25 列特征
# --------------------------------------------------
feature_cols = df.columns[3:28].tolist()   # 25 列
target_col   = 'y'

X_train = train_df[feature_cols].values
y_train = train_df[target_col].values.reshape(-1, 1)
X_test  = test_df[feature_cols].values
y_test  = test_df[target_col].values.reshape(-1, 1)

dates_train = train_df['ds'].reset_index(drop=True)
dates_test  = test_df['ds'].reset_index(drop=True)

# --------------------------------------------------
# 4. 归一化
# --------------------------------------------------
scaler_X = MinMaxScaler(feature_range=(0, 1))
scaler_y = MinMaxScaler(feature_range=(0, 1))

X_train_scaled = scaler_X.fit_transform(X_train)
y_train_scaled = scaler_y.fit_transform(y_train)
X_test_scaled  = scaler_X.transform(X_test)
y_test_scaled  = scaler_y.transform(y_test)

# --------------------------------------------------
# 5. 构造 LSTM 样本  (time_step 步长)
# --------------------------------------------------
def make_dataset(X, y, time_step=10):
    xs, ys = [], []
    for i in range(len(X) - time_step):
        xs.append(X[i:i+time_step])
        ys.append(y[i+time_step, 0])
    return np.array(xs), np.array(ys)

TIME_STEP = 10
x_train_lstm, y_train_lstm = make_dataset(X_train_scaled, y_train_scaled, TIME_STEP)
x_test_lstm,  y_test_lstm  = make_dataset(X_test_scaled,  y_test_scaled,  TIME_STEP)

# --------------------------------------------------
# 6. 构建模型
# --------------------------------------------------
model = Sequential([
    Bidirectional(LSTM(128, return_sequences=True,
                       input_shape=(TIME_STEP, x_train_lstm.shape[2]),
                       kernel_regularizer=l2(1e-6))),
    Dropout(0.25),
    Bidirectional(LSTM(64, return_sequences=False, kernel_regularizer=l2(1e-6))),
    Dropout(0.2),
    Dense(1)
])
model.compile(optimizer='adam', loss='mse')

# --------------------------------------------------
# 7. 训练
# --------------------------------------------------
history = model.fit(x_train_lstm, y_train_lstm,
                    epochs=150,
                    batch_size=32,
                    verbose=2,
                    validation_data=(x_test_lstm, y_test_lstm))

# --------------------------------------------------
# 8. 评估
# --------------------------------------------------
def calc_metrics(y_true, y_pred):
    mse  = mean_squared_error(y_true, y_pred)
    mae  = mean_absolute_error(y_true, y_pred)
    rmse = math.sqrt(mse)
    mape = np.mean(np.abs((y_true - y_pred) / (y_true + 1e-8))) * 100
    return mse, mae, rmse, mape

# 反归一化
y_train_pred = scaler_y.inverse_transform(model.predict(x_train_lstm))
y_test_pred  = scaler_y.inverse_transform(model.predict(x_test_lstm))
y_train_true = scaler_y.inverse_transform(y_train_lstm.reshape(-1, 1))
y_test_true  = scaler_y.inverse_transform(y_test_lstm.reshape(-1, 1))

tr_mse, tr_mae, tr_rmse, tr_mape = calc_metrics(y_train_true, y_train_pred)
te_mse, te_mae, te_rmse, te_mape = calc_metrics(y_test_true,  y_test_pred)

# --------------------------------------------------
# 9. 预测未来 7 天
# --------------------------------------------------
def predict_next7(model, scaler_X, scaler_y, last_df, time_step=10):
    cur = last_df[-time_step:].copy()
    preds = []
    for _ in range(7):
        x = scaler_X.transform(cur.values).reshape(1, time_step, -1)
        y = model.predict(x, verbose=0)[0, 0]
        preds.append(scaler_y.inverse_transform([[y]])[0, 0])
        new_row = cur.iloc[-1:].copy()
        cur = pd.concat([cur.iloc[1:], new_row], ignore_index=True)
    return preds

last_window = test_df[feature_cols].tail(TIME_STEP)
next7_pred  = predict_next7(model, scaler_X, scaler_y, last_window, TIME_STEP)
next7_dates = [dates_test.iloc[-1] + timedelta(days=i+1) for i in range(7)]

# --------------------------------------------------
# 10. 打印结果
# --------------------------------------------------
print("\n=== 后续 7 日客流量预测 ===")
for d, p in zip(next7_dates, next7_pred):
    print(f"{d.strftime('%Y-%m-%d')}: {p:.0f} 人")

# 未来 7 天准确率参考（用测试集最后 3 天误差代替）
if len(y_test_true) >= 3:
    last3_true = y_test_true[-3:]
    last3_pred = y_test_pred[-3:]
    future_mape = np.mean(np.abs((last3_true - last3_pred) / (last3_true + 1e-8))) * 100
else:
    future_mape = "N/A (Insufficient data)"

print("\n=== 未来七天预测准确率参考（基于测试集最后几天）===")
print(f"准确率: {future_mape if isinstance(future_mape, str) else f'{100 - future_mape:.2f}%'}")
print("(注意: 这是基于测试集最后几天的参考值，不是真实未来数据的准确率)")

# 模型评估
print("\n=== 模型评估 ===")
print(f"Train MSE: {tr_mse:.4f} | MAE: {tr_mae:.4f} | RMSE: {tr_rmse:.4f} | MAPE: {tr_mape:.2f}%")
print(f"Test  MSE: {te_mse:.4f} | MAE: {te_mae:.4f} | RMSE: {te_rmse:.4f} | MAPE: {te_mape:.2f}%")

# --------------------------------------------------
# 11. 可视化
# --------------------------------------------------
plt.figure(figsize=(15, 10))

# loss 曲线
plt.subplot(2, 1, 1)
plt.plot(history.history['loss'], label='Train Loss')
plt.plot(history.history['val_loss'], label='Val Loss')
plt.title('Loss Curve'); plt.ylabel('MSE'); plt.legend(); plt.grid()

# 测试集真实 vs 预测 + 未来 7 天
plt.subplot(2, 1, 2)
test_dates_cut = dates_test[TIME_STEP:].reset_index(drop=True)
plt.plot(test_dates_cut, y_test_true, label='True', color='green', alpha=0.7)
plt.plot(test_dates_cut, y_test_pred, label='Predicted', color='red', ls='--', alpha=0.7)
plt.plot(next7_dates, next7_pred, label='Next-7-days', color='orange', marker='o', ls='-.')
plt.title('Visitor Count – Test Set & Next 7 Days'); plt.ylabel('Count'); plt.legend(); plt.grid()
plt.tight_layout()
plt.show()

# --------------------------------------------------
# 12. 单独柱状图：未来 7 日客流量预测
# --------------------------------------------------
plt.figure(figsize=(8, 5))
bars = plt.bar(range(len(next7_dates)), next7_pred, color='skyblue', edgecolor='navy')
# 数值标签
for bar, val in zip(bars, next7_pred):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height()+1,
             f'{val:.0f}', ha='center', va='bottom')
plt.xticks(range(len(next7_dates)), [d.strftime('%m-%d') for d in next7_dates])
plt.title('Next 7-Day Visitor Count Forecast')
plt.xlabel('Date')
plt.ylabel('Predicted Visitors')
plt.grid(axis='y', ls='--', alpha=0.7)
plt.tight_layout()
plt.show()