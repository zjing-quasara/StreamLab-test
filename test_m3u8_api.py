# -*- coding: utf-8 -*-
"""测试直接返回m3u8的API"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import requests
import urllib3
import json
import re
urllib3.disable_warnings()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}

youku_url = 'https://v.youku.com/v_show/id_XNDI2NjcyMzI4NA==.html'

# 一些返回JSON/m3u8的API
apis = [
    ('JSON Player', 'https://jx.jsonplayer.com/player/?url='),
    ('BLBO', 'https://jx.blbo.cc:4433/?url='),
    ('YParse', 'https://jx.yparse.com/index.php?url='),
    ('77JX', 'https://jx.777jiexi.com/player/?url='),
]

print("测试返回m3u8的API接口")
print("=" * 60)

for name, api in apis:
    url = api + youku_url
    print(f"\n[测试] {name}")
    print(f"URL: {url[:60]}...")
    
    try:
        r = requests.get(url, timeout=15, verify=False, headers=headers, allow_redirects=True)
        print(f"状态: {r.status_code}, 长度: {len(r.text)}")
        
        # 尝试解析JSON
        try:
            data = r.json()
            print(f"JSON响应: {json.dumps(data, ensure_ascii=False)[:300]}")
            if 'url' in data and data['url']:
                print(f"[OK] 找到视频URL: {data['url'][:100]}")
        except json.JSONDecodeError:
            # 不是JSON，检查是否包含m3u8
            m3u8_match = re.search(r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*', r.text)
            if m3u8_match:
                print(f"[OK] 在HTML中找到m3u8: {m3u8_match.group()[:100]}")
            elif '<video' in r.text.lower() or '<iframe' in r.text.lower():
                print("[INFO] 返回HTML播放器页面")
            else:
                print(f"返回内容开头: {r.text[:200]}")
                
    except requests.exceptions.Timeout:
        print("[FAIL] 超时")
    except requests.exceptions.SSLError:
        print("[FAIL] SSL错误")
    except requests.exceptions.ConnectionError:
        print("[FAIL] 连接失败")
    except Exception as e:
        print(f"[FAIL] 错误: {str(e)[:50]}")

print("\n" + "=" * 60)
print("测试完成")

