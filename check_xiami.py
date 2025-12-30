# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import re

with open('working_虾米.html', 'r', encoding='utf-8') as f:
    content = f.read()

print('文件长度:', len(content))
print()

# 检查关键内容
if 'Xmflv' in content:
    print('[OK] 包含 Xmflv 播放器')
if 'dplayer' in content.lower():
    print('[OK] 包含 DPlayer')
if 'artplayer' in content.lower():
    print('[OK] 包含 ArtPlayer')

# 查找视频源
m3u8_matches = re.findall(r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*', content)
if m3u8_matches:
    print('[OK] 找到M3U8源:', len(m3u8_matches), '个')
    for m in m3u8_matches[:3]:
        print('  ', m[:100])

mp4_matches = re.findall(r'https?://[^\s"\'<>]+\.mp4[^\s"\'<>]*', content)
if mp4_matches:
    print('[OK] 找到MP4源:', len(mp4_matches), '个')
    for m in mp4_matches[:3]:
        print('  ', m[:100])

# 检查是否有API调用
api_matches = re.findall(r'api\.php\?[^"\'<>\s]+', content)
if api_matches:
    print('[INFO] 有API调用:', len(api_matches), '个')
    for m in api_matches[:2]:
        print('  ', m[:80])

# 检查是否需要进一步解析
if 'url=' in content and 'api' in content.lower():
    print('[INFO] 可能需要进一步解析视频源')
    
print()
print('=== HTML开头 ===')
print(content[:2000])

