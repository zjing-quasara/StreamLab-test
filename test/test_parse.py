#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试视频链接解析"""
import requests

def test_parse():
    url = 'https://www.hongniuzy2.com/api.php/provide/vod/?ac=detail&wd=狂飙'
    resp = requests.get(url, timeout=15)
    data = resp.json()

    if not data.get('list'):
        print("无结果")
        return

    item = data['list'][0]
    print("名称:", item.get('vod_name'))
    print("播放源标识:", item.get('vod_play_from'))
    print()
    
    play_url = item.get('vod_play_url', '')
    play_from = item.get('vod_play_from', '')
    
    sources = play_url.split('$$$')
    source_names = play_from.split('$$$') if play_from else []
    
    print(f"共 {len(sources)} 个播放源\n")
    
    for i, src in enumerate(sources[:3]):
        name = source_names[i] if i < len(source_names) else 'unknown'
        episodes = src.split('#')
        print(f"源{i+1} [{name}]: {len(episodes)}集")
        
        # 显示前2集链接
        for ep in episodes[:2]:
            if '$' in ep:
                ep_name, ep_url = ep.split('$', 1)
                # 检查是否需要添加m3u8后缀
                needs_suffix = not ep_url.endswith('.m3u8')
                print(f"  {ep_name}: {ep_url[:70]}...")
                print(f"    -> 是m3u8: {'否, 需要加后缀' if needs_suffix else '是'}")
        print()

if __name__ == '__main__':
    test_parse()

