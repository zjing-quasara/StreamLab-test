# -*- coding: utf-8 -*-
"""使用资源采集站API搜索长安十二时辰"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import requests
import urllib3
import json
import re
import xml.etree.ElementTree as ET
urllib3.disable_warnings()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}

# 资源采集站API列表 - 这些是专门提供m3u8资源的
# 格式：(名称, 搜索API, 详情API格式)
resource_apis = [
    ('快看资源', 'https://kuaikan-api.com/api.php/provide/vod/?ac=detail&wd='),
    ('红牛资源', 'https://www.hongniuzy2.com/api.php/provide/vod/?ac=detail&wd='),
    ('天空资源', 'https://m3u8.tiankongapi.com/api.php/provide/vod/?ac=detail&wd='),
    ('U酷资源', 'https://api.ukuapi.com/api.php/provide/vod/?ac=detail&wd='),
    ('速播资源', 'https://subocaiji.com/api.php/provide/vod/?ac=detail&wd='),
    ('量子资源', 'https://cj.lziapi.com/api.php/provide/vod/?ac=detail&wd='),
    ('闪电资源', 'https://sdzyapi.com/api.php/provide/vod/?ac=detail&wd='),
    ('暴风资源', 'https://bfzyapi.com/api.php/provide/vod/?ac=detail&wd='),
]

keyword = '长安十二时辰'
found_resources = []

print("=" * 60)
print("搜索《长安十二时辰》资源")
print("=" * 60)

for name, api in resource_apis:
    url = api + keyword
    print(f"\n[搜索] {name}")
    
    try:
        r = requests.get(url, timeout=10, verify=False, headers=headers)
        
        # 尝试JSON解析
        try:
            data = r.json()
            if 'list' in data and len(data['list']) > 0:
                print(f"  [OK] 找到 {len(data['list'])} 个结果")
                
                for item in data['list'][:2]:
                    vod_name = item.get('vod_name', '')
                    vod_play_url = item.get('vod_play_url', '')
                    
                    if '长安' in vod_name:
                        print(f"  名称: {vod_name}")
                        
                        # 解析播放链接
                        if vod_play_url:
                            # 格式通常是: 第1集$url#第2集$url
                            episodes = vod_play_url.split('#')
                            print(f"  集数: {len(episodes)}")
                            
                            if episodes:
                                first_ep = episodes[0]
                                if '$' in first_ep:
                                    ep_name, ep_url = first_ep.split('$', 1)
                                    print(f"  第一集: {ep_name}")
                                    print(f"  URL: {ep_url[:100]}...")
                                    
                                    found_resources.append({
                                        'source': name,
                                        'name': vod_name,
                                        'episodes': episodes,
                                        'first_url': ep_url,
                                    })
            else:
                print(f"  没有找到结果")
                
        except json.JSONDecodeError:
            # 可能是XML格式
            try:
                root = ET.fromstring(r.text)
                videos = root.findall('.//video')
                if videos:
                    print(f"  [OK] XML格式，找到 {len(videos)} 个结果")
                    for video in videos[:2]:
                        name_elem = video.find('name')
                        if name_elem is not None and '长安' in name_elem.text:
                            print(f"  名称: {name_elem.text}")
                            dl = video.find('.//dd')
                            if dl is not None:
                                print(f"  播放链接: {dl.text[:100] if dl.text else 'N/A'}...")
                else:
                    print(f"  XML解析但没有video元素")
            except ET.ParseError:
                print(f"  返回格式未知: {r.text[:100]}")
                
    except requests.exceptions.Timeout:
        print(f"  [FAIL] 超时")
    except requests.exceptions.ConnectionError:
        print(f"  [FAIL] 连接失败")
    except Exception as e:
        print(f"  [FAIL] {str(e)[:50]}")

print("\n" + "=" * 60)
print("搜索结果汇总")
print("=" * 60)

if found_resources:
    print(f"\n找到 {len(found_resources)} 个可用资源:")
    for i, res in enumerate(found_resources):
        print(f"\n{i+1}. {res['source']} - {res['name']}")
        print(f"   集数: {len(res['episodes'])}")
        print(f"   第一集URL: {res['first_url'][:80]}...")
        
        # 验证URL是否可访问
        if res['first_url'].endswith('.m3u8'):
            print("   [OK] 是m3u8格式，可直接播放!")
else:
    print("\n没有找到可用资源")

