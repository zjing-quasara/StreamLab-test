# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import requests
import urllib3
import re
urllib3.disable_warnings()

url = 'https://jx.yparse.com/index.php?url=https://v.youku.com/v_show/id_XNDI2NjcyMzI4NA==.html'
r = requests.get(url, timeout=15, verify=False, headers={'User-Agent': 'Mozilla/5.0'})

print('状态:', r.status_code)
print('长度:', len(r.text))

# 保存内容
with open('yparse_result.html', 'w', encoding='utf-8') as f:
    f.write(r.text)
print('已保存到 yparse_result.html')

# 检查关键内容
if 'dplayer' in r.text.lower():
    print('[OK] 包含DPlayer')
if 'artplayer' in r.text.lower():
    print('[OK] 包含ArtPlayer')
if 'hls.js' in r.text.lower():
    print('[OK] 包含HLS.js')
    
# 查找m3u8
m3u8_matches = re.findall(r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*', r.text)
if m3u8_matches:
    print('[OK] 找到M3U8源:')
    for m in m3u8_matches[:3]:
        print('  ', m[:100])
else:
    print('[INFO] 没有直接的m3u8链接，需要JavaScript解析')

# 检查是否有播放器div
if 'id="player"' in r.text.lower() or 'id="dplayer"' in r.text.lower():
    print('[OK] 包含播放器容器')

