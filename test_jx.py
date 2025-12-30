"""测试解析接口"""
import requests
import urllib3
import re
urllib3.disable_warnings()

test_video = 'https://www.iqiyi.com/v_19rr1zbkb0.html'

apis = [
    ('jsonplayer', 'https://jx.jsonplayer.com/player/?url='),
    ('777jiexi', 'https://jx.777jiexi.com/player/?url='),
    ('8090g', 'https://www.8090g.cn/?url='),
    ('playerjy', 'https://jx.playerjy.com/?url='),
    ('mtosz', 'https://www.mtosz.com/m3u8.php?url='),
    ('we-vip', 'https://jx.we-vip.com/?url='),
    ('xmflv', 'https://jx.xmflv.com/?url='),
    ('m3u8tv', 'https://jx.m3u8.tv/jiexi/?url='),
    ('aidouer', 'https://jx.aidouer.net/?url='),
    ('yparse', 'https://jx.yparse.com/index.php?url='),
    ('ckmov', 'https://www.ckmov.vip/api.php?url='),
    ('nxflv', 'https://jx.nxflv.com/?url='),
    ('dplayer', 'https://jx.bozrc.com:4433/player/?url='),
    ('b1yy', 'https://jx.b1yy.com/?url='),
    ('cuan', 'https://cuan.la/m.php?url='),
]

working_apis = []

for name, api in apis:
    try:
        full_url = api + test_video
        r = requests.get(full_url, timeout=10, verify=False, 
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': api
            },
            allow_redirects=True)
        
        text = r.text.lower()
        
        # 检查是否有真正的播放器元素
        has_m3u8 = '.m3u8' in r.text
        has_video_tag = '<video' in text
        has_iframe = '<iframe' in text
        has_player = 'dplayer' in text or 'artplayer' in text or 'ckplayer' in text
        
        # 检查是否是广告页面
        is_ad = '广告' in r.text or 'advertisement' in text or '试玩' in r.text
        
        status = 'OK' if (has_m3u8 or has_video_tag or has_player) and not is_ad else 'FAIL'
        
        if status == 'OK':
            working_apis.append((name, api))
            
        print(f'{name:12}: {r.status_code} | m3u8={has_m3u8} video={has_video_tag} player={has_player} ad={is_ad} => {status}')
        
    except Exception as e:
        print(f'{name:12}: ERROR - {str(e)[:50]}')

print('\n=== 可用的解析接口 ===')
for name, api in working_apis:
    print(f'{name}: {api}')

