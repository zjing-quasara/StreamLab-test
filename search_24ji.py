# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import requests
import urllib3
import json
urllib3.disable_warnings()

headers = {'User-Agent': 'Mozilla/5.0'}
keyword = '长安二十四计'

apis = [
    ('红牛', 'https://www.hongniuzy2.com/api.php/provide/vod/?ac=detail&wd='),
    ('天空', 'https://m3u8.tiankongapi.com/api.php/provide/vod/?ac=detail&wd='),
    ('优酷M3U8', 'https://api.yparse.com/api.php/provide/vod/?ac=detail&wd='),
    ('卧龙', 'https://collect.wolongzyw.com/api.php/provide/vod/?ac=detail&wd='),
    ('樱花', 'https://m3u8.tiankongapi.com/api.php/provide/vod/?ac=detail&wd='),
]

print(f'搜索: {keyword}')
print('=' * 50)

for name, api in apis:
    url = api + keyword
    print(f'\n[{name}]')
    try:
        r = requests.get(url, timeout=10, verify=False, headers=headers)
        data = r.json()
        if 'list' in data and len(data['list']) > 0:
            for item in data['list'][:2]:
                vod_name = item.get('vod_name', '')
                print(f"  找到: {vod_name}")
                print(f"  备注: {item.get('vod_remarks', '')}")
                
                vod_play_url = item.get('vod_play_url', '')
                if vod_play_url:
                    sources = vod_play_url.split('$$$')
                    eps = sources[0].split('#') if sources else []
                    print(f"  集数: {len(eps)}")
                    if eps and '$' in eps[0]:
                        ep_name, ep_url = eps[0].split('$', 1)
                        print(f"  首集: {ep_url[:70]}")
        else:
            print('  没有结果')
    except Exception as e:
        print(f'  错误: {str(e)[:40]}')

