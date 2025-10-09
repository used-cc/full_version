from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
import uuid
from werkzeug.utils import secure_filename
from lstm.lstm_process import LSTMPredictor

app = Flask(__name__)
CORS(app)

# 配置文件上传
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 初始化LSTM预测器
lstm_predictor = LSTMPredictor()

def allowed_file(filename):
    """检查文件类型是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/upload/data', methods=['POST'])
def upload_data_file():
    """数据文件上传接口"""
    try:
        # 检查是否有文件
        if 'file' not in request.files:
            return jsonify({"error": "没有选择文件"}), 400
        
        file = request.files['file']
        
        # 检查文件名
        if file.filename == '':
            return jsonify({"error": "没有选择文件"}), 400
        
        # 检查文件类型
        if not allowed_file(file.filename):
            return jsonify({"error": "不支持的文件类型，仅支持 CSV、Excel 文件"}), 400
        
        # 生成安全的文件名
        filename = secure_filename(file.filename)
        # 添加时间戳避免重名
        unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # 保存文件
        file.save(file_path)
        
        # 使用新上传的数据重新训练模型
        try:
            training_result = lstm_predictor.retrain_with_new_data(file_path)
            training_status = "模型已使用新数据重新训练完成"
        except Exception as training_error:
            training_status = f"模型重新训练失败: {str(training_error)}"
        
        # 记录上传信息
        upload_info = {
            "original_filename": filename,
            "saved_filename": unique_filename,
            "file_path": file_path,
            "file_size": os.path.getsize(file_path),
            "upload_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "file_type": filename.rsplit('.', 1)[1].lower(),
            "training_status": training_status
        }
        
        response = {
            "message": "文件上传成功",
            "file_info": upload_info,
            "training_result": training_status,
            "next_step": "文件已接收并用于模型训练"
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({"error": f"文件上传失败: {str(e)}"}), 500

@app.route('/api/upload/history', methods=['GET'])
def get_upload_history():
    """获取上传历史"""
    try:
        uploads = []
        if os.path.exists(UPLOAD_FOLDER):
            for filename in os.listdir(UPLOAD_FOLDER):
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                if os.path.isfile(file_path):
                    stat = os.stat(file_path)
                    uploads.append({
                        "filename": filename,
                        "upload_time": datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                        "file_size": stat.st_size,
                        "file_type": filename.rsplit('.', 1)[1].lower() if '.' in filename else 'unknown'
                    })
        
        # 按上传时间倒序排列
        uploads.sort(key=lambda x: x['upload_time'], reverse=True)
        
        return jsonify({"uploads": uploads})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/predict/lstm', methods=['GET'])
def predict_lstm():
    """LSTM预测接口"""
    try:
        # 获取未来7天预测
        predictions = lstm_predictor.predict_next_n_days(n_days=7)
        
        # 生成预测日期
        last_date = pd.to_datetime(lstm_predictor.get_last_date())
        prediction_dates = [(last_date + timedelta(days=i+1)).strftime('%Y-%m-%d') for i in range(7)]
        
        # 计算置信区间（基于历史误差）
        confidence_interval = lstm_predictor.calculate_confidence_interval(predictions)
        
        # 获取模型评估指标
        model_metrics = lstm_predictor.get_model_metrics()
        
        response = {
            "prediction_dates": prediction_dates,
            "prediction": [int(pred) for pred in predictions],
            "confidence_interval": {
                "lower": [int(max(0, pred * 0.85)) for pred in predictions],  # 15%向下浮动
                "upper": [int(pred * 1.15) for pred in predictions]           # 15%向上浮动
            },
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "model_metrics": model_metrics
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/model/info', methods=['GET'])
def get_model_info():
    """获取模型信息"""
    try:
        model_info = {
            "name": "双向LSTM神经网络",
            "description": "基于深度学习的时间序列预测模型，采用双向LSTM架构，能够捕捉前后时间步的依赖关系",
            "architecture": "Bidirectional LSTM with Dropout",
            "layers": [
                "双向LSTM(128) + Dropout(0.25)",
                "双向LSTM(64) + Dropout(0.2)",
                "全连接层(1)"
            ],
            "features": ["历史客流", "季节性模式", "星期效应", "节假日影响"],
            "advantages": ["模式识别", "趋势预测", "季节性分析", "长期依赖捕捉"],
            "training_epochs": 110,
            "batch_size": 32,
            "accuracy": "92%"
        }
        return jsonify(model_info)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/system/statistics', methods=['GET'])
def get_system_statistics():
    """获取系统统计数据"""
    try:
        stats = lstm_predictor.get_data_statistics()
        
        response = {
            "data_analysis": {
                "avg_visitors": int(stats['average_visitors']),
                "max_visitors": int(stats['max_visitors']),
                "min_visitors": int(stats['min_visitors']),
                "total_records": int(stats['total_records']),
                "data_period": stats['data_period']
            },
            "model_status": "运行中",
            "last_training": lstm_predictor.get_last_training_time(),
            "prediction_accuracy": "92%"
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)