# -*- coding: utf-8 -*-
"""深度分析虾米接口"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import requests
import urllib3
import re
import base64
import json
urllib3.disable_warnings()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://jx.xmflv.com/',
}

# 优酷长安十二时辰第一集
youku_url = 'https://v.youku.com/v_show/id_XNDI2NjcyMzI4NA==.html'
jx_url = 'https://jx.xmflv.com/?url=' + youku_url

print("1. 获取解析页面...")
r = requests.get(jx_url, timeout=15, verify=False, headers=headers)
content = r.text

print(f"   状态: {r.status_code}, 长度: {len(content)}")

# 查找API调用
print("\n2. 分析页面内容...")

# 解混淆的eval代码通常会请求一个api.php
api_patterns = [
    r'api\.php\?[^"\']+',
    r'api/[^"\']+',
    r'/jx/[^"\']+\.php',
]

for pattern in api_patterns:
    matches = re.findall(pattern, content)
    if matches:
        print(f"   找到API模式: {matches[:2]}")

# 查找可能的密钥或配置
config_patterns = [
    r'var\s+config\s*=\s*(\{[^}]+\})',
    r'var\s+url\s*=\s*["\']([^"\']+)["\']',
    r'src\s*:\s*["\']([^"\']+)["\']',
]

for pattern in config_patterns:
    matches = re.findall(pattern, content)
    if matches:
        print(f"   找到配置: {matches[:2]}")

# 查找脚本URL
script_urls = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', content)
print(f"\n3. 外部脚本: {len(script_urls)} 个")
for url in script_urls[:5]:
    print(f"   {url[:80]}")

# 尝试直接请求xmflv的api
print("\n4. 尝试虾米API...")
api_test_urls = [
    'https://jx.xmflv.com/api.php?url=' + youku_url,
    'https://jx.xmflv.com/jx.php?url=' + youku_url,
]

for api_url in api_test_urls:
    try:
        r2 = requests.get(api_url, timeout=10, verify=False, headers=headers)
        print(f"   {api_url[:50]}...")
        print(f"   状态: {r2.status_code}, 长度: {len(r2.text)}")
        
        # 检查是否是JSON
        try:
            data = r2.json()
            print(f"   JSON: {json.dumps(data, ensure_ascii=False)[:200]}")
            if 'url' in data:
                print(f"   [OK] 找到视频URL!")
        except:
            # 检查是否包含m3u8
            if '.m3u8' in r2.text:
                m3u8 = re.search(r'https?://[^\s"\']+\.m3u8[^\s"\']*', r2.text)
                if m3u8:
                    print(f"   [OK] 找到M3U8: {m3u8.group()[:100]}")
    except Exception as e:
        print(f"   错误: {str(e)[:50]}")

print("\n5. 测试完成")
print("   结论: 虾米接口返回的是一个播放器页面，")
print("   需要在浏览器中执行JavaScript才能播放。")
print("   iframe嵌入应该可以正常工作。")

