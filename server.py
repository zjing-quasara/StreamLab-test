"""
B站视频播放器后端服务
支持：视频解析、弹幕获取、视频流代理
"""

from flask import Flask, jsonify, request, Response, render_template
from flask_cors import CORS
import requests
import json
import re
import time
import hashlib
import urllib.parse

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# 请求头配置
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.bilibili.com',
    'Origin': 'https://www.bilibili.com'
}

# WBI签名相关 (B站API需要)
MIXIN_KEY_ENC_TAB = [
    46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35,
    27, 43, 5, 49, 33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13,
    37, 48, 7, 16, 24, 55, 40, 61, 26, 17, 0, 1, 60, 51, 30, 4,
    22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11, 36, 20, 34, 44, 52
]

def get_mixin_key(orig: str) -> str:
    """获取混合密钥"""
    return ''.join([orig[i] for i in MIXIN_KEY_ENC_TAB])[:32]

def enc_wbi(params: dict, img_key: str, sub_key: str) -> dict:
    """WBI签名"""
    mixin_key = get_mixin_key(img_key + sub_key)
    curr_time = int(time.time())
    params['wts'] = curr_time
    params = dict(sorted(params.items()))
    params = {
        k: ''.join(filter(lambda c: c not in "!'()*", str(v)))
        for k, v in params.items()
    }
    query = urllib.parse.urlencode(params)
    wbi_sign = hashlib.md5((query + mixin_key).encode()).hexdigest()
    params['w_rid'] = wbi_sign
    return params

def get_wbi_keys():
    """获取WBI密钥"""
    try:
        resp = requests.get(
            'https://api.bilibili.com/x/web-interface/nav',
            headers=HEADERS,
            timeout=10
        )
        data = resp.json()['data']
        img_url = data['wbi_img']['img_url']
        sub_url = data['wbi_img']['sub_url']
        img_key = img_url.rsplit('/', 1)[1].split('.')[0]
        sub_key = sub_url.rsplit('/', 1)[1].split('.')[0]
        return img_key, sub_key
    except:
        return None, None

def bv_to_av(bvid):
    """BV号转AV号"""
    try:
        resp = requests.get(
            f'https://api.bilibili.com/x/web-interface/view?bvid={bvid}',
            headers=HEADERS,
            timeout=10
        )
        return resp.json()['data']['aid']
    except:
        return None


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/video/info')
def get_video_info():
    """获取视频信息（支持普通视频和番剧）"""
    input_url = request.args.get('bvid', '').strip()
    
    if not input_url:
        return jsonify({'code': -1, 'message': '请提供视频链接或BV号'})
    
    # 检查是否是番剧链接
    ep_match = re.search(r'ep(\d+)', input_url)
    ss_match = re.search(r'ss(\d+)', input_url)
    
    if ep_match or ss_match:
        # 番剧处理
        return get_bangumi_info(ep_match, ss_match)
    
    # 普通视频处理
    bvid = input_url
    if bvid.startswith('BV'):
        pass
    elif 'bilibili.com' in bvid:
        # 从URL提取BV号
        match = re.search(r'BV\w+', bvid)
        if match:
            bvid = match.group()
        else:
            return jsonify({'code': -1, 'message': '无法从URL提取BV号，请尝试普通视频链接'})
    
    try:
        # 获取视频基本信息
        resp = requests.get(
            f'https://api.bilibili.com/x/web-interface/view?bvid={bvid}',
            headers=HEADERS,
            timeout=10
        )
        data = resp.json()
        
        if data['code'] != 0:
            return jsonify({'code': -1, 'message': data.get('message', '获取视频信息失败')})
        
        video_data = data['data']
        
        # 获取分P信息
        pages = video_data.get('pages', [])
        
        result = {
            'code': 0,
            'data': {
                'bvid': bvid,
                'aid': video_data['aid'],
                'title': video_data['title'],
                'desc': video_data['desc'],
                'pic': video_data['pic'],
                'duration': video_data['duration'],
                'type': 'video',  # 标记类型
                'owner': {
                    'name': video_data['owner']['name'],
                    'face': video_data['owner']['face']
                },
                'stat': {
                    'view': video_data['stat']['view'],
                    'danmaku': video_data['stat']['danmaku'],
                    'like': video_data['stat']['like'],
                    'coin': video_data['stat']['coin']
                },
                'pages': [
                    {
                        'cid': p['cid'],
                        'page': p['page'],
                        'part': p['part'],
                        'duration': p['duration']
                    }
                    for p in pages
                ],
                'cid': video_data['cid']  # 默认第一P的cid
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'code': -1, 'message': f'请求失败: {str(e)}'})


def get_bangumi_info(ep_match, ss_match):
    """获取番剧信息"""
    try:
        # 构建API请求
        if ep_match:
            ep_id = ep_match.group(1)
            api_url = f'https://api.bilibili.com/pgc/view/web/season?ep_id={ep_id}'
        else:
            ss_id = ss_match.group(1)
            api_url = f'https://api.bilibili.com/pgc/view/web/season?season_id={ss_id}'
        
        resp = requests.get(api_url, headers=HEADERS, timeout=10)
        data = resp.json()
        
        if data['code'] != 0:
            return jsonify({'code': -1, 'message': data.get('message', '获取番剧信息失败')})
        
        result_data = data['result']
        episodes = result_data.get('episodes', [])
        
        # 找到当前集
        current_ep = None
        if ep_match:
            ep_id = int(ep_match.group(1))
            for ep in episodes:
                if ep['ep_id'] == ep_id:
                    current_ep = ep
                    break
        
        if not current_ep and episodes:
            current_ep = episodes[0]
        
        if not current_ep:
            return jsonify({'code': -1, 'message': '未找到可播放的剧集'})
        
        result = {
            'code': 0,
            'data': {
                'bvid': current_ep.get('bvid', ''),
                'aid': current_ep.get('aid', 0),
                'ep_id': current_ep['ep_id'],
                'title': f"{result_data['title']} - {current_ep.get('long_title') or current_ep.get('title', '')}",
                'desc': result_data.get('evaluate', ''),
                'pic': result_data.get('cover', ''),
                'duration': current_ep.get('duration', 0) // 1000,
                'type': 'bangumi',  # 标记为番剧
                'season_id': result_data.get('season_id'),
                'owner': {
                    'name': result_data.get('up_info', {}).get('uname', '番剧'),
                    'face': result_data.get('up_info', {}).get('avatar', '')
                },
                'stat': {
                    'view': result_data.get('stat', {}).get('views', 0),
                    'danmaku': result_data.get('stat', {}).get('danmakus', 0),
                    'like': result_data.get('stat', {}).get('likes', 0),
                    'coin': result_data.get('stat', {}).get('coins', 0)
                },
                'pages': [
                    {
                        'cid': ep['cid'],
                        'page': idx + 1,
                        'part': ep.get('long_title') or ep.get('title', f'第{idx+1}集'),
                        'duration': ep.get('duration', 0) // 1000,
                        'ep_id': ep['ep_id']
                    }
                    for idx, ep in enumerate(episodes)
                ],
                'cid': current_ep['cid']
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'code': -1, 'message': f'获取番剧信息失败: {str(e)}'})


@app.route('/api/video/playurl')
def get_play_url():
    """获取视频播放地址"""
    bvid = request.args.get('bvid', '')
    cid = request.args.get('cid', '')
    ep_id = request.args.get('ep_id', '')
    video_type = request.args.get('type', 'video')
    quality = request.args.get('quality', '80')  # 80=1080P, 64=720P, 32=480P, 16=360P
    
    if not cid:
        return jsonify({'code': -1, 'message': '缺少CID参数'})
    
    try:
        # 番剧使用专用接口
        if video_type == 'bangumi' or ep_id:
            return get_bangumi_playurl(ep_id, cid, quality)
        
        # 普通视频
        if not bvid:
            return jsonify({'code': -1, 'message': '缺少BVID参数'})
        
        # 获取WBI密钥
        img_key, sub_key = get_wbi_keys()
        
        params = {
            'bvid': bvid,
            'cid': cid,
            'qn': quality,
            'fnval': 16,  # 16=dash格式, 1=flv格式
            'fnver': 0,
            'fourk': 1
        }
        
        # WBI签名
        if img_key and sub_key:
            params = enc_wbi(params, img_key, sub_key)
        
        resp = requests.get(
            'https://api.bilibili.com/x/player/wbi/playurl',
            params=params,
            headers=HEADERS,
            timeout=15
        )
        data = resp.json()
        
        if data['code'] != 0:
            # 尝试旧版接口
            resp = requests.get(
                'https://api.bilibili.com/x/player/playurl',
                params={
                    'bvid': bvid,
                    'cid': cid,
                    'qn': quality,
                    'fnval': 1
                },
                headers=HEADERS,
                timeout=15
            )
            data = resp.json()
        
        if data['code'] != 0:
            return jsonify({'code': -1, 'message': data.get('message', '获取播放地址失败')})
        
        return parse_playurl_response(data['data'])
        
    except Exception as e:
        return jsonify({'code': -1, 'message': f'请求失败: {str(e)}'})


def get_bangumi_playurl(ep_id, cid, quality):
    """获取番剧播放地址"""
    try:
        # 番剧播放地址API
        params = {
            'cid': cid,
            'qn': quality,
            'fnval': 16,
            'fnver': 0,
            'fourk': 1
        }
        
        if ep_id:
            params['ep_id'] = ep_id
        
        resp = requests.get(
            'https://api.bilibili.com/pgc/player/web/playurl',
            params=params,
            headers=HEADERS,
            timeout=15
        )
        data = resp.json()
        
        if data['code'] != 0:
            # 番剧可能需要VIP，尝试获取预览
            return jsonify({
                'code': -1, 
                'message': f"番剧获取失败: {data.get('message', '可能需要大会员')}"
            })
        
        return parse_playurl_response(data['result'])
        
    except Exception as e:
        return jsonify({'code': -1, 'message': f'获取番剧播放地址失败: {str(e)}'})


def parse_playurl_response(play_data):
    """解析播放地址响应"""
    result = {
        'code': 0,
        'data': {
            'quality': play_data.get('quality', 0),
            'accept_quality': play_data.get('accept_quality', []),
            'accept_description': play_data.get('accept_description', [])
        }
    }
    
    # 处理DASH格式
    if 'dash' in play_data:
        dash = play_data['dash']
        videos = dash.get('video', [])
        audios = dash.get('audio', [])
        
        # 选择最高质量的视频和音频
        if videos:
            best_video = max(videos, key=lambda x: x.get('bandwidth', 0))
            result['data']['video_url'] = best_video.get('baseUrl') or best_video.get('base_url')
            result['data']['video_codecs'] = best_video.get('codecs', '')
            result['data']['video_bandwidth'] = best_video.get('bandwidth', 0)
        
        if audios:
            best_audio = max(audios, key=lambda x: x.get('bandwidth', 0))
            result['data']['audio_url'] = best_audio.get('baseUrl') or best_audio.get('base_url')
            result['data']['audio_codecs'] = best_audio.get('codecs', '')
        
        result['data']['format'] = 'dash'
    
    # 处理FLV/MP4格式
    elif 'durl' in play_data:
        durls = play_data['durl']
        if durls:
            result['data']['video_url'] = durls[0]['url']
            result['data']['format'] = 'flv'
    
    return jsonify(result)


@app.route('/api/danmaku')
def get_danmaku():
    """获取弹幕"""
    cid = request.args.get('cid', '')
    
    if not cid:
        return jsonify({'code': -1, 'message': '缺少CID参数'})
    
    try:
        # 获取XML格式弹幕
        resp = requests.get(
            f'https://comment.bilibili.com/{cid}.xml',
            headers=HEADERS,
            timeout=15
        )
        resp.encoding = 'utf-8'
        
        # 解析XML
        import xml.etree.ElementTree as ET
        root = ET.fromstring(resp.text)
        
        danmakus = []
        for d in root.findall('d'):
            try:
                attrs = d.get('p', '').split(',')
                if len(attrs) >= 4:
                    danmakus.append({
                        'time': float(attrs[0]),
                        'mode': int(attrs[1]),  # 1滚动 4底部 5顶部
                        'size': int(attrs[2]),
                        'color': int(attrs[3]),
                        'text': d.text or ''
                    })
            except:
                continue
        
        # 按时间排序
        danmakus.sort(key=lambda x: x['time'])
        
        return jsonify({
            'code': 0,
            'data': {
                'count': len(danmakus),
                'danmakus': danmakus
            }
        })
        
    except Exception as e:
        return jsonify({'code': -1, 'message': f'获取弹幕失败: {str(e)}'})


@app.route('/api/proxy/video')
def proxy_video():
    """代理视频流 (解决跨域和防盗链)"""
    url = request.args.get('url', '')
    
    if not url:
        return Response('Missing URL', status=400)
    
    try:
        # 处理Range请求 (支持视频拖动)
        headers = dict(HEADERS)
        if 'Range' in request.headers:
            headers['Range'] = request.headers['Range']
        
        resp = requests.get(
            url,
            headers=headers,
            stream=True,
            timeout=30
        )
        
        # 构建响应头
        response_headers = {
            'Content-Type': resp.headers.get('Content-Type', 'video/mp4'),
            'Accept-Ranges': 'bytes',
            'Access-Control-Allow-Origin': '*'
        }
        
        if 'Content-Length' in resp.headers:
            response_headers['Content-Length'] = resp.headers['Content-Length']
        if 'Content-Range' in resp.headers:
            response_headers['Content-Range'] = resp.headers['Content-Range']
        
        def generate():
            for chunk in resp.iter_content(chunk_size=8192):
                yield chunk
        
        status_code = 206 if 'Range' in request.headers else 200
        return Response(
            generate(),
            status=status_code,
            headers=response_headers
        )
        
    except Exception as e:
        return Response(f'Proxy error: {str(e)}', status=500)


@app.route('/api/parse/jx')
def parse_with_jx():
    """
    返回可用的解析接口列表
    前端使用iframe直接加载解析页面
    """
    url = request.args.get('url', '')
    
    if not url:
        return jsonify({'code': -1, 'message': '缺少URL参数'})
    
    # 可用的解析接口 (2024年测试可用)
    jx_apis = [
        {'name': '虾米解析', 'api': 'https://jx.xmflv.com/?url='},
        {'name': '爱豆解析', 'api': 'https://jx.aidouer.net/?url='},
        {'name': 'M3U8TV', 'api': 'https://jx.m3u8.tv/jiexi/?url='},
        {'name': '听乐解析', 'api': 'https://jx.dj6u.com/?url='},
        {'name': '盘古解析', 'api': 'https://www.pangujiexi.cc/jiexi.php?url='},
        {'name': 'OK解析', 'api': 'https://okjx.cc/?url='},
        {'name': '云解析', 'api': 'https://jx.yparse.com/index.php?url='},
        {'name': '爱看解析', 'api': 'https://jx.xn--z7x900a.vip/player/?url='},
    ]
    
    return jsonify({
        'code': 0,
        'data': [
            {
                'name': item['name'],
                'url': item['api'] + url
            }
            for item in jx_apis
        ]
    })


@app.route('/player')
def player_page():
    """独立播放器页面 - 使用iframe加载解析接口"""
    return render_template('player.html')


@app.route('/search')
def search_page():
    """影视搜索页面"""
    return render_template('search.html')


@app.route('/play')
def play_page():
    """播放页面"""
    return render_template('play.html')


@app.route('/changan')
def changan_page():
    """长安十二时辰专属页面"""
    return render_template('changan.html')


@app.route('/changan24')
def changan24_page():
    """长安二十四计专属页面"""
    return render_template('changan24.html')


@app.route('/api/search/movie')
def search_movie():
    """
    搜索影视 - 内置热门影视数据 + 真实可播放的m3u8源
    """
    keyword = request.args.get('keyword', '').lower()
    
    if not keyword:
        return jsonify({'code': -1, 'message': '请输入搜索关键词'})
    
    # 内置影视数据库 - 使用真实可播放的公开m3u8源演示
    movie_db = [
        {
            'name': '长安十二时辰',
            'keywords': ['长安', '十二时辰', '雷佳音', '易烊千玺'],
            'type': '电视剧',
            'year': '2019',
            'note': '48集全',
            'source': '资源站',
            'pic': 'https://img9.doubanio.com/view/photo/l_ratio_poster/public/p2561716440.jpg',
            # 演示用 - 实际会使用真实资源站数据
            'play_url': '第1集$https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8#第2集$https://bitdash-a.akamaihd.net/content/sintel/hls/playlist.m3u8#第3集$https://demo.unified-streaming.com/k8s/features/stable/video/tears-of-steel/tears-of-steel.ism/.m3u8'
        },
        {
            'name': '唐人街探案1900',
            'keywords': ['唐探', '唐人街', '1900', '王宝强', '刘昊然'],
            'type': '电影',
            'year': '2025',
            'note': 'HD',
            'source': '资源站',
            'pic': '',
            'play_url': '高清$https://bitdash-a.akamaihd.net/content/sintel/hls/playlist.m3u8'
        },
        {
            'name': '庆余年',
            'keywords': ['庆余年', '张若昀', '李沁'],
            'type': '电视剧',
            'year': '2019',
            'note': '46集全',
            'source': '资源站',
            'pic': 'https://img1.doubanio.com/view/photo/l_ratio_poster/public/p2577418984.jpg',
            'play_url': '第1集$https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8#第2集$https://bitdash-a.akamaihd.net/content/sintel/hls/playlist.m3u8'
        },
        {
            'name': '狂飙',
            'keywords': ['狂飙', '张译', '张颂文', '高启强'],
            'type': '电视剧',
            'year': '2023',
            'note': '39集全',
            'source': '资源站',
            'pic': '',
            'play_url': '第1集$https://bitdash-a.akamaihd.net/content/sintel/hls/playlist.m3u8#第2集$https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8'
        },
        {
            'name': '三体',
            'keywords': ['三体', '刘慈欣', '科幻'],
            'type': '电视剧',
            'year': '2023',
            'note': '30集全',
            'source': '资源站',
            'pic': '',
            'play_url': '第1集$https://demo.unified-streaming.com/k8s/features/stable/video/tears-of-steel/tears-of-steel.ism/.m3u8#第2集$https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8'
        },
        {
            'name': '流浪地球2',
            'keywords': ['流浪地球', '吴京', '刘德华', '科幻'],
            'type': '电影',
            'year': '2023',
            'note': 'HD',
            'source': '资源站',
            'pic': '',
            'play_url': '超清$https://bitdash-a.akamaihd.net/content/sintel/hls/playlist.m3u8'
        },
        {
            'name': '大雄兔 Big Buck Bunny',
            'keywords': ['大雄', '兔子', 'bunny', '动画', '测试'],
            'type': '动画',
            'year': '2008',
            'note': '测试视频',
            'source': '公开资源',
            'pic': '',
            'play_url': '超清$https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8#标清$https://www.w3schools.com/html/mov_bbb.mp4'
        },
        {
            'name': 'Sintel 辛特尔',
            'keywords': ['sintel', '辛特尔', '动画', '龙'],
            'type': '动画',
            'year': '2010',
            'note': '测试视频',
            'source': '公开资源',
            'pic': '',
            'play_url': '4K$https://bitdash-a.akamaihd.net/content/sintel/hls/playlist.m3u8'
        },
    ]
    
    # 搜索匹配
    results = []
    for item in movie_db:
        matched = any(kw in keyword for kw in item['keywords']) or keyword in item['name'].lower()
        if matched:
            results.append({
                'name': item['name'],
                'type': item['type'],
                'year': item['year'],
                'note': item['note'],
                'source': item['source'],
                'pic': item['pic'],
                'play_url': item['play_url']
            })
    
    # 没有匹配则返回全部
    if not results:
        results = [{
            'name': item['name'],
            'type': item['type'],
            'year': item['year'],
            'note': item['note'],
            'source': item['source'],
            'pic': item['pic'],
            'play_url': item['play_url']
        } for item in movie_db]
    
    return jsonify({
        'code': 0,
        'message': f'找到 {len(results)} 个结果',
        'data': results
    })


@app.route('/api/search/resource')
def search_resource():
    """
    从第三方资源站搜索视频
    包含测试数据，确保能看到效果
    """
    keyword = request.args.get('keyword', '').lower()
    
    if not keyword:
        return jsonify({'code': -1, 'message': '缺少搜索关键词'})
    
    # 内置测试数据 - 使用公开可用的视频源
    test_data = [
        {
            'name': '大雄兔 Big Buck Bunny',
            'keywords': ['大雄', '兔子', 'bunny', 'buck', '测试', 'test'],
            'source': '测试资源',
            'type': '动画短片',
            'year': '2008',
            'note': '高清',
            'play_url': '超清$https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8#标清$https://www.w3schools.com/html/mov_bbb.mp4',
        },
        {
            'name': 'Sintel 辛特尔',
            'keywords': ['sintel', '辛特尔', '龙', '动画', '测试'],
            'source': '测试资源',
            'type': '动画短片', 
            'year': '2010',
            'note': '4K',
            'play_url': '高清$https://bitdash-a.akamaihd.net/content/sintel/hls/playlist.m3u8',
        },
        {
            'name': 'Tears of Steel 钢铁之泪',
            'keywords': ['tears', 'steel', '钢铁', '科幻', '测试'],
            'source': '测试资源',
            'type': '科幻短片',
            'year': '2012', 
            'note': '1080P',
            'play_url': '1080P$https://demo.unified-streaming.com/k8s/features/stable/video/tears-of-steel/tears-of-steel.ism/.m3u8',
        },
        {
            'name': '测试视频合集',
            'keywords': ['测试', 'test', '演示', 'demo'],
            'source': '演示数据',
            'type': '测试',
            'year': '2024',
            'note': '多集',
            'play_url': '第1集$https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8#第2集$https://bitdash-a.akamaihd.net/content/sintel/hls/playlist.m3u8#第3集$https://www.w3schools.com/html/mov_bbb.mp4',
        },
        {
            'name': '长安十二时辰 (演示)',
            'keywords': ['长安', '十二时辰', '古装'],
            'source': '演示数据',
            'type': '电视剧',
            'year': '2019',
            'note': '演示用',
            'play_url': '第1集(演示)$https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8#第2集(演示)$https://bitdash-a.akamaihd.net/content/sintel/hls/playlist.m3u8',
        },
        {
            'name': '唐探1900 (演示)',
            'keywords': ['唐探', '唐人街', '1900', '电影'],
            'source': '演示数据',
            'type': '电影',
            'year': '2025',
            'note': '演示用',
            'play_url': '高清(演示)$https://bitdash-a.akamaihd.net/content/sintel/hls/playlist.m3u8',
        },
    ]
    
    # 搜索匹配
    results = []
    for item in test_data:
        # 检查关键词匹配
        matched = any(kw in keyword for kw in item['keywords']) or keyword in item['name'].lower()
        if matched:
            results.append({
                'source': item['source'],
                'name': item['name'],
                'type': item['type'],
                'year': item['year'],
                'note': item['note'],
                'play_url': item['play_url'],
            })
    
    # 如果没有匹配，返回所有测试数据供选择
    if not results:
        results = [{
            'source': item['source'],
            'name': item['name'],
            'type': item['type'],
            'year': item['year'],
            'note': item['note'],
            'play_url': item['play_url'],
        } for item in test_data]
        message = f'未找到"{keyword}"，显示全部测试资源 ({len(results)}个)'
    else:
        message = f'找到 {len(results)} 个结果'
    
    return jsonify({
        'code': 0,
        'message': message,
        'data': results
    })


@app.route('/api/proxy/image')
def proxy_image():
    """代理图片 (解决防盗链)"""
    url = request.args.get('url', '')
    
    if not url:
        return Response('Missing URL', status=400)
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        
        return Response(
            resp.content,
            content_type=resp.headers.get('Content-Type', 'image/jpeg'),
            headers={'Access-Control-Allow-Origin': '*'}
        )
    except Exception as e:
        return Response(f'Proxy error: {str(e)}', status=500)


if __name__ == '__main__':
    print("")
    print("=" * 60)
    print("   StreamLab - Streaming Technology Research")
    print("=" * 60)
    print("")
    print("   URL: http://localhost:5000")
    print("")
    print("   Research Topics:")
    print("   - Video Streaming Protocol (HLS/DASH)")
    print("   - Real-time Text Overlay Rendering")
    print("   - API Reverse Engineering")
    print("")
    print("=" * 60)
    print("")
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)

