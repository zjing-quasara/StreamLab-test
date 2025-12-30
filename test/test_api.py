#!/usr/bin/env python3
"""
测试资源站API
"""
import requests
import json

SITES = [
    {
        'name': '红牛资源',
        'api': 'https://www.hongniuzy2.com/api.php/provide/vod/',
    },
    {
        'name': '无尽资源',
        'api': 'https://api.wujinapi.me/api.php/provide/vod/',
    },
]

def test_search(keyword):
    """测试搜索功能"""
    print(f"\n{'='*50}")
    print(f"搜索关键词: {keyword}")
    print('='*50)
    
    for site in SITES:
        try:
            url = f"{site['api']}?ac=detail&wd={keyword}"
            print(f"\n[{site['name']}]")
            print(f"URL: {url}")
            
            resp = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            if resp.status_code != 200:
                print(f"请求失败: {resp.status_code}")
                continue
            
            data = resp.json()
            total = data.get('total', 0)
            videos = data.get('list', [])
            
            print(f"总数: {total}")
            
            if videos:
                for i, v in enumerate(videos[:3]):
                    name = v.get('vod_name', '未知')
                    remarks = v.get('vod_remarks', '')
                    play_url = v.get('vod_play_url', '')
                    episodes = len(play_url.split('#')) if play_url else 0
                    print(f"  {i+1}. {name} ({remarks}) - {episodes}集")
            else:
                print("  无结果")
                
        except requests.Timeout:
            print(f"超时")
        except Exception as e:
            print(f"错误: {e}")

if __name__ == '__main__':
    test_search('长安')
    test_search('狂飙')
    test_search('繁花')

