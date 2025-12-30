# -*- coding: utf-8 -*-
"""获取长安十二时辰的完整m3u8链接"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import requests
import urllib3
import json
urllib3.disable_warnings()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}

# 红牛资源API
api = 'https://www.hongniuzy2.com/api.php/provide/vod/?ac=detail&wd=长安十二时辰'

print("获取长安十二时辰资源详情...")
r = requests.get(api, timeout=15, verify=False, headers=headers)
data = r.json()

if 'list' in data and len(data['list']) > 0:
    item = data['list'][0]
    print(f"\n名称: {item.get('vod_name')}")
    print(f"年份: {item.get('vod_year')}")
    print(f"地区: {item.get('vod_area')}")
    print(f"备注: {item.get('vod_remarks')}")
    
    vod_play_url = item.get('vod_play_url', '')
    vod_play_from = item.get('vod_play_from', '')
    
    print(f"\n播放源: {vod_play_from}")
    
    # 解析所有集数
    if vod_play_url:
        # 可能有多个播放源，用$$$分隔
        sources = vod_play_url.split('$$$')
        source_names = vod_play_from.split('$$$') if vod_play_from else ['未知']
        
        print(f"\n共 {len(sources)} 个播放源")
        
        all_episodes = []
        
        for idx, (source, source_name) in enumerate(zip(sources, source_names)):
            episodes = source.split('#')
            print(f"\n源{idx+1} ({source_name}): {len(episodes)} 集")
            
            for i, ep in enumerate(episodes[:3]):  # 只显示前3集
                if '$' in ep:
                    ep_name, ep_url = ep.split('$', 1)
                    print(f"  {ep_name}: {ep_url}")
                    if idx == 0:  # 只保存第一个源
                        all_episodes.append({'name': ep_name, 'url': ep_url})
            
            if len(episodes) > 3:
                print(f"  ... 还有 {len(episodes) - 3} 集")
        
        # 保存第一个源的所有集数到文件
        if all_episodes:
            # 获取完整的集数列表
            first_source = sources[0].split('#')
            complete_episodes = []
            for ep in first_source:
                if '$' in ep:
                    ep_name, ep_url = ep.split('$', 1)
                    complete_episodes.append({'name': ep_name, 'url': ep_url})
            
            print(f"\n保存 {len(complete_episodes)} 集到文件...")
            with open('changan_episodes.json', 'w', encoding='utf-8') as f:
                json.dump(complete_episodes, f, ensure_ascii=False, indent=2)
            print("已保存到 changan_episodes.json")
            
            # 测试第一集的URL是否可访问
            print("\n测试第一集URL...")
            first_url = complete_episodes[0]['url']
            try:
                test_r = requests.head(first_url, timeout=10, verify=False, headers=headers, allow_redirects=True)
                print(f"状态码: {test_r.status_code}")
                print(f"Content-Type: {test_r.headers.get('Content-Type', 'N/A')}")
                if test_r.status_code == 200:
                    print("[OK] URL可访问!")
            except Exception as e:
                print(f"测试失败: {str(e)[:50]}")
else:
    print("没有找到资源")

