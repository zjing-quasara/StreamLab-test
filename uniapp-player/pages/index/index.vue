<template>
  <view class="container">
    <!-- 搜索框 -->
    <view class="search-box">
      <input 
        v-model="keyword" 
        placeholder="输入影视名称搜索" 
        confirm-type="search"
        @confirm="doSearch"
      />
      <button @click="doSearch">搜索</button>
    </view>
    
    <!-- 推荐列表 -->
    <view class="section">
      <text class="section-title">热门推荐</text>
      <view class="movie-grid">
        <view 
          class="movie-item" 
          v-for="item in hotMovies" 
          :key="item.name"
          @click="quickSearch(item.name)"
        >
          <text class="movie-name">{{ item.name }}</text>
          <text class="movie-tag">{{ item.tag }}</text>
        </view>
      </view>
    </view>
    
    <!-- 说明 -->
    <view class="tips">
      <text>StreamLab - 流媒体技术研究</text>
      <text>资源来自第三方，仅供学习研究</text>
    </view>
  </view>
</template>

<script>
import { initConfig } from '../../utils/api.js';

export default {
  data() {
    return {
      keyword: '',
      hotMovies: [
        { name: '长安十二时辰', tag: '48集' },
        { name: '长安二十四计', tag: '28集' },
        { name: '狂飙', tag: '热门' },
        { name: '繁花', tag: '热门' },
        { name: '庆余年', tag: '热门' },
        { name: '三体', tag: '科幻' },
      ]
    };
  },
  onLoad() {
    // 初始化配置
    initConfig();
  },
  methods: {
    doSearch() {
      if (!this.keyword.trim()) {
        uni.showToast({ title: '请输入关键词', icon: 'none' });
        return;
      }
      uni.navigateTo({
        url: `/pages/search/search?keyword=${encodeURIComponent(this.keyword)}`
      });
    },
    quickSearch(name) {
      this.keyword = name;
      this.doSearch();
    }
  }
};
</script>

<style>
.container {
  min-height: 100vh;
  background: #0a0a0f;
  padding: 20rpx;
}

.search-box {
  display: flex;
  gap: 15rpx;
  margin-bottom: 30rpx;
}

.search-box input {
  flex: 1;
  height: 80rpx;
  background: #1a1a2e;
  border-radius: 40rpx;
  padding: 0 30rpx;
  color: #fff;
  font-size: 28rpx;
}

.search-box button {
  width: 140rpx;
  height: 80rpx;
  background: linear-gradient(135deg, #00d4ff, #c471ed);
  border-radius: 40rpx;
  color: #fff;
  font-size: 28rpx;
  line-height: 80rpx;
}

.section {
  margin-bottom: 30rpx;
}

.section-title {
  color: #888;
  font-size: 26rpx;
  margin-bottom: 20rpx;
  display: block;
}

.movie-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 15rpx;
}

.movie-item {
  background: #1a1a2e;
  padding: 20rpx 30rpx;
  border-radius: 10rpx;
  display: flex;
  flex-direction: column;
}

.movie-name {
  color: #fff;
  font-size: 28rpx;
}

.movie-tag {
  color: #00d4ff;
  font-size: 22rpx;
  margin-top: 5rpx;
}

.tips {
  margin-top: 60rpx;
  text-align: center;
}

.tips text {
  display: block;
  color: #444;
  font-size: 24rpx;
  line-height: 1.8;
}
</style>

