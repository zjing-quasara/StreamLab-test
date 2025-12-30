# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import requests
import urllib3
import json
urllib3.disable_warnings()

api = 'https://www.hongniuzy2.com/api.php/provide/vod/?ac=detail&wd=长安二十四计'
r = requests.get(api, timeout=15, verify=False, headers={'User-Agent': 'Mozilla/5.0'})
data = r.json()

item = data['list'][0]
print('名称:', item.get('vod_name'))
print('备注:', item.get('vod_remarks'))

vod_play_url = item.get('vod_play_url', '')
vod_play_from = item.get('vod_play_from', '')
print('播放源:', vod_play_from)

# 获取m3u8源
sources = vod_play_url.split('$$$')
source_names = vod_play_from.split('$$$')

for i, (source, sname) in enumerate(zip(sources, source_names)):
    eps = source.split('#')
    print(f'\n源{i+1} ({sname}): {len(eps)}集')
    
    # 保存m3u8源
    if 'm3u8' in sname.lower():
        episodes = []
        for ep in eps:
            if '$' in ep:
                name, url = ep.split('$', 1)
                episodes.append({'name': name, 'url': url})
                print(f'  {name}: {url}')
        
        with open('changan24ji_episodes.json', 'w', encoding='utf-8') as f:
            json.dump(episodes, f, ensure_ascii=False, indent=2)
        print('\n已保存到 changan24ji_episodes.json')
        break

