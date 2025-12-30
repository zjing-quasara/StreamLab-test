/**
 * 测试 API 逻辑 (Node.js)
 */

const RESOURCE_SITES = [
  {
    name: '红牛资源',
    api: 'https://www.hongniuzy2.com/api.php/provide/vod/',
  },
  {
    name: '无尽资源',
    api: 'https://api.wujinapi.me/api.php/provide/vod/',
  },
];

function parseEpisodes(playUrl, playFrom) {
  if (!playUrl) return [];

  const sources = playUrl.split('$$$');
  const sourceNames = playFrom ? playFrom.split('$$$') : [];

  // 优先选择m3u8源
  for (let i = 0; i < sources.length; i++) {
    const name = sourceNames[i] || '';
    if (name.toLowerCase().includes('m3u8')) {
      return parseSource(sources[i], false);
    }
  }

  // 否则用第一个源（需要添加m3u8后缀）
  if (sources.length > 0) {
    return parseSource(sources[0], true);
  }

  return [];
}

function parseSource(source, addM3u8Suffix = false) {
  const episodes = [];
  if (!source) return episodes;

  const parts = source.split('#');
  for (const part of parts) {
    if (part.includes('$')) {
      const [name, url] = part.split('$');
      if (name && url && url.startsWith('http')) {
        let finalUrl = url.trim();
        if (addM3u8Suffix && !finalUrl.endsWith('.m3u8')) {
          finalUrl = finalUrl + '/index.m3u8';
        }
        episodes.push({ name: name.trim(), url: finalUrl });
      }
    }
  }
  return episodes;
}

async function searchVideo(keyword) {
  const results = [];

  const promises = RESOURCE_SITES.map(async (site) => {
    try {
      const url = `${site.api}?ac=detail&wd=${encodeURIComponent(keyword)}`;
      console.log(`搜索: ${site.name}`);

      const response = await fetch(url);

      if (!response.ok) {
        console.log(`${site.name} 请求失败: ${response.status}`);
        return [];
      }

      const data = await response.json();

      if (data.list && data.list.length > 0) {
        const siteResults = [];
        for (const item of data.list) {
          const episodes = parseEpisodes(item.vod_play_url, item.vod_play_from);
          if (episodes.length > 0) {
            siteResults.push({
              source: site.name,
              name: item.vod_name,
              pic: item.vod_pic || '',
              remarks: item.vod_remarks || '',
              year: item.vod_year || '',
              episodes,
            });
          }
        }
        console.log(`${site.name} 找到 ${siteResults.length} 个结果`);
        return siteResults;
      } else {
        console.log(`${site.name} 无结果`);
        return [];
      }
    } catch (error) {
      console.log(`${site.name} 错误: ${error.message}`);
      return [];
    }
  });

  const allResults = await Promise.all(promises);
  
  for (const siteResults of allResults) {
    results.push(...siteResults);
  }

  return results;
}

// 测试
async function test() {
  console.log('=== 测试搜索 API ===\n');
  
  const keyword = '狂飙';
  console.log(`关键词: ${keyword}\n`);
  
  const startTime = Date.now();
  const results = await searchVideo(keyword);
  const elapsed = Date.now() - startTime;
  
  console.log(`\n耗时: ${elapsed}ms`);
  console.log(`总结果: ${results.length} 个\n`);
  
  // 显示前3个结果
  results.slice(0, 3).forEach((item, i) => {
    console.log(`${i+1}. ${item.name} (${item.source})`);
    console.log(`   备注: ${item.remarks}`);
    console.log(`   集数: ${item.episodes.length}`);
    if (item.episodes.length > 0) {
      const ep = item.episodes[0];
      console.log(`   第1集: ${ep.url.substring(0, 60)}...`);
    }
    console.log();
  });
}

test().catch(console.error);

