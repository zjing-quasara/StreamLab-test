# StreamLab

流媒体技术研究 - React Native 移动端视频播放应用

## 功能

- 影视搜索（资源站聚合）
- 在线播放（m3u8/mp4）
- 支持 Android
- **🎉 弹幕功能** *(新增，可选)*
  - 多平台弹幕源（B站、爱奇艺、腾讯）
  - 自动搜索和匹配
  - 性能优化，不影响视频播放
  - 模块化设计，可一键禁用/删除
  - 详见 [弹幕使用指南](StreamLabApp/DANMAKU_GUIDE.md)

## 运行

```bash
cd StreamLabApp
npm install
npx react-native run-android
```

## 构建 APK

用 Android Studio 打开 `StreamLabApp/android` 目录，Build → Build APK

## 弹幕功能

### 快速禁用
如果不需要弹幕功能，只需修改一行代码：

```javascript
// StreamLabApp/src/services/danmaku/config.js
enabled: false  // 改为 false 即可
```

### 完整文档
- 📖 [弹幕使用指南](StreamLabApp/DANMAKU_GUIDE.md) - 使用说明、配置、禁用/删除
- 📁 [模块说明](StreamLabApp/src/services/danmaku/README.md) - 架构、扩展、API对接
- 💡 [真实API示例](StreamLabApp/src/services/danmaku/DanmakuService.real-api.example.js) - API对接参考代码

### 性能影响
- ✅ **不影响视频播放** - 独立的显示层
- ✅ **不会卡顿** - 多重性能优化（限流、缓存、硬件加速）
- ✅ **可随时移除** - 完全模块化设计

## 说明

仅供学习研究
