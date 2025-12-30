# -*- coding: utf-8 -*-
"""测试更多资源站是否有长安十二时辰"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import requests
import urllib3
import concurrent.futures
urllib3.disable_warnings()

headers = {'User-Agent': 'Mozilla/5.0'}
keyword = '长安十二时辰'

# 更全的资源站列表
resource_sites = [
    ('红牛资源', 'https://www.hongniuzy2.com/api.php/provide/vod/?ac=detail&wd='),
    ('无尽资源', 'https://api.wujinapi.me/api.php/provide/vod/?ac=detail&wd='),
    ('闪电资源', 'https://sdzyapi.com/api.php/provide/vod/?ac=detail&wd='),
    ('光速资源', 'https://api.guangsuapi.com/api.php/provide/vod/?ac=detail&wd='),
    ('飞速资源', 'https://www.feisuzyapi.com/api.php/provide/vod/?ac=detail&wd='),
    ('鱼乐资源', 'https://api.ylzy.xyz/api.php/provide/vod/?ac=detail&wd='),
    ('淘片资源', 'https://taopianapi.com/home/cjapi/as/mc10/vod/xml?wd='),
    ('鲨鱼资源', 'https://api.1080pzy.com/api.php/provide/vod/?ac=detail&wd='),
    ('OK资源', 'https://api.okzy.tv/api.php/provide/vod/?ac=detail&wd='),
    ('快看资源', 'https://kuaikan-api.com/api.php/provide/vod/?ac=detail&wd='),
    ('天空资源', 'https://m3u8.tiankongapi.com/api.php/provide/vod/?ac=detail&wd='),
    ('暴风资源', 'https://bfzyapi.com/api.php/provide/vod/?ac=detail&wd='),
    ('百度云资源', 'https://api.apibdzy.com/api.php/provide/vod/?ac=detail&wd='),
    ('优质资源', 'https://api.youziyuan.com/api.php/provide/vod/?ac=detail&wd='),
    ('U酷资源', 'https://api.ukuapi.com/api.php/provide/vod/?ac=detail&wd='),
]

def test_site(site_info):
    name, api = site_info
    url = api + keyword
    try:
        r = requests.get(url, timeout=6, verify=False, headers=headers)
        data = r.json()
        if 'list' in data and len(data['list']) > 0:
            item = data['list'][0]
            vod_name = item.get('vod_name', '')
            if '长安' in vod_name:
                vod_play_url = item.get('vod_play_url', '')
                sources = vod_play_url.split('$$$')
                eps = sources[0].split('#') if sources else []
                return (name, True, len(eps), item.get('vod_remarks', ''))
        return (name, False, 0, '无结果')
    except:
        return (name, False, 0, '连接失败')

print('=' * 60)
print(f'测试 {len(resource_sites)} 个资源站')
print('搜索: 长安十二时辰')
print('=' * 60)

# 并发测试
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(test_site, resource_sites))

available = []
failed = []

for name, success, eps, note in results:
    if success:
        print(f'✓ {name}: {eps}集 ({note})')
        available.append((name, eps))
    else:
        print(f'✗ {name}: {note}')
        failed.append(name)

print('\n' + '=' * 60)
print(f'结果: {len(available)}/{len(resource_sites)} 个资源站有资源')
print('=' * 60)
if available:
    print('\n可用资源站:')
    for name, eps in available:
        print(f'  ● {name} - {eps}集')

