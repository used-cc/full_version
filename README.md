餐厅客流量智能预测系统
一、项目简介
    餐厅客流量智能预测系统是一个基于深度学习的全栈Web应用，采用双向LSTM神经网络对餐厅客流量进行精准预测。系统结合了现代Web技术和机器学习算法，为餐厅管理者提供未来7天的客流量预测，辅助经营决策。

二、核心特性
    智能预测: 基于双向LSTM神经网络的时间序列预测
    数据可视化: 使用ECharts展示预测结果和趋势分析
    文件上传: 支持CSV/Excel格式数据上传和模型重训练
    用户友好: 现代化UI设计，响应式布局
    实时监控: 系统状态、模型精度实时展示

三、技术架构
    1、前端技术栈
        Vue 3 - 渐进式JavaScript框架
        Element Plus - UI组件库
        ECharts 5 - 数据可视化图表
        Vue Router 4 - 路由管理
        Axios - HTTP请求库
        Vite - 前端构建工具
    2、后端技术栈
        Flask - Python Web框架
        TensorFlow/Keras - 深度学习框架
        LSTM神经网络 - 时间序列预测模型
        Pandas/NumPy - 数据处理
        Scikit-learn - 机器学习工具
        Flask-CORS - 跨域支持

四、项目结构
full/
├── backend/                  # 后端服务
│   ├── app.py                # Flask主应用
│   ├── requirements.txt      # Python依赖
│   ├── lstm/                 # LSTM模型模块
│   │   ├── lstm_process.py   # LSTM预测器
│   │   ├── best_model.h5     # 预训练模型
│   │   ├── more_train.csv    # 训练数据
│   │   └── more_test.csv     # 测试数据
│   └── uploads/              # 文件上传目录
└── frontend/                 # 前端应用
    ├── src/
    │   ├── views/            # 页面组件
    │   │   ├── Login.vue     # 登录页
    │   │   └── Main.vue      # 主页面
    │   ├── router/           # 路由配置
    │   ├── assets/           # 静态资源
    │   ├── App.vue           # 根组件
    │   └── main.js           # 入口文件
    ├── package.json          # 前端依赖
    └── vite.config.js        # Vite配置

五、构建方式
    1、环境要求
        Python 3.8+
        Node.js 16+
        npm包管理器
    2、后端部署
        进入后端目录cd backend
        创建虚拟环境python -m venv venv    source venv/bin/activate（for Linux/Mac）    或       venv\Scripts\activate（for windows）
        安装Python依赖pip install -r requirements.txt
        启动后端服务python app.py
        后端服务将在 http://localhost:5000 启动，API文档可通过访问 /api/health 验证服务状态
    3、前端部署
        进入前端目录cd frontend
        安装Node.js依赖npm install
        启动开发服务器npm run dev
        应用将在http://localhost:5173启动
        支持热重载开发模式，构建生产版本npm run build
        
六、配置说明
    1.后端配置
        端口: 5000
        文件上传: 支持CSV/Excel，最大50MB
        模型配置: 双向LSTM，128+64神经元，Dropout正则化
        预测周期: 默认7天
    2.前端配置
        端口: 5173
        API代理: 通过Vite代理到后端服务
        路由模式: History模式

七、系统功能
    1.用户认证：简洁的登录界面、本地存储认证状态、路由守卫保护
    2.预测分析
        LSTM预测: 未来7天客流量预测
        置信区间: 85%置信度区间展示
        可视化图表: 交互式趋势图表
        详细数据: 表格形式展示预测结果
    3.数据管理
        文件上传: 支持CSV/Excel格式
        模型重训练: 基于新数据自动更新模型
        上传历史: 文件管理记录
        数据统计: 基本数据分析展示
    4.用户界面
        响应式设计: 适配不同屏幕尺寸
        现代化UI: Element Plus组件库
        状态卡片: 系统关键指标展示
        加载动画: 等待提示
    5.LSTM模型
        模型架构：双向LSTM(128) → Dropout(0.25) → 双向LSTM(64) → Dropout(0.2) → 全连接层(1)
        特征工程
        历史客流数据
        季节性模式识别
        星期效应分析
        节假日影响因子
        性能指标：准确率、训练周期: 50-110 epochs、批大小: 32、损失函数: MSE

八、API接口
    POST /api/upload/data - 数据文件上传
    GET /api/predict/lstm - LSTM预测
    GET /api/model/info - 模型信息
    GET /api/system/statistics - 系统统计
    GET /api/upload/history - 上传历史

九、使用说明
    ==>登录系统
    ==>输入任意账号密码进行伪登录
    ==>查看预测
    ==>点击"生成未来7天预测"获取最新预测结果
    ==>上传数据
    ==>通过"上传数据文件"更新训练数据
    ==>系统将自动重新训练模型
    ==>监控状态
    ==>查看系统状态卡片了解关键指标
    ==>监控模型精度和数据处理状态

十、未来规划
    实时数据流处理
    多餐厅数据支持
    移动端适配
    预测结果导出
    模型性能监控面板
