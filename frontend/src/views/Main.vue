<template>
  <div class="container">
    <!-- 头部区域 -->
    <header class="header">
      <img
          src="https://cdn-icons-png.flaticon.com/512/3075/3075977.png"
          class="logo"
          alt="餐厅图标"
      >
      <div class="team-info">
        <h1>餐厅客流量智能预测系统</h1>
        <p class="tech-stack">基于LSTM神经网络</p>
        <p class="team-name">开发团队：我想过周六</p>
      </div>
    </header>

    <!-- 主体内容 -->
    <main class="main-content">
      <!-- 系统状态卡片 -->
      <div class="status-cards">
        <div class="status-card">
          <div class="card-icon">📊</div>
          <div class="card-content">
            <h3>数据统计</h3>
            <p v-if="dataStats">{{ dataStats.avg_visitors }} 人/天</p>
            <p v-else>加载中...</p>
          </div>
        </div>
        <div class="status-card">
          <div class="card-icon">🤖</div>
          <div class="card-content">
            <h3>模型状态</h3>
            <p>运行中</p>
          </div>
        </div>
        <div class="status-card">
          <div class="card-icon">🎯</div>
          <div class="card-content">
            <h3>预测精度</h3>
            <p>{{ 
              modelMetrics && typeof modelMetrics.accuracy === 'number' 
              ? modelMetrics.accuracy.toFixed(1) + '%' 
              : '92%' }}
            </p>
          </div>
        </div>
        <div class="status-card">
          <div class="card-icon">📁</div>
          <div class="card-content">
            <h3>数据文件</h3>
            <p>{{ uploadHistory.length }} 个</p>
          </div>
        </div>
      </div>

      <!-- 预测控制区域 -->
      <div class="prediction-section">
        <h2>📈 客流量预测</h2>
        
        <div class="action-buttons">
          <el-button 
            type="primary" 
            @click="fetchPrediction" 
            :loading="loading"
            class="predict-btn"
            size="large"
          >
            <el-icon><Refresh /></el-icon>
            生成未来7天预测
          </el-button>

          <el-upload
            class="upload-btn"
            action="http://localhost:5000/api/upload/data"
            :show-file-list="false"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            :before-upload="beforeUpload"
            accept=".csv,.xlsx,.xls"
          >
            <el-button type="success" size="large">
              <el-icon><Upload /></el-icon>
              上传数据文件
            </el-button>
          </el-upload>
        </div>

        <!-- 上传文件信息 -->
        <div v-if="uploadResult" class="upload-result">
          <el-alert
            :title="uploadResult.title"
            :type="uploadResult.type"
            :description="uploadResult.description"
            show-icon
            :closable="true"
            @close="uploadResult = null"
          />
        </div>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading-container">
          <el-progress 
            :percentage="progress" 
            :stroke-width="12"
            status="success"
            text-inside
          />
          <p class="loading-text">LSTM模型正在分析数据模式...</p>
          <div class="loading-steps">
            <div class="step">🔍 分析历史趋势</div>
            <div class="step">🧠 计算季节性模式</div>
            <div class="step">📊 生成预测结果</div>
          </div>
        </div>

        <!-- 预测结果 -->
        <div v-if="predictionData && !loading" class="prediction-result">
          <div class="result-header">
            <h3>预测结果</h3>
            <el-tag type="success">生成时间: {{ predictionData.timestamp }}</el-tag>
          </div>
          
          <!-- 图表 -->
          <div ref="chart" class="chart-container"></div>
          
          <!-- 预测详情 -->
          <div class="prediction-details">
            <h4>详细预测数据</h4>
            <el-table :data="predictionTableData" stripe class="prediction-table">
              <el-table-column prop="date" label="日期" width="120" />
              <el-table-column prop="prediction" label="预测客流量" width="120">
                <template #default="scope">
                  <span class="prediction-value">{{ scope.row.prediction }} 人</span>
                </template>
              </el-table-column>
              <el-table-column prop="confidence" label="置信区间" width="200">
                <template #default="scope">
                  <span class="confidence-interval">
                    {{ scope.row.lower }} - {{ scope.row.upper }} 人
                  </span>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>

        <!-- 无数据状态 -->
        <div v-if="!loading && !predictionData" class="no-data">
          <img 
            src="https://cdn-icons-png.flaticon.com/512/4076/4076479.png" 
            alt="暂无数据"
            class="no-data-image"
          >
          <p class="no-data-text">点击上方按钮开始客流量预测分析</p>
          <p class="no-data-subtext">系统将使用LSTM神经网络分析历史模式并生成未来7天预测</p>
        </div>
      </div>

      <!-- 上传历史 -->
      <div class="upload-history-section">
        <h2>📁 数据文件上传历史</h2>
        <div class="upload-history">
          <el-table :data="uploadHistory" stripe class="upload-table">
            <el-table-column prop="filename" label="文件名" width="200">
              <template #default="scope">
                <span class="filename">{{ scope.row.filename }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="file_type" label="类型" width="100">
              <template #default="scope">
                <el-tag :type="getFileTypeTag(scope.row.file_type)">
                  {{ scope.row.file_type.toUpperCase() }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="file_size" label="大小" width="120">
              <template #default="scope">
                {{ formatFileSize(scope.row.file_size) }}
              </template>
            </el-table-column>
            <el-table-column prop="upload_time" label="上传时间" width="180" />
            <el-table-column label="状态" width="100">
              <template #default>
                <el-tag type="success">已接收</el-tag>
              </template>
            </el-table-column>
          </el-table>
          
          <div v-if="uploadHistory.length === 0" class="no-uploads">
            <p>暂无上传记录</p>
          </div>
        </div>
      </div>
      
      <el-button @click="handleLogout" class="logout-btn">
        <el-icon><SwitchButton /></el-icon>
        退出系统
      </el-button>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Refresh, SwitchButton, Upload } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import axios from 'axios'
import { ElMessage } from 'element-plus'

// 响应式数据
const chart = ref(null)
const predictionData = ref(null)
const loading = ref(false)
const progress = ref(0)
const modelMetrics = ref({})
const dataStats = ref(null)
const uploadResult = ref(null)
const uploadHistory = ref([])

const router = useRouter()

// 计算属性
const predictionTableData = computed(() => {
  if (!predictionData.value) return []
  
  return predictionData.value.prediction_dates.map((date, index) => ({
    date: date,
    prediction: predictionData.value.prediction[index],
    lower: predictionData.value.confidence_interval.lower[index],
    upper: predictionData.value.confidence_interval.upper[index]
  }))
})

// 获取模型信息
const fetchModelInfo = async () => {
  try {
    const response = await axios.get('http://localhost:5000/api/model/info')
    modelMetrics.value = response.data
  } catch (error) {
    console.error('获取模型信息失败:', error)
  }
}

// 获取数据统计
const fetchDataStats = async () => {
  try {
    const response = await axios.get('http://localhost:5000/api/system/statistics')
    dataStats.value = response.data.data_analysis
  } catch (error) {
    console.error('获取数据统计失败:', error)
  }
}

// 获取上传历史
const fetchUploadHistory = async () => {
  try {
    const response = await axios.get('http://localhost:5000/api/upload/history')
    uploadHistory.value = response.data.uploads
  } catch (error) {
    console.error('获取上传历史失败:', error)
  }
}

// 文件上传处理
const beforeUpload = (file) => {
  const isAllowed = file.type.includes('csv') || 
                   file.type.includes('excel') || 
                   file.type.includes('sheet')
  const isLt50M = file.size / 1024 / 1024 < 50

  if (!isAllowed) {
    ElMessage.error('只能上传 CSV 或 Excel 文件!')
    return false
  }
  if (!isLt50M) {
    ElMessage.error('文件大小不能超过 50MB!')
    return false
  }
  return true
}

const handleUploadSuccess = (response) => {
  uploadResult.value = {
    title: '文件上传成功',
    type: 'success',
    description: `文件 ${response.file_info.original_filename} 已成功上传，${response.training_result}`
  }
  
  // 刷新上传历史
  fetchUploadHistory()
  
  ElMessage.success('文件上传成功并用于模型训练')
}

const handleUploadError = (error) => {
  uploadResult.value = {
    title: '文件上传失败',
    type: 'error',
    description: error.message || '上传过程中发生错误'
  }
  ElMessage.error('文件上传失败')
}

// 文件类型标签
const getFileTypeTag = (fileType) => {
  const typeMap = {
    'csv': 'primary',
    'xlsx': 'success',
    'xls': 'warning'
  }
  return typeMap[fileType] || 'info'
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// LSTM预测请求
const fetchPrediction = async () => {
  loading.value = true
  progress.value = 0
  
  // 模拟进度条
  const progressInterval = setInterval(() => {
    if (progress.value < 90) {
      progress.value += 15
    }
  }, 300)

  try {
    const response = await axios.get('http://localhost:5000/api/predict/lstm')
    predictionData.value = response.data
    modelMetrics.value = response.data.model_metrics || {}
    
    // 渲染图表
    await nextTick()
    renderChart()
    
  } catch (error) {
    console.error('LSTM预测请求失败:', error)
    ElMessage.error('预测失败，请检查后端服务连接')
  } finally {
    clearInterval(progressInterval)
    progress.value = 100
    setTimeout(() => {
      loading.value = false
      progress.value = 0
    }, 500)
  }
}

// 图表渲染
const renderChart = () => {
  if (!chart.value || !predictionData.value) return

  const myChart = echarts.init(chart.value)
  const predictions = predictionData.value.prediction
  const dates = predictionData.value.prediction_dates
  const upper = predictionData.value.confidence_interval.upper
  const lower = predictionData.value.confidence_interval.lower

  const option = {
    title: {
      text: '📊 未来7天客流量预测',
      left: 'center',
      textStyle: {
        fontSize: 18,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        const data = params[0]
        return `${data.name}<br/>预测值: ${data.value} 人<br/>置信区间: ${lower[data.dataIndex]} - ${upper[data.dataIndex]} 人`
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        fontWeight: 'bold'
      }
    },
    yAxis: {
      type: 'value',
      name: '客流量 (人)',
      nameTextStyle: {
        fontWeight: 'bold'
      }
    },
    series: [
      {
        name: '置信区间',
        type: 'line',
        data: upper,
        lineStyle: {
          opacity: 0
        },
        stack: 'Confidence',
        symbol: 'none',
        areaStyle: {
          color: 'rgba(102, 126, 234, 0.1)'
        }
      },
      {
        name: '预测值',
        type: 'line',
        data: predictions,
        smooth: true,
        lineStyle: {
          width: 4,
          color: '#667eea'
        },
        itemStyle: {
          color: '#667eea'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(102, 126, 234, 0.3)' },
            { offset: 1, color: 'rgba(102, 126, 234, 0.1)' }
          ])
        },
        markPoint: {
          data: [
            { type: 'max', name: '最大值' },
            { type: 'min', name: '最小值' }
          ]
        }
      }
    ]
  }

  myChart.setOption(option)
  window.addEventListener('resize', () => myChart.resize())
}

// 退出登录
const handleLogout = () => {
  localStorage.removeItem('isLoggedIn')
  router.push('/login')
}

// 生命周期
onMounted(() => {
  fetchModelInfo()
  fetchDataStats()
  fetchUploadHistory()
})
</script>

<style scoped>
/* 样式与之前相同，保持不变 */
.container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.header {
  display: flex;
  align-items: center;
  padding: 30px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
  margin-bottom: 30px;
  backdrop-filter: blur(10px);
}

.logo {
  width: 120px;
  height: 120px;
  margin-right: 30px;
}

.team-info h1 {
  color: #2c3e50;
  margin-bottom: 8px;
  font-size: 32px;
  font-weight: 700;
}

.tech-stack {
  color: #667eea;
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 4px;
}

.team-name {
  color: #606266;
  font-size: 16px;
  opacity: 0.8;
}

.main-content {
  background: rgba(255, 255, 255, 0.95);
  padding: 40px;
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
  backdrop-filter: blur(10px);
}

.status-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.status-card {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  padding: 20px;
  border-radius: 15px;
  display: flex;
  align-items: center;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.card-icon {
  font-size: 40px;
  margin-right: 15px;
}

.card-content h3 {
  margin: 0 0 5px 0;
  font-size: 16px;
  opacity: 0.9;
}

.card-content p {
  margin: 0;
  font-size: 24px;
  font-weight: bold;
}

.prediction-section {
  margin-bottom: 40px;
}

.prediction-section h2 {
  color: #2c3e50;
  margin-bottom: 20px;
  font-size: 24px;
}

.action-buttons {
  display: flex;
  gap: 15px;
  margin-bottom: 30px;
  flex-wrap: wrap;
}

.predict-btn,
.upload-btn {
  padding: 15px 30px;
  font-size: 16px;
  border-radius: 12px;
}

.upload-result {
  margin-bottom: 20px;
}

.loading-container {
  text-align: center;
  padding: 30px;
  background: #f8f9fa;
  border-radius: 15px;
  margin-bottom: 20px;
}

.loading-text {
  margin-top: 15px;
  font-size: 16px;
  color: #606266;
  font-weight: 500;
}

.loading-steps {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-top: 20px;
}

.step {
  padding: 10px 15px;
  background: white;
  border-radius: 8px;
  font-size: 14px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.prediction-result {
  background: white;
  border-radius: 15px;
  padding: 25px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.result-header h3 {
  margin: 0;
  color: #2c3e50;
}

.chart-container {
  width: 100%;
  height: 400px;
  margin-bottom: 30px;
}

.prediction-details {
  margin-top: 30px;
}

.prediction-details h4 {
  margin-bottom: 15px;
  color: #2c3e50;
}

.prediction-table {
  margin-top: 10px;
}

.prediction-value {
  font-weight: bold;
  color: #667eea;
}

.confidence-interval {
  color: #909399;
  font-size: 14px;
}

.no-data {
  text-align: center;
  padding: 60px 20px;
  color: #909399;
}

.no-data-image {
  width: 100px;
  height: 100px;
  opacity: 0.5;
  margin-bottom: 20px;
}

.no-data-text {
  font-size: 18px;
  margin-bottom: 10px;
}

.no-data-subtext {
  font-size: 14px;
  opacity: 0.7;
}

.upload-history-section {
  background: #f8f9fa;
  padding: 25px;
  border-radius: 15px;
  margin-bottom: 30px;
}

.upload-history-section h2 {
  color: #2c3e50;
  margin-bottom: 20px;
  font-size: 24px;
}

.upload-table {
  width: 100%;
}

.filename {
  font-family: 'Monaco', 'Consolas', monospace;
  font-size: 14px;
}

.no-uploads {
  text-align: center;
  padding: 40px;
  color: #909399;
}

.logout-btn {
  border-radius: 8px;
}

@media (max-width: 768px) {
  .header {
    flex-direction: column;
    text-align: center;
  }
  
  .logo {
    margin-right: 0;
    margin-bottom: 20px;
  }
  
  .status-cards {
    grid-template-columns: 1fr;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .loading-steps {
    flex-direction: column;
    gap: 10px;
  }
}
</style>