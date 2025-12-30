# StreamLab - uni-app版

## 项目结构

```
uniapp-player/
├── pages/
│   ├── index/index.vue    # 首页（搜索入口）
│   ├── search/search.vue  # 搜索结果页
│   └── play/play.vue      # 播放页
├── utils/
│   └── api.js             # 资源站API
├── App.vue                # 应用入口
├── main.js                # 主入口
├── manifest.json          # 应用配置
└── pages.json             # 页面配置
```

## 开发步骤

### 1. 安装HBuilderX
下载地址: https://www.dcloud.io/hbuilderx.html

### 2. 导入项目
打开HBuilderX → 文件 → 导入 → 从本地目录导入 → 选择uniapp-player文件夹

### 3. 运行调试
- 运行到浏览器: 运行 → 运行到浏览器
- 运行到手机: 运行 → 运行到手机或模拟器

### 4. 打包APK
发行 → 原生App-云打包 → 选择Android → 打包

## 热更新配置

### 1. 生成wgt更新包
发行 → 原生App-制作应用wgt包

### 2. 上传wgt到服务器/Gitee
把生成的.wgt文件上传到可访问的地址

### 3. 配置更新检测
在App.vue的onLaunch中添加:

```javascript
onLaunch() {
  // 检查更新
  uni.request({
    url: 'https://gitee.com/xxx/config/raw/master/version.json',
    success: (res) => {
      const serverVersion = res.data.version;
      const localVersion = plus.runtime.version;
      
      if (serverVersion > localVersion) {
        uni.showModal({
          title: '发现新版本',
          content: '是否更新？',
          success: (res) => {
            if (res.confirm) {
              // 下载并安装wgt
              uni.downloadFile({
                url: res.data.wgtUrl,
                success: (download) => {
                  plus.runtime.install(download.tempFilePath, {}, () => {
                    plus.runtime.restart();
                  });
                }
              });
            }
          }
        });
      }
    }
  });
}
```

### 4. version.json格式
```json
{
  "version": "1.0.1",
  "wgtUrl": "https://gitee.com/xxx/releases/app.wgt",
  "description": "修复bug"
}
```

## 资源站动态更新

utils/api.js 中配置远程资源站列表地址:

```javascript
const REMOTE_CONFIG_URL = 'https://gitee.com/你的用户名/config/raw/master/sites.json';
```

sites.json格式:
```json
{
  "sites": [
    {"name": "红牛资源", "api": "https://www.hongniuzy2.com/api.php/provide/vod/"},
    {"name": "无尽资源", "api": "https://api.wujinapi.me/api.php/provide/vod/"}
  ]
}
```

## 特点

- ✅ 国内网络友好（uni-app国产框架）
- ✅ 接近原生体验
- ✅ 支持热更新（不用重新安装APP）
- ✅ 资源站可远程动态更新
- ✅ 无需服务器（配置放Gitee）
- ✅ 不需要应用商店审核（直接发APK）

