# -*- coding: utf-8 -*-
"""自动测试解析接口，找到能用的"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import requests
import urllib3
import re
import time
urllib3.disable_warnings()

# 优酷长安十二时辰第一集
test_url = 'https://v.youku.com/v_show/id_XNDI2NjcyMzI4NA==.html'

# 解析接口列表
apis = [
    ('虾米', 'https://jx.xmflv.com/?url='),
    ('M3U8', 'https://jx.m3u8.tv/jiexi/?url='),
    ('爱豆', 'https://jx.aidouer.net/?url='),
    ('OK解析', 'https://okjx.cc/?url='),
    ('NXFLV', 'https://jx.nxflv.com/?url='),
    ('B1YY', 'https://jx.b1yy.com/?url='),
    ('8090', 'https://www.8090g.cn/?url='),
    ('PlayerJY', 'https://jx.playerjy.com/?url='),
    ('YMU', 'https://www.ymu.cc/?url='),
    ('DMJX', 'https://www.dmjx.cc/?url='),
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

working_apis = []

print("=" * 60)
print("自动测试解析接口")
print("测试视频: 优酷 - 长安十二时辰 第1集")
print("=" * 60)

for name, api in apis:
    full_url = api + test_url
    print(f"\n[测试] {name}: {api[:40]}...")
    
    try:
        r = requests.get(full_url, timeout=15, verify=False, headers=headers, allow_redirects=True)
        
        content = r.text
        content_lower = content.lower()
        
        # 检查指标
        has_player = any(x in content_lower for x in ['dplayer', 'artplayer', 'ckplayer', 'xmflv', 'jwplayer', 'videojs'])
        has_video_tag = '<video' in content_lower
        has_m3u8 = '.m3u8' in content
        has_script = '<script' in content
        
        # 检查是否是广告
        ad_keywords = ['VR女友', '试玩', '下载游戏', '领取女神', '点击下载', '广告']
        is_ad = any(kw in content for kw in ad_keywords)
        
        # 检查是否有真正的视频源
        has_source = bool(re.search(r'(url|src|source)\s*[:=]\s*["\'][^"\']*\.(m3u8|mp4|flv)', content, re.I))
        
        # 判断是否可用
        is_working = (has_player or has_video_tag or has_m3u8 or has_source) and not is_ad
        
        status = "[OK] 可能可用" if is_working else "[FAIL] 不可用"
        if is_ad:
            status = "[AD] 广告页面"
            
        print(f"  状态: {r.status_code}, 长度: {len(content)}")
        print(f"  播放器: {has_player}, Video标签: {has_video_tag}, M3U8: {has_m3u8}")
        print(f"  广告: {is_ad}, 视频源: {has_source}")
        print(f"  结果: {status}")
        
        if is_working:
            working_apis.append((name, api))
            # 保存可用的响应
            with open(f'working_{name}.html', 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  已保存到 working_{name}.html")
            
    except requests.exceptions.Timeout:
        print(f"  结果: [FAIL] 超时")
    except requests.exceptions.ConnectionError:
        print(f"  结果: [FAIL] 连接失败")
    except Exception as e:
        print(f"  结果: [FAIL] 错误: {str(e)[:50]}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)

if working_apis:
    print(f"\n找到 {len(working_apis)} 个可能可用的接口:")
    for name, api in working_apis:
        print(f"  - {name}: {api}")
    print(f"\n推荐使用: {working_apis[0][0]}")
else:
    print("\n没有找到可用的接口")

