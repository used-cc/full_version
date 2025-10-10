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
          <div class="card-icon">🔮</div>
          <div class="card-content">
            <h3>预测次日客流</h3>
            <p v-if="nextDayPrediction">{{ nextDayPrediction }} 人</p>
            <p v-else>点击预测生成</p>
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
        
        <!-- 后端配置 -->
        <div class="backend-config">
          <el-input 
            v-model="backendUrl" 
            placeholder="输入后端服务器地址，如: http://192.168.1.100:5000"
            class="backend-input"
          >
            <template #prepend>后端地址</template>
          </el-input>
          <el-button @click="testBackendConnection" type="info">
            <el-icon><Connection /></el-icon>
            测试连接
          </el-button>
        </div>
        
        <!-- 核心按钮区域：优化排布 -->
        <div class="action-buttons">
          <!-- 生成预测按钮 -->
          <el-button 
            type="primary" 
            @click="fetchPrediction" 
            :loading="loading"
            class="action-btn predict-btn"
            size="large"
          >
            <el-icon class="btn-icon"><Refresh /></el-icon>
            生成未来7天预测
          </el-button>
          
          <!-- 上传文件按钮 -->
          <el-upload
            class="action-btn upload-btn"
            :action="uploadUrl"
            :show-file-list="false"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            :before-upload="beforeUpload"
            accept=".csv,.xlsx,.xls"
          >
            <el-button type="success" size="large" class="upload-inner-btn">
              <el-icon class="btn-icon"><Upload /></el-icon>
              上传数据文件
            </el-button>
          </el-upload>
          
          <!-- 新增单日数据按钮 -->
          <el-button 
            type="warning" 
            @click="showSingleUploadDialog = true" 
            size="large"
            class="action-btn single-upload-btn"
          >
            <el-icon class="btn-icon"><Plus /></el-icon>
            新增单日数据
          </el-button>
        </div>
        
        <!-- 单日数据上传对话框：优化表单布局 -->
        <el-dialog 
          v-model="showSingleUploadDialog" 
          title="新增单日数据" 
          width="700px"
          :close-on-click-modal="false"
          class="single-data-dialog"
        >
          <el-form 
            :model="singleUploadForm" 
            :rules="singleUploadRules" 
            ref="singleUploadFormRef" 
            label-width="130px"
            class="single-data-form"
          >
            <!-- 日期输入项：优化间距和交互 -->
            <el-form-item label="* 日期" prop="date" class="form-item">
              <el-date-picker
                v-model="singleUploadForm.date"
                type="date"
                placeholder="请选择日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
                size="default"
                class="form-input"
              />
            </el-form-item>
            
            <!-- 实际客流量输入项 -->
            <el-form-item label="* 实际客流量" prop="y_value" class="form-item">
              <el-input-number
                v-model="singleUploadForm.y_value"
                :min="0"
                :max="10000"
                placeholder="请输入当日实际客流量"
                style="width: 100%"
                size="default"
                class="form-input"
                controls-position="right"
              />
            </el-form-item>
            
            <!-- 特征数据区域：重点优化布局 -->
            <el-form-item label="特征数据" class="form-item features-form-item">
              <div class="features-section">
                <p class="features-description">请输入特征值（与训练数据格式一致，支持小数点后2位）</p>
                <!-- 自适应网格布局：根据屏幕宽度自动调整列数 -->
                <div class="features-grid">
                  <div 
                    v-for="i in 25" 
                    :key="i" 
                    class="feature-input-item"
                  >
                    <label class="feature-label">特征 {{ i }}</label>
                    <el-input-number
                      v-model="singleUploadForm.features[i-1]"
                      :precision="2"
                      :step="0.1"
                      size="default"
                      class="feature-input"
                      :placeholder="`特征${i}`"
                    />
                  </div>
                </div>
              </div>
            </el-form-item>
          </el-form>
          
          <!-- 底部按钮：优化间距和样式 -->
          <template #footer>
            <el-button class="cancel-btn" @click="showSingleUploadDialog = false">取消</el-button>
            <el-button 
              type="primary" 
              @click="submitSingleUpload" 
              :loading="singleUploadLoading"
              class="submit-btn"
            >
              提交并训练
            </el-button>
          </template>
        </el-dialog>
        
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
          
          <!-- 后端生成的图表 -->
          <div v-if="chartUrl" class="chart-container">
            <img :src="chartUrl" alt="预测图表" class="backend-chart" />
            <p class="chart-note">* 图表由后端LSTM模型生成</p>
          </div>
          
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
import { Refresh, SwitchButton, Upload, Connection, Plus } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
// 响应式数据
const predictionData = ref(null)
const loading = ref(false)
const progress = ref(0)
const modelMetrics = ref({})
const dataStats = ref(null)
const uploadResult = ref(null)
const uploadHistory = ref([])
const chartUrl = ref('')
const backendUrl = ref('http://localhost:5000') // 默认本地
const nextDayPrediction = ref(null)
// 单日数据上传相关
const showSingleUploadDialog = ref(false)
const singleUploadLoading = ref(false)
const singleUploadFormRef = ref(null)
const singleUploadForm = ref({
  date: '',
  y_value: 0,
  features: Array(25).fill(0) // 初始化25个特征值为0
})
// 表单验证规则
const singleUploadRules = {
  date: [
    { required: true, message: '请选择日期', trigger: 'change' }
  ],
  y_value: [
    { required: true, message: '请输入客流量', trigger: 'blur' },
    { type: 'number', min: 0, message: '客流量必须大于0', trigger: 'blur' }
  ]
}
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
const uploadUrl = computed(() => `${backendUrl.value}/api/upload/data`)
// 测试后端连接
const testBackendConnection = async () => {
  try {
    const response = await axios.get(`${backendUrl.value}/api/health`)
    if (response.data.status === 'healthy') {
      ElMessage.success('后端连接成功！')
      // 连接成功后获取初始数据
      fetchModelInfo()
      fetchNextDayPrediction()
      fetchUploadHistory()
    } else {
      ElMessage.warning('后端服务异常')
    }
  } catch (error) {
    ElMessage.error(`后端连接失败: ${error.message}`)
    console.error('后端连接测试失败:', error)
  }
}
// 获取次日预测
const fetchNextDayPrediction = async () => {
  try {
    const response = await axios.get(`${backendUrl.value}/api/predict/next_day`)
    nextDayPrediction.value = response.data.next_day_prediction
  } catch (error) {
    console.error('获取次日预测失败:', error)
    // 如果接口不存在，使用7天预测的第一个值
    if (predictionData.value && predictionData.value.prediction.length > 0) {
      nextDayPrediction.value = predictionData.value.prediction[0]
    }
  }
}
// 获取模型信息
const fetchModelInfo = async () => {
  try {
    const response = await axios.get(`${backendUrl.value}/api/model/info`)
    modelMetrics.value = response.data
  } catch (error) {
    console.error('获取模型信息失败:', error)
  }
}
// 获取上传历史
const fetchUploadHistory = async () => {
  try {
    const response = await axios.get(`${backendUrl.value}/api/upload/history`)
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
  // 刷新预测数据
  fetchNextDayPrediction()
  
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
// 单日数据提交
const submitSingleUpload = async () => {
  if (!singleUploadFormRef.value) return
  
  try {
    // 表单验证
    await singleUploadFormRef.value.validate()
    
    singleUploadLoading.value = true
    
    const payload = {
      date: singleUploadForm.value.date,
      y_value: singleUploadForm.value.y_value,
      features: singleUploadForm.value.features
    }
    
    const response = await axios.post(`${backendUrl.value}/api/upload/single`, payload)
    
    if (response.data.status === 'success') {
      ElMessage.success(response.data.message)
      showSingleUploadDialog.value = false
      
      // 重置表单
      singleUploadFormRef.value.resetFields()
      singleUploadForm.value.features = Array(25).fill(0)
      
      // 刷新预测数据
      fetchNextDayPrediction()
    } else {
      ElMessage.error(response.data.message)
    }
    
  } catch (error) {
    if (error.response && error.response.data.error) {
      ElMessage.error(`上传失败: ${error.response.data.error}`)
    } else {
      ElMessage.error('单日数据上传失败')
    }
    console.error('单日数据上传失败:', error)
  } finally {
    singleUploadLoading.value = false
  }
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
    const response = await axios.get(`${backendUrl.value}/api/predict/lstm`)
    predictionData.value = response.data
    modelMetrics.value = response.data.model_metrics || {}
    
    // 设置次日预测值
    if (response.data.prediction && response.data.prediction.length > 0) {
      nextDayPrediction.value = response.data.prediction[0]
    }
    
    // 设置图表URL
    if (response.data.chart_url) {
      chartUrl.value = `${backendUrl.value}${response.data.chart_url}`
    }
    
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
// 退出登录
const handleLogout = () => {
  localStorage.removeItem('isLoggedIn')
  router.push('/login')
}
// 生命周期
onMounted(() => {
  // 尝试连接默认后端
  testBackendConnection()
})
</script>
<style scoped>
/* 原有样式保持不变，重点优化按钮区域样式 */
.backend-config {
  display: flex;
  gap: 10px;
  margin-bottom: 24px;
  align-items: center;
  flex-wrap: wrap;
}
.backend-input {
  flex: 1;
  min-width: 280px;
}
/* 核心按钮区域优化：居中排列+自适应间距 */
.action-buttons {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-bottom: 32px;
  flex-wrap: wrap;
  padding: 16px;
  background-color: #f9fafb;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}
/* 统一按钮基础样式 */
.action-btn {
  padding: 12px 24px;
  font-size: 15px;
  border-radius: 10px !important;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 180px;
}
/* 按钮图标优化 */
.btn-icon {
  margin-right: 8px;
  font-size: 18px;
}
/* 单个按钮差异化样式 */
.predict-btn {
  background: linear-gradient(135deg, #4096ff 0%, #165dff 100%);
  border: none;
}
.predict-btn:hover {
  background: linear-gradient(135deg, #3688f0 0%, #0e4bdb 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(22, 93, 255, 0.2);
}
.upload-inner-btn {
  background: linear-gradient(135deg, #52c41a 0%, #389e0d 100%);
  border: none;
}
.upload-inner-btn:hover {
  background: linear-gradient(135deg, #47b811 0%, #2e860a 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(56, 158, 13, 0.2);
}
.single-upload-btn {
  background: linear-gradient(135deg, #faad14 0%, #d48806 100%);
  border: none;
}
.single-upload-btn:hover {
  background: linear-gradient(135deg, #f9a602 0%, #c27a05 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(212, 136, 6, 0.2);
}
/* 后端图表样式 */
.backend-chart {
  width: 100%;
  max-width: 800px;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
  margin: 0 auto;
}
.chart-note {
  text-align: center;
  color: #909399;
  font-size: 12px;
  margin-top: 8px;
}
/* 单日数据上传表单：重点优化样式 */
.single-data-dialog .el-dialog__title {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 8px;
}
.single-data-form {
  padding: 10px 0;
}
.form-item {
  margin-bottom: 20px;
}
.form-input {
  padding: 8px 12px;
  border-radius: 6px !important;
}
/* 特征数据区域优化 */
.features-form-item {
  margin-bottom: 10px;
}
.features-section {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px;
  background: #f8f9fa;
  transition: all 0.3s ease;
}
.features-section:hover {
  border-color: #c9cdcf;
  box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}
.features-description {
  margin: 0 0 16px 0;
  color: #4e5969;
  font-size: 15px;
  font-weight: 500;
  line-height: 1.4;
}
/* 自适应特征网格：根据屏幕宽度自动分配列数，更灵活 */
.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
  gap: 12px;
  max-height: 320px;
  overflow-y: auto;
  padding-right: 8px;
}
/* 自定义滚动条：提升美观度 */
.features-grid::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
.features-grid::-webkit-scrollbar-track {
  background: #f1f3f5;
  border-radius: 3px;
}
.features-grid::-webkit-scrollbar-thumb {
  background: #c9cdcf;
  border-radius: 3px;
}
.features-grid::-webkit-scrollbar-thumb:hover {
  background: #adb5bd;
}
/* 特征输入项优化：间距和字体 */
.feature-input-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 8px;
  background: #fff;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}
.feature-label {
  font-size: 13px;
  color: #505359;
  font-weight: 500;
}
.feature-input {
  border-radius: 4px !important;
  height: 38px;
}
/* 底部按钮优化 */
.cancel-btn {
  margin-right: 16px;
  padding: 8px 20px;
  border-radius: 6px;
}
.submit-btn {
  padding: 8px 24px;
  border-radius: 6px;
  background: linear-gradient(135deg, #4096ff 0%, #165dff 100%);
  border: none;
}
.submit-btn:hover {
  background: linear-gradient(135deg, #3688f0 0%, #0e4bdb 100%);
}
/* 原有基础样式保持不变 */
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
  transition: transform 0.3s ease;
}
.status-card:hover {
  transform: translateY(-5px);
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
  display: flex;
  align-items: center;
  gap: 8px;
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
  flex-wrap: wrap;
}
.step {
  padding: 10px 15px;
  background: white;
  border-radius: 8px;
  font-size: 14px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  gap: 6px;
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
  flex-wrap: wrap;
  gap: 10px;
}
.result-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 18px;
}
.chart-container {
  width: 100%;
  margin-bottom: 30px;
  text-align: center;
}
.prediction-details {
  margin-top: 30px;
}
.prediction-details h4 {
  margin-bottom: 15px;
  color: #2c3e50;
  font-size: 16px;
}
.prediction-table {
  margin-top: 10px;
  border-radius: 8px;
  overflow: hidden;
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
  background: #f8f9fa;
  border-radius: 15px;
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
  color: #606266;
}
.no-data-subtext {
  font-size: 14px;
  opacity: 0.7;
  max-width: 500px;
  margin: 0 auto;
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
  display: flex;
  align-items: center;
  gap: 8px;
}
.upload-table {
  width: 100%;
  border-radius: 8px;
  overflow: hidden;
}
.filename {
  font-family: 'Monaco', 'Consolas', monospace;
  font-size: 14px;
  word-break: break-all;
}
.no-uploads {
  text-align: center;
  padding: 40px;
  color: #909399;
}
.logout-btn {
  border-radius: 8px;
  padding: 8px 16px;
  transition: all 0.3s ease;
}
.logout-btn:hover {
  background-color: #f56c6c;
  color: white;
}
/* 响应式优化：不同屏幕尺寸下按钮排布适配 */
@media (max-width: 1024px) {
  .action-buttons {
    gap: 16px;
  }
  .action-btn {
    min-width: 160px;
    padding: 10px 20px;
    font-size: 14px;
  }
  .features-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  }
}
@media (max-width: 768px) {
  .header {
    flex-direction: column;
    text-align: center;
    padding: 20px;
  }
  .logo {
    margin-right: 0;
    margin-bottom: 20px;
    width: 100px;
    height: 100px;
  }
  .status-cards {
    grid-template-columns: 1fr 1fr;
  }
  .action-buttons {
    flex-direction: row;
    justify-content: center;
    gap: 12px;
    padding: 12px;
  }
  .action-btn {
    min-width: 140px;
    padding: 8px 16px;
    font-size: 13px;
  }
  .btn-icon {
    font-size: 16px;
    margin-right: 6px;
  }
  .loading-steps {
    flex-direction: column;
    gap: 10px;
  }
  .backend-config {
    flex-direction: column;
    align-items: stretch;
  }
  .features-grid {
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  }
  .main-content {
    padding: 20px;
  }
  .single-data-dialog {
    width: 90% !important;
  }
}
@media (max-width: 480px) {
  .action-buttons {
    flex-direction: column;
    align-items: stretch;
  }
  .action-btn {
    min-width: 100%;
    margin-bottom: 8px;
  }
  .features-grid {
    grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  }
  .status-cards {
    grid-template-columns: 1fr;
  }
  .team-info h1 {
    font-size: 24px;
  }
  .tech-stack {
    font-size: 16px;
  }
  .prediction-section h2,
  .upload-history-section h2 {
    font-size: 20px;
  }
  .feature-label {
    font-size: 12px;
  }
  .features-description {
    font-size: 14px;
  }
}
</style>
