# -*- coding: utf-8 -*-
"""测试网盘搜索"""
import requests
import urllib3
import json
import re
urllib3.disable_warnings()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# 测试一些网盘搜索站点
search_sites = [
    {
        'name': 'alipansou',
        'url': 'https://www.alipansou.com/search?k=%E9%95%BF%E5%AE%89%E5%8D%81%E4%BA%8C%E6%97%B6%E8%BE%B0',
    },
    {
        'name': 'upyunso', 
        'url': 'https://www.upyunso.com/search.html?keyword=%E9%95%BF%E5%AE%89',
    },
]

for site in search_sites:
    try:
        print(f"\n=== Testing {site['name']} ===")
        r = requests.get(site['url'], timeout=15, verify=False, headers=headers, allow_redirects=True)
        print(f"Status: {r.status_code}")
        print(f"Length: {len(r.text)}")
        
        # 查找阿里云盘链接
        aliyun_links = re.findall(r'https://www\.aliyundrive\.com/s/[a-zA-Z0-9]+', r.text)
        quark_links = re.findall(r'https://pan\.quark\.cn/s/[a-zA-Z0-9]+', r.text)
        
        if aliyun_links:
            print(f"Found Aliyun links: {aliyun_links[:3]}")
        if quark_links:
            print(f"Found Quark links: {quark_links[:3]}")
            
        # 保存结果
        with open(f"{site['name']}_result.html", 'w', encoding='utf-8') as f:
            f.write(r.text)
        print(f"Saved to {site['name']}_result.html")
        
    except Exception as e:
        print(f"Error: {str(e)[:80]}")

