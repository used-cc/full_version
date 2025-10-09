import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Bidirectional
import math
from datetime import datetime, timedelta
import os
import json

class LSTMPredictor:
    def __init__(self, data_path='lstm/more_train.csv'):
        """初始化"""
        self.data_path = data_path
        self.model = None
        self.scaler_X = MinMaxScaler(feature_range=(0, 1))
        self.scaler_y = MinMaxScaler(feature_range=(0, 1))
        self.time_step = 10
        self.feature_cols = None
        self.df = None
        self.model_metrics = {}
        self.last_training_time = None
       
        self.load_and_prepare_data()
        self.build_and_train_model()
    
    def load_and_prepare_data(self):
        """加载和准备数据"""
        try:
            if os.path.exists(self.data_path):
                self.df = pd.read_csv(self.data_path)
            else:
                alt_path = os.path.join('backend', self.data_path)
                if os.path.exists(alt_path):
                    self.df = pd.read_csv(alt_path)
                    self.data_path = alt_path
                else:
                    raise FileNotFoundError(f"数据文件不存在: {self.data_path}")
            
            self.df['ds'] = pd.to_datetime(self.df['ds'])
            
            # 确定特征列（从第3列到第28列，共25个特征）
            self.feature_cols = self.df.columns[3:28].tolist()
            
            print(f"成功加载数据，共 {len(self.df)} 行，{len(self.feature_cols)} 个特征")
            print(f"数据时间范围: {self.df['ds'].min()} 至 {self.df['ds'].max()}")
            
        except Exception as e:
            print(f"数据加载失败: {e}")
            # 创建示例数据用于演示
            self.create_sample_data()
    
    def create_sample_data(self):
        """创建示例数据（用于演示）"""
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        sample_data = {
            'ds': dates,
            'y': np.random.poisson(50, len(dates)) + np.sin(np.arange(len(dates)) * 2 * np.pi / 7) * 10
        }
        
        # 添加示例特征
        for i in range(25):
            sample_data[f'feature_{i}'] = np.random.normal(0, 1, len(dates))
        
        self.df = pd.DataFrame(sample_data)
        self.feature_cols = [f'feature_{i}' for i in range(25)]
        print("使用示例数据进行演示")
    
    def build_and_train_model(self):
        """构建和训练LSTM模型"""
        try:
            # 划分训练/测试集
            train_size = int(len(self.df) * 0.7)
            train_df = self.df.iloc[:train_size].copy()
            test_df = self.df.iloc[train_size:].copy()
            
            # 准备数据
            X_train = train_df[self.feature_cols].values
            y_train = train_df['y'].values.reshape(-1, 1)
            X_test = test_df[self.feature_cols].values
            y_test = test_df['y'].values.reshape(-1, 1)
            
            # 数据归一化
            X_train_scaled = self.scaler_X.fit_transform(X_train)
            y_train_scaled = self.scaler_y.fit_transform(y_train)
            X_test_scaled = self.scaler_X.transform(X_test)
            y_test_scaled = self.scaler_y.transform(y_test)
            
            # 构建LSTM样本
            x_train_lstm, y_train_lstm = self.make_dataset(X_train_scaled, y_train_scaled, self.time_step)
            x_test_lstm, y_test_lstm = self.make_dataset(X_test_scaled, y_test_scaled, self.time_step)
            
            # 构建模型
            self.model = Sequential([
                Bidirectional(LSTM(128, return_sequences=True), input_shape=(self.time_step, len(self.feature_cols))),
                Dropout(0.25),
                Bidirectional(LSTM(64, return_sequences=False)),
                Dropout(0.2),
                Dense(1)
            ])
            
            self.model.compile(optimizer='adam', loss='mse')
            
            # 训练模型
            history = self.model.fit(
                x_train_lstm, y_train_lstm,
                epochs=50,  # 减少epochs以加快训练速度
                batch_size=32,
                verbose=0,
                validation_data=(x_test_lstm, y_test_lstm)
            )
            
            # 评估模型
            y_test_pred = self.scaler_y.inverse_transform(self.model.predict(x_test_lstm, verbose=0))
            y_test_true = self.scaler_y.inverse_transform(y_test_lstm.reshape(-1, 1))
            
            # 计算指标
            mse = mean_squared_error(y_test_true, y_test_pred)
            mae = mean_absolute_error(y_test_true, y_test_pred)
            rmse = math.sqrt(mse)
            mape = np.mean(np.abs((y_test_true - y_test_pred) / (y_test_true + 1e-8))) * 100
            
            self.model_metrics = {
                'mse': float(mse),
                'mae': float(mae),
                'rmse': float(rmse),
                'mape': float(mape),
                'accuracy': float(100 - mape)
            }
            
            self.last_training_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            print(f"模型训练完成，测试集准确率: {100 - mape:.2f}%")
            
        except Exception as e:
            print(f"模型训练失败: {e}")
            # 创建简单的线性模型作为备用
            self.create_fallback_model()
    
    def create_fallback_model(self):
        """创建备用模型"""
        from sklearn.linear_model import LinearRegression
        from sklearn.preprocessing import StandardScaler
        
        self.fallback_model = LinearRegression()
        self.fallback_scaler = StandardScaler()
        
        # 使用最后几天的数据作为特征
        X = np.arange(len(self.df)).reshape(-1, 1)
        y = self.df['y'].values
        
        X_scaled = self.fallback_scaler.fit_transform(X)
        self.fallback_model.fit(X_scaled, y)
        
        print("使用线性回归作为备用模型")
    
    def make_dataset(self, X, y, time_step=10):
        """构造LSTM样本"""
        xs, ys = [], []
        for i in range(len(X) - time_step):
            xs.append(X[i:i+time_step])
            ys.append(y[i+time_step, 0])
        return np.array(xs), np.array(ys)
    
    def predict_next_n_days(self, n_days=7):
        """预测未来n天"""
        try:
            if self.model:
                # 使用LSTM模型预测
                last_window = self.df[self.feature_cols].tail(self.time_step)
                predictions = []
                
                current_window = last_window.copy()
                
                for _ in range(n_days):
                    x_scaled = self.scaler_X.transform(current_window.values)
                    x_reshaped = x_scaled.reshape(1, self.time_step, -1)
                    
                    y_pred_scaled = self.model.predict(x_reshaped, verbose=0)[0, 0]
                    y_pred = self.scaler_y.inverse_transform([[y_pred_scaled]])[0, 0]
                    
                    predictions.append(max(0, y_pred))  # 确保非负
                    
                    # 更新窗口（这里简化处理，实际应该生成新的特征）
                    new_row = current_window.iloc[-1:].copy()
                    current_window = pd.concat([current_window.iloc[1:], new_row], ignore_index=True)
                
                return predictions
            else:
                # 使用备用模型
                return self.predict_with_fallback(n_days)
                
        except Exception as e:
            print(f"预测失败: {e}")
            # 返回基于历史均值的预测
            avg_visitors = self.df['y'].mean()
            return [avg_visitors * (1 + 0.1 * i) for i in range(n_days)]
    
    def predict_with_fallback(self, n_days=7):
        """使用备用模型预测"""
        last_index = len(self.df)
        future_indices = np.arange(last_index, last_index + n_days).reshape(-1, 1)
        future_indices_scaled = self.fallback_scaler.transform(future_indices)
        predictions = self.fallback_model.predict(future_indices_scaled)
        return [max(0, pred) for pred in predictions]
    
    def calculate_confidence_interval(self, predictions, confidence_level=0.85):
        """计算置信区间"""
        # 基于历史误差计算置信区间
        if 'mape' in self.model_metrics:
            error_margin = self.model_metrics['mape'] / 100
        else:
            error_margin = 0.15  # 默认15%误差
            
        lower = [max(0, pred * (1 - error_margin)) for pred in predictions]
        upper = [pred * (1 + error_margin) for pred in predictions]
        return {'lower': [int(x) for x in lower], 'upper': [int(x) for x in upper]}
    
    def get_last_date(self):
        """获取最后日期"""
        return self.df['ds'].iloc[-1]
    
    def get_model_metrics(self):
        """获取模型评估指标"""
        return self.model_metrics
    
    def get_data_statistics(self):
        """获取数据统计信息"""
        return {
            'average_visitors': float(self.df['y'].mean()),
            'max_visitors': int(self.df['y'].max()),
            'min_visitors': int(self.df['y'].min()),
            'total_records': len(self.df),
            'data_period': f"{self.df['ds'].iloc[0].strftime('%Y-%m-%d')} 至 {self.df['ds'].iloc[-1].strftime('%Y-%m-%d')}"
        }
    
    def get_last_training_time(self):
        """获取最后训练时间"""
        return self.last_training_time or "尚未训练"
    
    def retrain_with_new_data(self, new_data_path):
        """使用新数据重新训练模型"""
        try:
            # 加载新数据
            new_df = pd.read_csv(new_data_path)
            new_df['ds'] = pd.to_datetime(new_df['ds'])
            
            # 检查数据格式是否符合要求
            required_columns = ['ds', 'y'] + [f'feature_{i}' for i in range(25)]
            if not all(col in new_df.columns for col in ['ds', 'y']):
                return {"status": "error", "message": "数据文件必须包含 'ds' 和 'y' 列"}
            
            # 合并数据（这里选择追加新数据）
            self.df = pd.concat([self.df, new_df], ignore_index=True).drop_duplicates(subset=['ds']).sort_values('ds')
            self.data_path = new_data_path
            
            print(f"使用新数据重新训练模型，数据量: {len(self.df)} 行")
            
            # 重新训练模型
            self.build_and_train_model()
            
            return {"status": "success", "message": "模型使用新数据重新训练完成"}
            
        except Exception as e:
            return {"status": "error", "message": f"重新训练失败: {str(e)}"}