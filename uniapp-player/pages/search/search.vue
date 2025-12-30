<template>
  <view class="container">
    <!-- 加载中 -->
    <view class="loading" v-if="loading">
      <text>搜索中...</text>
    </view>
    
    <!-- 搜索结果 -->
    <view class="results" v-else>
      <view class="result-header">
        <text>搜索: {{ keyword }}</text>
        <text>找到 {{ results.length }} 个结果</text>
      </view>
      
      <view 
        class="result-item" 
        v-for="(item, index) in results" 
        :key="index"
        @click="selectMovie(item)"
      >
        <image class="poster" :src="item.pic" mode="aspectFill"></image>
        <view class="info">
          <text class="name">{{ item.name }}</text>
          <text class="meta">{{ item.source }} · {{ item.remarks }}</text>
          <text class="episodes">共 {{ item.episodes.length }} 集</text>
        </view>
      </view>
      
      <view class="empty" v-if="results.length === 0">
        <text>没有找到相关资源</text>
      </view>
    </view>
  </view>
</template>

<script>
import { searchVideo } from '../../utils/api.js';

export default {
  data() {
    return {
      keyword: '',
      loading: true,
      results: []
    };
  },
  onLoad(options) {
    this.keyword = decodeURIComponent(options.keyword || '');
    this.doSearch();
  },
  methods: {
    async doSearch() {
      this.loading = true;
      try {
        this.results = await searchVideo(this.keyword);
      } catch (e) {
        uni.showToast({ title: '搜索失败', icon: 'none' });
      }
      this.loading = false;
    },
    selectMovie(item) {
      // 保存到全局，传递给播放页
      getApp().globalData = getApp().globalData || {};
      getApp().globalData.currentMovie = item;
      uni.navigateTo({
        url: '/pages/play/play'
      });
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

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400rpx;
}

.loading text {
  color: #888;
  font-size: 28rpx;
}

.result-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20rpx;
}

.result-header text {
  color: #888;
  font-size: 26rpx;
}

.result-item {
  display: flex;
  gap: 20rpx;
  background: #1a1a2e;
  padding: 20rpx;
  border-radius: 10rpx;
  margin-bottom: 15rpx;
}

.poster {
  width: 160rpx;
  height: 220rpx;
  border-radius: 8rpx;
  background: #333;
}

.info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.name {
  color: #fff;
  font-size: 32rpx;
  margin-bottom: 10rpx;
}

.meta {
  color: #888;
  font-size: 24rpx;
  margin-bottom: 8rpx;
}

.episodes {
  color: #00d4ff;
  font-size: 24rpx;
}

.empty {
  text-align: center;
  padding: 100rpx 0;
}

.empty text {
  color: #666;
  font-size: 28rpx;
}
</style>

