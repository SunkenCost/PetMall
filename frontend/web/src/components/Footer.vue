<template>
  <footer class="site-footer">
    <!-- 服务承诺条带 -->
    <div class="promise-bar">
      <div class="promise-bar__inner">
        <div class="promise-item">
          <el-icon class="promise-icon"><Shield /></el-icon>
          <span class="promise-label">7天无理由退换货</span>
        </div>
        <div class="promise-divider"></div>
        <div class="promise-item">
          <el-icon class="promise-icon"><Van /></el-icon>
          <span class="promise-label">满99元全场免邮</span>
        </div>
        <div class="promise-divider"></div>
        <div class="promise-item">
          <el-icon class="promise-icon"><Trophy /></el-icon>
          <span class="promise-label">100%品质保证</span>
        </div>
      </div>
    </div>

    <!-- 底部信息区 -->
    <div class="footer-main">
      <div class="footer-brand">
        <span class="brand-logo">PETMALL 宠爱之家</span>
        <p class="brand-slogan">用专业的态度呵护您的宠物生活</p>
      </div>

      <nav class="footer-links">
        <a href="javascript:;" class="footer-link">关于我们</a>
        <span class="sep">·</span>
        <a href="javascript:;" class="footer-link">帮助中心</a>
        <span class="sep">·</span>
        <a href="javascript:;" class="footer-link">售后服务</a>
        <span class="sep">·</span>
        <a href="javascript:;" class="footer-link">宠物资讯</a>
        <span class="sep">·</span>
        <a href="javascript:;" class="footer-link">关于货源</a>
      </nav>

      <p class="footer-copy">© 2026 宠爱之家 PetMall   版权所有 ·  谢奇鹰</p>
    </div>
  </footer>
</template>

<script>
import { Shield, Van, Trophy } from '@element-plus/icons-vue'

export default {
  name: 'FooterPage',
  components: { Shield, Van, Trophy }
}
</script>

<style scoped>
.site-footer {
  background: #f8f9fa;
  color: #606266;
  margin-top: auto;
  border-top: 1px solid #ebeef5;
}

/* 服务承诺条带 */
.promise-bar {
  background: #ffffff;
  border-bottom: 1px solid #ebeef5;
}
.promise-bar__inner {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
}
.promise-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 60px;
  flex: 1;
  justify-content: center;
}
.promise-icon {
  font-size: 24px;
  color: #1677ff;
}
.promise-label {
  font-size: 15px;
  font-weight: 500;
  color: #303133;
  letter-spacing: 0.5px;
  white-space: nowrap;
}
.promise-divider {
  width: 1px;
  height: 24px;
  background: #ebeef5;
  flex-shrink: 0;
}

/* 主信息区 */
.footer-main {
  max-width: 1400px;
  margin: 0 auto;
  padding: 40px 40px 30px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}
.footer-brand {
  text-align: center;
}
.brand-logo {
  font-size: 20px;
  font-weight: 800;
  color: #1a1a1a;
  letter-spacing: 1px;
  font-family: 'Inter', sans-serif;
}
.brand-slogan {
  margin: 8px 0 0;
  font-size: 13px;
  color: #909399;
}
.footer-links {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: center;
}
.footer-link {
  color: #606266;
  text-decoration: none;
  font-size: 13px;
  transition: color 0.2s;
}
.footer-link:hover {
  color: #1677ff;
}
.sep {
  color: #dcdfe6;
  font-size: 13px;
}
.footer-copy {
  font-size: 12px;
  color: #a8abb2;
  margin: 0;
  text-align: center;
}
</style>
