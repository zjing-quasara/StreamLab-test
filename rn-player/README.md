# StreamLab - React Native 版

## 项目结构

```
rn-player/
├── src/
│   ├── screens/
│   │   ├── HomeScreen.js      # 首页
│   │   ├── SearchScreen.js    # 搜索结果页
│   │   └── PlayScreen.js      # 播放页
│   └── utils/
│       ├── api.js             # 资源站API
│       └── update.js          # Pushy热更新
├── App.js                     # 应用入口
├── package.json               # 依赖配置
└── README.md                  # 说明文档
```

---

## 环境准备

### 1. 安装 Node.js
下载: https://nodejs.org (选择LTS版本)

### 2. 安装 JDK 17
下载: https://adoptium.net

### 3. 配置 Android SDK
如果你已安装 Android Studio，SDK已经有了。

配置环境变量:
```
ANDROID_HOME = C:\Users\你的用户名\AppData\Local\Android\Sdk
Path 添加:
  %ANDROID_HOME%\platform-tools
  %ANDROID_HOME%\emulator
```

---

## 创建项目

由于React Native项目需要完整初始化，执行以下命令:

```bash
# 1. 全局安装 react-native-cli
npm install -g react-native-cli

# 2. 创建新项目 (在你想要的目录下)
npx react-native init StreamLab

# 3. 进入项目目录
cd StreamLab

# 4. 复制我提供的源代码
# 把 rn-player/src 文件夹复制到 StreamLab/src
# 把 rn-player/App.js 覆盖到 StreamLab/App.js

# 5. 安装依赖
npm install react-native-video @react-navigation/native @react-navigation/native-stack react-native-screens react-native-safe-area-context react-native-update

# 6. 运行项目
npx react-native run-android
```

---

## 配置 Pushy 热更新

### 1. 注册 Pushy
访问: https://pushy.reactnative.cn
注册账号 → 创建应用 → 获取 appKey

### 2. 配置 appKey
编辑 `src/utils/update.js`:
```javascript
const appKey = Platform.select({
  android: '你从Pushy获取的Android_appKey',
  ios: '你从Pushy获取的iOS_appKey',
});
```

### 3. 配置原生代码
参考官方文档: https://pushy.reactnative.cn/docs/getting-started

### 4. 发布热更新

```bash
# 安装 pushy-cli
npm install -g react-native-update-cli

# 登录
pushy login

# 发布更新
pushy bundle --platform android
pushy publish --platform android
```

---

## 资源站动态更新

编辑 `src/utils/api.js` 中的远程配置地址:
```javascript
const REMOTE_CONFIG_URL = 'https://gitee.com/你的用户名/streamlab-config/raw/master/config.json';
```

在Gitee创建 `config.json`:
```json
{
  "sites": [
    {"name": "红牛资源", "api": "https://www.hongniuzy2.com/api.php/provide/vod/"},
    {"name": "无尽资源", "api": "https://api.wujinapi.me/api.php/provide/vod/"}
  ]
}
```

---

## 打包 APK

### Debug 版本 (测试用)
```bash
npx react-native run-android
```
APK位置: `android/app/build/outputs/apk/debug/app-debug.apk`

### Release 版本 (发布用)
```bash
cd android
./gradlew assembleRelease
```
APK位置: `android/app/build/outputs/apk/release/app-release.apk`

---

## 热更新流程

```
1. 修改代码

2. 发布热更新包
   pushy bundle --platform android
   pushy publish --platform android

3. 用户打开APP → 自动下载更新 → 下次启动生效
```

---

## 常见问题

### Q: 运行报错 "SDK location not found"
A: 在 android 目录创建 `local.properties` 文件:
```
sdk.dir=C:\\Users\\你的用户名\\AppData\\Local\\Android\\Sdk
```

### Q: 视频播放黑屏
A: 确保使用的是 m3u8 格式的链接

### Q: 热更新不生效
A: 检查 appKey 是否正确配置

---

## 特点

- ✅ 接近原生性能
- ✅ Pushy 热更新（国内服务）
- ✅ 资源站可远程动态更新
- ✅ 支持 m3u8 视频播放
- ✅ 静默更新，用户无感知

