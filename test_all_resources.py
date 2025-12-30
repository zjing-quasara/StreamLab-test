# -*- coding: utf-8 -*-
"""
资源采集站生态说明：

1. 资源采集站（资源API）- 不是播放器，是提供影视数据的API服务
   - 它们爬取各大视频平台的资源
   - 转换成m3u8格式存储在CDN上
   - 通过标准API接口提供给影视APP使用

2. API格式统一（苹果CMS标准）：
   - 搜索：/api.php/provide/vod/?ac=detail&wd=关键词
   - 返回JSON：包含剧名、集数、m3u8链接等

3. 影视APP的工作原理：
   - 聚合多个资源站的API
   - 用户搜索时同时查询多个资源站
   - 找到资源后用HLS.js播放m3u8

下面测试常见的资源采集站：
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import requests
import urllib3
urllib3.disable_warnings()

headers = {'User-Agent': 'Mozilla/5.0'}
keyword = '长安十二时辰'

# 常见资源采集站列表
resource_sites = [
    ('红牛资源', 'https://www.hongniuzy2.com/api.php/provide/vod/?ac=detail&wd='),
    ('光速资源', 'https://api.guangsuapi.com/api.php/provide/vod/?ac=detail&wd='),
    ('快车资源', 'https://caiji.kczyapi.com/api.php/provide/vod/?ac=detail&wd='),
    ('酷云资源', 'https://kuaikan-api.com/api.php/provide/vod/?ac=detail&wd='),
    ('无尽资源', 'https://api.wujinapi.me/api.php/provide/vod/?ac=detail&wd='),
    ('非凡资源', 'https://cj.ffzyapi.com/api.php/provide/vod/?ac=detail&wd='),
    ('优质资源', 'https://api.youziyuan.com/api.php/provide/vod/?ac=detail&wd='),
    ('新浪资源', 'https://api.xinlangapi.com/api.php/provide/vod/?ac=detail&wd='),
    ('百度云资源', 'https://api.apibdzy.com/api.php/provide/vod/?ac=detail&wd='),
    ('1080P资源', 'https://1080p.tv/api.php/provide/vod/?ac=detail&wd='),
]

print('=' * 70)
print('资源采集站测试 - 搜索《长安十二时辰》')
print('=' * 70)
print(f'\n共测试 {len(resource_sites)} 个资源站\n')

available_sites = []

for name, api in resource_sites:
    url = api + keyword
    print(f'[{name}]', end=' ')
    
    try:
        r = requests.get(url, timeout=8, verify=False, headers=headers)
        data = r.json()
        
        if 'list' in data and len(data['list']) > 0:
            item = data['list'][0]
            vod_name = item.get('vod_name', '')
            remarks = item.get('vod_remarks', '')
            
            # 获取集数
            vod_play_url = item.get('vod_play_url', '')
            sources = vod_play_url.split('$$$')
            eps = sources[0].split('#') if sources else []
            
            print(f'✓ 找到《{vod_name}》{remarks}, {len(eps)}集')
            available_sites.append({
                'name': name,
                'api': api,
                'vod_name': vod_name,
                'episodes': len(eps)
            })
        else:
            print('✗ 无结果')
            
    except requests.exceptions.Timeout:
        print('✗ 超时')
    except requests.exceptions.ConnectionError:
        print('✗ 连接失败')
    except Exception as e:
        print(f'✗ 错误')

print('\n' + '=' * 70)
print('测试结果汇总')
print('=' * 70)

if available_sites:
    print(f'\n找到 {len(available_sites)} 个可用资源站:')
    for site in available_sites:
        print(f"  - {site['name']}: {site['episodes']}集")
else:
    print('\n没有找到可用资源站')

print('\n说明：')
print('  - 这些资源站不是播放器，是提供m3u8链接的API服务')
print('  - 影视APP会聚合多个资源站，提高资源覆盖率')
print('  - 资源站可能随时失效或更换域名')

