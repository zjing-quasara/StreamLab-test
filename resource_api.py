# -*- coding: utf-8 -*-
"""
资源站API模块 - 只保留可用的资源站
可用于：Web后端、手机APP后端、或直接集成到客户端
"""
import requests
import urllib3
urllib3.disable_warnings()

# 可用资源站列表（只保留测试通过的）
RESOURCE_SITES = [
    {
        'name': '红牛资源',
        'api': 'https://www.hongniuzy2.com/api.php/provide/vod/',
    },
    {
        'name': '无尽资源', 
        'api': 'https://api.wujinapi.me/api.php/provide/vod/',
    },
]

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}


def search_video(keyword, timeout=10):
    """
    搜索影视资源
    返回: [{'source': '红牛', 'name': '长安十二时辰', 'episodes': [...], ...}, ...]
    """
    results = []
    
    for site in RESOURCE_SITES:
        try:
            url = f"{site['api']}?ac=detail&wd={keyword}"
            r = requests.get(url, timeout=timeout, verify=False, headers=HEADERS)
            data = r.json()
            
            if 'list' in data and len(data['list']) > 0:
                for item in data['list']:
                    vod_name = item.get('vod_name', '')
                    vod_play_url = item.get('vod_play_url', '')
                    vod_play_from = item.get('vod_play_from', '')
                    
                    # 解析播放源
                    sources = vod_play_url.split('$$$')
                    source_names = vod_play_from.split('$$$')
                    
                    # 优先选择m3u8源
                    episodes = []
                    for source, sname in zip(sources, source_names):
                        if 'm3u8' in sname.lower():
                            for ep in source.split('#'):
                                if '$' in ep:
                                    ep_name, ep_url = ep.split('$', 1)
                                    episodes.append({'name': ep_name, 'url': ep_url})
                            break
                    
                    # 如果没有m3u8源，用第一个源
                    if not episodes and sources:
                        for ep in sources[0].split('#'):
                            if '$' in ep:
                                ep_name, ep_url = ep.split('$', 1)
                                # 自动补全m3u8后缀
                                if not ep_url.endswith('.m3u8'):
                                    ep_url = ep_url + '/index.m3u8'
                                episodes.append({'name': ep_name, 'url': ep_url})
                    
                    if episodes:
                        results.append({
                            'source': site['name'],
                            'name': vod_name,
                            'year': item.get('vod_year', ''),
                            'area': item.get('vod_area', ''),
                            'remarks': item.get('vod_remarks', ''),
                            'pic': item.get('vod_pic', ''),
                            'episodes': episodes,
                        })
        except Exception as e:
            print(f"[{site['name']}] 错误: {str(e)[:50]}")
    
    return results


def get_available_sites():
    """返回可用资源站列表"""
    return [{'name': s['name'], 'api': s['api']} for s in RESOURCE_SITES]


# 测试
if __name__ == '__main__':
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print('搜索: 长安十二时辰')
    results = search_video('长安十二时辰')
    
    for r in results:
        print(f"\n[{r['source']}] {r['name']} ({r['remarks']})")
        print(f"  集数: {len(r['episodes'])}")
        if r['episodes']:
            print(f"  第1集: {r['episodes'][0]['url'][:60]}...")

