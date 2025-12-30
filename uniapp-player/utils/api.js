/**
 * 资源站API模块
 * 支持从远程动态获取资源站列表
 */

// 远程配置地址（放Gitee上，国内访问快）
const REMOTE_CONFIG_URL = 'https://gitee.com/你的用户名/streamlab-config/raw/master/config.json';

// 默认资源站（内置备用）
const DEFAULT_SITES = [
  {
    name: '红牛资源',
    api: 'https://www.hongniuzy2.com/api.php/provide/vod/'
  },
  {
    name: '无尽资源',
    api: 'https://api.wujinapi.me/api.php/provide/vod/'
  }
];

// 当前使用的资源站列表
let currentSites = [...DEFAULT_SITES];

/**
 * 初始化 - 尝试获取远程配置
 */
export async function initConfig() {
  try {
    const res = await uni.request({
      url: REMOTE_CONFIG_URL,
      timeout: 5000
    });
    if (res.data && res.data.sites) {
      currentSites = res.data.sites;
      console.log('远程配置加载成功');
    }
  } catch (e) {
    console.log('使用内置配置');
  }
}

/**
 * 搜索影视
 */
export async function searchVideo(keyword) {
  const results = [];
  
  for (const site of currentSites) {
    try {
      const url = `${site.api}?ac=detail&wd=${encodeURIComponent(keyword)}`;
      const res = await uni.request({ url, timeout: 8000 });
      const data = res.data;
      
      if (data.list && data.list.length > 0) {
        for (const item of data.list) {
          const episodes = parseEpisodes(item.vod_play_url, item.vod_play_from);
          if (episodes.length > 0) {
            results.push({
              source: site.name,
              name: item.vod_name,
              pic: item.vod_pic,
              remarks: item.vod_remarks,
              year: item.vod_year,
              episodes: episodes
            });
          }
        }
      }
    } catch (e) {
      console.log(`${site.name} 请求失败`);
    }
  }
  
  return results;
}

/**
 * 解析剧集列表
 */
function parseEpisodes(playUrl, playFrom) {
  if (!playUrl) return [];
  
  const sources = playUrl.split('$$$');
  const sourceNames = playFrom ? playFrom.split('$$$') : [];
  
  // 优先选择m3u8源
  for (let i = 0; i < sources.length; i++) {
    if (sourceNames[i] && sourceNames[i].toLowerCase().includes('m3u8')) {
      return parseSource(sources[i]);
    }
  }
  
  // 否则用第一个源
  return parseSource(sources[0], true);
}

function parseSource(source, addM3u8Suffix = false) {
  const episodes = [];
  for (const ep of source.split('#')) {
    if (ep.includes('$')) {
      const [name, url] = ep.split('$');
      let finalUrl = url;
      if (addM3u8Suffix && !url.endsWith('.m3u8')) {
        finalUrl = url + '/index.m3u8';
      }
      episodes.push({ name, url: finalUrl });
    }
  }
  return episodes;
}

