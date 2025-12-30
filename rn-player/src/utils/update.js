/**
 * Pushy 热更新模块
 * 文档: https://pushy.reactnative.cn/docs/getting-started
 */

import {
  checkUpdate,
  downloadUpdate,
  switchVersion,
  switchVersionLater,
  markSuccess,
  isFirstTime,
  isRolledBack,
} from 'react-native-update';
import { Alert, Platform } from 'react-native';

// 从 Pushy 后台获取的 appKey
const appKey = Platform.select({
  android: '你的Android_appKey',
  ios: '你的iOS_appKey',
});

/**
 * 检查并执行热更新
 * @param {boolean} silent - 是否静默更新（不弹窗提示）
 */
export async function checkForUpdate(silent = true) {
  try {
    const info = await checkUpdate(appKey);

    if (info.expired) {
      // 原生版本过旧，需要下载新的APK
      if (!silent) {
        Alert.alert('提示', '您的应用版本过旧，请下载最新版本', [
          { text: '确定', onPress: () => {} },
        ]);
      }
      return;
    }

    if (info.upToDate) {
      // 已是最新版本
      if (!silent) {
        Alert.alert('提示', '当前已是最新版本');
      }
      return;
    }

    if (info.update) {
      // 有新版本，开始下载
      console.log('发现新版本，开始下载...');
      
      const hash = await downloadUpdate(info, {
        onDownloadProgress: ({ received, total }) => {
          const progress = Math.round((received / total) * 100);
          console.log(`下载进度: ${progress}%`);
        },
      });

      if (silent) {
        // 静默更新：下次启动生效
        switchVersionLater(hash);
        console.log('更新已下载，下次启动生效');
      } else {
        // 询问用户是否立即重启
        Alert.alert('更新完成', '是否立即重启应用？', [
          { text: '稍后', onPress: () => switchVersionLater(hash) },
          { text: '立即重启', onPress: () => switchVersion(hash) },
        ]);
      }
    }
  } catch (error) {
    console.log('检查更新失败:', error);
  }
}

/**
 * 标记更新成功（防止回滚）
 */
export function markUpdateSuccess() {
  if (isFirstTime) {
    markSuccess();
    console.log('更新成功');
  }
  if (isRolledBack) {
    console.log('更新已回滚');
  }
}

