<template>
  <view class="container">
    <!-- 视频播放器 -->
    <view class="player-wrapper">
      <video
        id="videoPlayer"
        :src="currentUrl"
        controls
        autoplay
        :title="movieName"
        @error="onVideoError"
        @play="onVideoPlay"
      ></video>
    </view>
    
    <!-- 视频信息 -->
    <view class="info">
      <text class="title">{{ movieName }}</text>
      <text class="episode">正在播放: {{ currentEpisodeName }}</text>
    </view>
    
    <!-- 剧集选择 -->
    <view class="episodes-section">
      <text class="section-title">选集 (共{{ episodes.length }}集)</text>
      <scroll-view scroll-x class="episodes-scroll">
        <view class="episodes-list">
          <view 
            class="ep-btn"
            :class="{ active: index === currentIndex }"
            v-for="(ep, index) in episodes"
            :key="index"
            @click="playEpisode(index)"
          >
            <text>{{ index + 1 }}</text>
          </view>
        </view>
      </scroll-view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      movieName: '',
      episodes: [],
      currentIndex: 0,
      currentUrl: '',
      currentEpisodeName: ''
    };
  },
  onLoad() {
    const globalData = getApp().globalData || {};
    const movie = globalData.currentMovie;
    
    if (movie) {
      this.movieName = movie.name;
      this.episodes = movie.episodes || [];
      if (this.episodes.length > 0) {
        this.playEpisode(0);
      }
    }
  },
  methods: {
    playEpisode(index) {
      if (index < 0 || index >= this.episodes.length) return;
      
      this.currentIndex = index;
      const ep = this.episodes[index];
      this.currentUrl = ep.url;
      this.currentEpisodeName = ep.name;
      
      uni.setNavigationBarTitle({
        title: `${this.movieName} - ${ep.name}`
      });
    },
    onVideoError(e) {
      console.log('视频加载失败', e);
      uni.showToast({
        title: '视频加载失败，请切换线路',
        icon: 'none'
      });
    },
    onVideoPlay() {
      console.log('开始播放');
    }
  }
};
</script>

<style>
.container {
  min-height: 100vh;
  background: #0a0a0f;
}

.player-wrapper {
  width: 100%;
  background: #000;
}

.player-wrapper video {
  width: 100%;
  height: 420rpx;
}

.info {
  padding: 20rpx;
}

.title {
  color: #fff;
  font-size: 34rpx;
  display: block;
  margin-bottom: 10rpx;
}

.episode {
  color: #888;
  font-size: 26rpx;
}

.episodes-section {
  padding: 20rpx;
}

.section-title {
  color: #888;
  font-size: 26rpx;
  display: block;
  margin-bottom: 15rpx;
}

.episodes-scroll {
  white-space: nowrap;
}

.episodes-list {
  display: flex;
  flex-wrap: wrap;
  gap: 15rpx;
}

.ep-btn {
  width: 80rpx;
  height: 80rpx;
  background: #1a1a2e;
  border-radius: 10rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ep-btn text {
  color: #fff;
  font-size: 28rpx;
}

.ep-btn.active {
  background: linear-gradient(135deg, #00d4ff, #c471ed);
}

.ep-btn.active text {
  color: #000;
  font-weight: bold;
}
</style>

