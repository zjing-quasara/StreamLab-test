/**
 * 视频播放器控制器
 * 处理视频加载、播放控制、弹幕集成
 */

class VideoPlayer {
    constructor() {
        // DOM元素
        this.video = document.getElementById('videoPlayer');
        this.canvas = document.getElementById('danmakuCanvas');
        this.playerWrapper = document.getElementById('playerWrapper');
        
        // 控制元素
        this.playBtn = document.getElementById('playBtn');
        this.volumeBtn = document.getElementById('volumeBtn');
        this.volumeSlider = document.getElementById('volumeSlider');
        this.fullscreenBtn = document.getElementById('fullscreenBtn');
        this.danmakuToggle = document.getElementById('danmakuToggle');
        this.qualitySelect = document.getElementById('qualitySelect');
        
        // 进度条
        this.progressBar = document.getElementById('progressBar');
        this.progressPlayed = document.getElementById('progressPlayed');
        this.progressBuffered = document.getElementById('progressBuffered');
        this.progressThumb = document.getElementById('progressThumb');
        
        // 时间显示
        this.currentTimeEl = document.getElementById('currentTime');
        this.totalTimeEl = document.getElementById('totalTime');
        
        // 加载层
        this.loadingOverlay = document.getElementById('loadingOverlay');
        this.loadingText = document.getElementById('loadingText');
        
        // 其他元素
        this.searchInput = document.getElementById('searchInput');
        this.searchBtn = document.getElementById('searchBtn');
        this.videoInfo = document.getElementById('videoInfo');
        this.controlsOverlay = document.getElementById('controlsOverlay');
        
        // 状态
        this.currentVideo = null;
        this.currentCid = null;
        this.isLoading = false;
        
        // 弹幕引擎
        this.danmaku = new DanmakuEngine(this.canvas, this.video);
        
        // 初始化
        this.bindEvents();
        this.initSettings();
    }
    
    /**
     * 绑定事件
     */
    bindEvents() {
        // 搜索
        this.searchBtn.addEventListener('click', () => this.search());
        this.searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.search();
        });
        
        // 播放控制
        this.playBtn.addEventListener('click', () => this.togglePlay());
        this.video.addEventListener('click', () => this.togglePlay());
        
        // 音量控制
        this.volumeBtn.addEventListener('click', () => this.toggleMute());
        this.volumeSlider.addEventListener('input', (e) => {
            this.video.volume = e.target.value / 100;
            this.updateVolumeIcon();
        });
        
        // 全屏
        this.fullscreenBtn.addEventListener('click', () => this.toggleFullscreen());
        
        // 弹幕开关
        this.danmakuToggle.addEventListener('click', () => {
            const enabled = this.danmaku.toggle();
            this.danmakuToggle.classList.toggle('active', enabled);
            this.showToast(enabled ? '弹幕已开启' : '弹幕已关闭', 'info');
        });
        
        // 画质选择
        this.qualitySelect.addEventListener('change', () => {
            if (this.currentVideo) {
                this.loadVideo(this.currentVideo.bvid, this.currentCid);
            }
        });
        
        // 进度条
        this.progressBar.addEventListener('click', (e) => this.seekTo(e));
        this.progressBar.addEventListener('mousemove', (e) => this.updateThumb(e));
        
        // 视频事件
        this.video.addEventListener('loadedmetadata', () => this.onVideoLoaded());
        this.video.addEventListener('timeupdate', () => this.onTimeUpdate());
        this.video.addEventListener('progress', () => this.onProgress());
        this.video.addEventListener('play', () => this.onPlay());
        this.video.addEventListener('pause', () => this.onPause());
        this.video.addEventListener('waiting', () => this.showLoading('缓冲中...'));
        this.video.addEventListener('playing', () => this.hideLoading());
        this.video.addEventListener('error', (e) => this.onError(e));
        
        // 键盘快捷键
        document.addEventListener('keydown', (e) => this.handleKeyboard(e));
        
        // 控制栏显示/隐藏
        let hideTimeout;
        this.playerWrapper.addEventListener('mousemove', () => {
            this.controlsOverlay.classList.add('visible');
            clearTimeout(hideTimeout);
            hideTimeout = setTimeout(() => {
                if (!this.video.paused) {
                    this.controlsOverlay.classList.remove('visible');
                }
            }, 3000);
        });
        
        // 主题切换
        document.getElementById('themeToggle').addEventListener('click', () => {
            const current = document.body.dataset.theme || 'dark';
            const next = current === 'dark' ? 'light' : 'dark';
            document.body.dataset.theme = next;
            document.getElementById('themeToggle').textContent = next === 'dark' ? '🌙' : '☀️';
        });
    }
    
    /**
     * 初始化设置
     */
    initSettings() {
        // 音量
        this.video.volume = 0.8;
        
        // 弹幕设置
        const opacitySlider = document.getElementById('danmakuOpacity');
        const speedSlider = document.getElementById('danmakuSpeed');
        const sizeSlider = document.getElementById('danmakuSize');
        const areaSelect = document.getElementById('danmakuArea');
        
        opacitySlider.addEventListener('input', (e) => {
            const value = e.target.value / 100;
            this.danmaku.setConfig('opacity', value);
            document.getElementById('opacityValue').textContent = e.target.value + '%';
        });
        
        speedSlider.addEventListener('input', (e) => {
            const value = e.target.value / 100;
            this.danmaku.setConfig('speed', value);
            document.getElementById('speedValue').textContent = value.toFixed(1) + 'x';
        });
        
        sizeSlider.addEventListener('input', (e) => {
            const value = parseInt(e.target.value);
            this.danmaku.setConfig('fontSize', value);
            document.getElementById('sizeValue').textContent = value + 'px';
        });
        
        areaSelect.addEventListener('change', (e) => {
            const value = parseFloat(e.target.value);
            this.danmaku.setConfig('areaRatio', value);
        });
    }
    
    /**
     * 搜索/解析视频
     */
    async search() {
        const input = this.searchInput.value.trim();
        if (!input) {
            this.showToast('请输入内容', 'error');
            return;
        }
        
        // 判断输入类型
        const isBiliUrl = input.includes('bilibili.com') || input.startsWith('BV') || input.startsWith('bv');
        const isDirectUrl = input.includes('.m3u8') || input.includes('.mp4') || input.includes('.flv');
        const isOtherPlatform = input.includes('iqiyi.com') || input.includes('youku.com') || 
                                input.includes('v.qq.com') || input.includes('mgtv.com');
        
        if (isDirectUrl) {
            // 直接播放URL
            this.playM3u8(input, '直接播放');
        } else if (isBiliUrl) {
            // B站视频解析
            await this.searchBilibili(input);
        } else if (isOtherPlatform) {
            // 其他平台，尝试解析接口
            await this.parseWithJx(input);
        } else {
            // 资源站搜索
            await this.searchResource(input);
        }
    }
    
    /**
     * 使用第三方解析接口 (演示VIP解析原理)
     */
    async parseWithJx(url) {
        this.showLoading('正在调用解析接口...');
        
        // 显示解析接口原理
        this.videoInfo.innerHTML = \`
            <h2 class="video-title">VIP解析原理演示</h2>
            <p class="video-desc">
                第三方解析接口会使用共享VIP账号获取视频地址。<br>
                由于接口不稳定，这里只演示原理。<br><br>
                <strong>常用解析接口格式:</strong><br>
                https://jx.xxx.com/?url=\${url.substring(0, 30)}...
            </p>
        \`;
        
        this.showLoading('解析接口演示 - 实际需要可用的接口');
        this.showToast('解析接口需要外部服务支持', 'info');
    }
    
    /**
     * B站视频解析
     */
    async searchBilibili(input) {
        this.showLoading('正在解析B站视频...');
        
        try {
            const resp = await fetch(`/api/video/info?bvid=${encodeURIComponent(input)}`);
            const data = await resp.json();
            
            if (data.code !== 0) {
                throw new Error(data.message);
            }
            
            this.currentVideo = data.data;
            this.currentCid = data.data.cid;
            this.currentEpId = data.data.ep_id || null;
            this.videoType = data.data.type || 'video';
            
            this.showVideoInfo(data.data);
            this.showEpisodes(data.data.pages, data.data.type === 'bangumi');
            this.showStats(data.data.stat);
            
            await this.loadVideo(data.data.bvid, data.data.cid, data.data.ep_id);
            
        } catch (error) {
            this.showLoading('解析失败: ' + error.message);
            this.showToast('B站解析失败，尝试资源站搜索...', 'info');
            // 失败后尝试资源站搜索
            await this.searchResource(input);
        }
    }
    
    /**
     * 资源站搜索 (核心功能 - 不需要VIP)
     */
    async searchResource(keyword) {
        this.showLoading('正在搜索资源站...');
        
        try {
            const resp = await fetch(`/api/search/resource?keyword=${encodeURIComponent(keyword)}`);
            const data = await resp.json();
            
            if (data.code !== 0 || !data.data || data.data.length === 0) {
                throw new Error('未找到相关资源');
            }
            
            // 显示搜索结果
            this.showSearchResults(data.data);
            this.hideLoading();
            this.showToast(`找到 ${data.data.length} 个资源`, 'success');
            
        } catch (error) {
            this.showLoading('搜索失败: ' + error.message);
            this.showToast(error.message, 'error');
        }
    }
    
    /**
     * 显示搜索结果列表
     */
    showSearchResults(results) {
        const panel = document.getElementById('episodePanel');
        const list = document.getElementById('episodeList');
        const title = panel.querySelector('.panel-title');
        
        title.textContent = '搜索结果';
        panel.style.display = 'block';
        
        // 隐藏统计面板
        document.getElementById('statsPanel').style.display = 'none';
        
        list.innerHTML = results.map((item, i) => `
            <div class="episode-item search-result" data-index="${i}" data-play-url="${this.escapeHtml(item.play_url || '')}">
                <div class="result-title">${this.escapeHtml(item.name)}</div>
                <div class="result-meta">
                    <span class="result-source">${this.escapeHtml(item.source)}</span>
                    <span class="result-note">${this.escapeHtml(item.note || item.year || '')}</span>
                </div>
            </div>
        `).join('');
        
        // 绑定点击事件
        list.querySelectorAll('.search-result').forEach(item => {
            item.addEventListener('click', () => {
                const playUrl = item.dataset.playUrl;
                list.querySelectorAll('.episode-item').forEach(el => el.classList.remove('active'));
                item.classList.add('active');
                
                if (playUrl) {
                    this.parseAndPlay(playUrl, item.querySelector('.result-title').textContent);
                } else {
                    this.showToast('该资源暂无播放地址', 'error');
                }
            });
        });
        
        // 更新视频信息区域
        this.videoInfo.innerHTML = `
            <h2 class="video-title">搜索: ${this.escapeHtml(this.searchInput.value)}</h2>
            <p class="video-desc">从资源站找到 ${results.length} 个结果，点击右侧列表选择播放</p>
        `;
    }
    
    /**
     * 解析播放地址并播放
     */
    parseAndPlay(playUrl, title) {
        // 播放地址格式通常是: "线路1$url1#线路2$url2"
        // 或者 "第1集$url1#第2集$url2"
        
        const episodes = playUrl.split('#').filter(Boolean);
        
        if (episodes.length > 1) {
            // 多集，显示剧集列表
            this.showEpisodeList(episodes, title);
        } else {
            // 单集，直接播放
            const url = this.extractUrl(episodes[0]);
            if (url) {
                this.playM3u8(url, title);
            }
        }
    }
    
    /**
     * 显示剧集列表
     */
    showEpisodeList(episodes, title) {
        const panel = document.getElementById('episodePanel');
        const list = document.getElementById('episodeList');
        const titleEl = panel.querySelector('.panel-title');
        
        titleEl.textContent = '剧集列表';
        
        list.innerHTML = episodes.map((ep, i) => {
            const parts = ep.split('$');
            const name = parts[0] || `第${i + 1}集`;
            const url = parts[1] || '';
            return `
                <div class="episode-item" data-url="${this.escapeHtml(url)}" data-index="${i}">
                    <span class="episode-number">${this.escapeHtml(name)}</span>
                </div>
            `;
        }).join('');
        
        // 更新视频信息
        this.videoInfo.innerHTML = `
            <h2 class="video-title">${this.escapeHtml(title)}</h2>
            <p class="video-desc">共 ${episodes.length} 集，点击右侧列表选择播放</p>
        `;
        
        // 绑定点击
        list.querySelectorAll('.episode-item').forEach(item => {
            item.addEventListener('click', () => {
                const url = item.dataset.url;
                list.querySelectorAll('.episode-item').forEach(el => el.classList.remove('active'));
                item.classList.add('active');
                
                if (url) {
                    this.playM3u8(url, title);
                }
            });
        });
        
        // 自动播放第一集
        const firstUrl = this.extractUrl(episodes[0]);
        if (firstUrl) {
            list.querySelector('.episode-item').classList.add('active');
            this.playM3u8(firstUrl, title);
        }
    }
    
    /**
     * 从播放地址中提取URL
     */
    extractUrl(str) {
        if (!str) return null;
        const parts = str.split('$');
        const url = parts.length > 1 ? parts[1] : parts[0];
        
        // 验证是否是有效URL
        if (url && (url.startsWith('http') || url.startsWith('//'))) {
            return url.startsWith('//') ? 'https:' + url : url;
        }
        return null;
    }
    
    /**
     * 播放M3U8视频 (资源站的视频格式)
     */
    async playM3u8(url, title = '') {
        this.showLoading('正在加载视频...');
        
        try {
            // 通过代理播放，解决跨域问题
            const proxyUrl = `/api/proxy/video?url=${encodeURIComponent(url)}`;
            
            // 检查是否是m3u8格式
            if (url.includes('.m3u8')) {
                // m3u8需要使用HLS.js
                if (typeof Hls !== 'undefined' && Hls.isSupported()) {
                    if (this.hls) {
                        this.hls.destroy();
                    }
                    this.hls = new Hls();
                    this.hls.loadSource(proxyUrl);
                    this.hls.attachMedia(this.video);
                    this.hls.on(Hls.Events.MANIFEST_PARSED, () => {
                        this.video.play();
                        this.hideLoading();
                    });
                } else if (this.video.canPlayType('application/vnd.apple.mpegurl')) {
                    // Safari原生支持
                    this.video.src = proxyUrl;
                    this.video.play();
                } else {
                    // 降级：直接尝试播放
                    this.video.src = proxyUrl;
                    this.video.play();
                }
            } else {
                // MP4等格式直接播放
                this.video.src = proxyUrl;
                this.video.play();
            }
            
            // 更新标题
            if (title) {
                this.videoInfo.querySelector('.video-title').textContent = title;
            }
            
            this.showToast('开始播放', 'success');
            
            // 资源站视频没有弹幕
            this.danmaku.clear();
            
        } catch (error) {
            this.showLoading('播放失败: ' + error.message);
            this.showToast('播放失败', 'error');
        }
    }
    
    /**
     * 加载视频
     */
    async loadVideo(bvid, cid, epId = null) {
        this.showLoading('正在获取播放地址...');
        
        try {
            const quality = this.qualitySelect.value;
            
            // 构建请求URL
            let apiUrl = `/api/video/playurl?cid=${cid}&quality=${quality}`;
            if (this.videoType === 'bangumi' && epId) {
                apiUrl += `&ep_id=${epId}&type=bangumi`;
            } else if (bvid) {
                apiUrl += `&bvid=${bvid}`;
            }
            
            // 获取播放地址
            const resp = await fetch(apiUrl);
            const data = await resp.json();
            
            if (data.code !== 0) {
                throw new Error(data.message);
            }
            
            const playData = data.data;
            
            // 通过代理加载视频
            if (playData.video_url) {
                const proxyUrl = `/api/proxy/video?url=${encodeURIComponent(playData.video_url)}`;
                this.video.src = proxyUrl;
            } else {
                throw new Error('未获取到视频地址');
            }
            
            this.currentCid = cid;
            this.currentEpId = epId;
            
            // 加载弹幕
            this.loadDanmaku(cid);
            
            // 开始播放
            this.video.play().catch(() => {});
            
        } catch (error) {
            this.showLoading('加载失败: ' + error.message);
            this.showToast('加载视频失败: ' + error.message, 'error');
        }
    }
    
    /**
     * 加载弹幕
     */
    async loadDanmaku(cid) {
        try {
            const resp = await fetch(`/api/danmaku?cid=${cid}`);
            const data = await resp.json();
            
            if (data.code === 0) {
                this.danmaku.load(data.data.danmakus);
                this.showToast(`已加载 ${data.data.count} 条弹幕`, 'success');
            }
        } catch (error) {
            console.error('加载弹幕失败:', error);
        }
    }
    
    /**
     * 显示视频信息
     */
    showVideoInfo(data) {
        const avatarUrl = `/api/proxy/image?url=${encodeURIComponent(data.owner.face)}`;
        
        this.videoInfo.innerHTML = `
            <h2 class="video-title">${this.escapeHtml(data.title)}</h2>
            <div class="video-meta">
                <div class="author-info">
                    <img class="author-avatar" src="${avatarUrl}" alt="">
                    <span class="author-name">${this.escapeHtml(data.owner.name)}</span>
                </div>
            </div>
            <p class="video-desc">${this.escapeHtml(data.desc || '暂无简介')}</p>
        `;
    }
    
    /**
     * 显示分P/剧集列表
     */
    showEpisodes(pages, isBangumi = false) {
        const panel = document.getElementById('episodePanel');
        const list = document.getElementById('episodeList');
        const title = panel.querySelector('.panel-title');
        
        if (pages.length <= 1) {
            panel.style.display = 'none';
            return;
        }
        
        // 修改标题
        title.textContent = isBangumi ? '📺 剧集列表' : '📑 分P列表';
        
        panel.style.display = 'block';
        list.innerHTML = pages.map((p, i) => `
            <div class="episode-item ${i === 0 ? 'active' : ''}" data-cid="${p.cid}" data-index="${i}" data-ep-id="${p.ep_id || ''}">
                <span class="episode-number">${isBangumi ? '第' + p.page + '集' : 'P' + p.page}</span>
                <span class="episode-title">${this.escapeHtml(p.part)}</span>
            </div>
        `).join('');
        
        // 绑定点击事件
        list.querySelectorAll('.episode-item').forEach(item => {
            item.addEventListener('click', () => {
                const cid = item.dataset.cid;
                const epId = item.dataset.epId || null;
                list.querySelectorAll('.episode-item').forEach(el => el.classList.remove('active'));
                item.classList.add('active');
                this.loadVideo(this.currentVideo.bvid, cid, epId);
            });
        });
    }
    
    /**
     * 显示统计信息
     */
    showStats(stat) {
        const panel = document.getElementById('statsPanel');
        panel.style.display = 'block';
        
        document.getElementById('statViews').textContent = this.formatNumber(stat.view);
        document.getElementById('statDanmaku').textContent = this.formatNumber(stat.danmaku);
        document.getElementById('statLikes').textContent = this.formatNumber(stat.like);
        document.getElementById('statCoins').textContent = this.formatNumber(stat.coin);
    }
    
    /**
     * 播放/暂停切换
     */
    togglePlay() {
        if (this.video.paused) {
            this.video.play();
        } else {
            this.video.pause();
        }
    }
    
    /**
     * 静音切换
     */
    toggleMute() {
        this.video.muted = !this.video.muted;
        this.volumeSlider.value = this.video.muted ? 0 : this.video.volume * 100;
        this.updateVolumeIcon();
    }
    
    /**
     * 更新音量图标
     */
    updateVolumeIcon() {
        const volume = this.video.muted ? 0 : this.video.volume;
        if (volume === 0) {
            this.volumeBtn.textContent = '🔇';
        } else if (volume < 0.5) {
            this.volumeBtn.textContent = '🔉';
        } else {
            this.volumeBtn.textContent = '🔊';
        }
    }
    
    /**
     * 全屏切换
     */
    toggleFullscreen() {
        if (document.fullscreenElement) {
            document.exitFullscreen();
        } else {
            this.playerWrapper.requestFullscreen();
        }
    }
    
    /**
     * 跳转到指定位置
     */
    seekTo(e) {
        const rect = this.progressBar.getBoundingClientRect();
        const percent = (e.clientX - rect.left) / rect.width;
        this.video.currentTime = percent * this.video.duration;
    }
    
    /**
     * 更新进度条滑块位置
     */
    updateThumb(e) {
        const rect = this.progressBar.getBoundingClientRect();
        const percent = (e.clientX - rect.left) / rect.width;
        this.progressThumb.style.left = (percent * 100) + '%';
    }
    
    /**
     * 视频加载完成
     */
    onVideoLoaded() {
        this.totalTimeEl.textContent = this.formatTime(this.video.duration);
        this.hideLoading();
    }
    
    /**
     * 时间更新
     */
    onTimeUpdate() {
        const percent = (this.video.currentTime / this.video.duration) * 100;
        this.progressPlayed.style.width = percent + '%';
        this.progressThumb.style.left = percent + '%';
        this.currentTimeEl.textContent = this.formatTime(this.video.currentTime);
    }
    
    /**
     * 缓冲进度更新
     */
    onProgress() {
        if (this.video.buffered.length > 0) {
            const buffered = this.video.buffered.end(this.video.buffered.length - 1);
            const percent = (buffered / this.video.duration) * 100;
            this.progressBuffered.style.width = percent + '%';
        }
    }
    
    /**
     * 播放状态
     */
    onPlay() {
        this.playBtn.textContent = '⏸';
    }
    
    /**
     * 暂停状态
     */
    onPause() {
        this.playBtn.textContent = '▶';
    }
    
    /**
     * 错误处理
     */
    onError(e) {
        console.error('视频加载错误:', e);
        this.showLoading('视频加载失败，请重试');
        this.showToast('视频加载失败', 'error');
    }
    
    /**
     * 键盘控制
     */
    handleKeyboard(e) {
        // 忽略输入框
        if (e.target.tagName === 'INPUT') return;
        
        switch (e.code) {
            case 'Space':
                e.preventDefault();
                this.togglePlay();
                break;
            case 'ArrowLeft':
                this.video.currentTime -= 5;
                break;
            case 'ArrowRight':
                this.video.currentTime += 5;
                break;
            case 'ArrowUp':
                e.preventDefault();
                this.video.volume = Math.min(1, this.video.volume + 0.1);
                this.volumeSlider.value = this.video.volume * 100;
                break;
            case 'ArrowDown':
                e.preventDefault();
                this.video.volume = Math.max(0, this.video.volume - 0.1);
                this.volumeSlider.value = this.video.volume * 100;
                break;
            case 'KeyF':
                this.toggleFullscreen();
                break;
            case 'KeyM':
                this.toggleMute();
                break;
            case 'KeyD':
                this.danmaku.toggle();
                this.danmakuToggle.classList.toggle('active');
                break;
        }
    }
    
    /**
     * 显示加载
     */
    showLoading(text) {
        this.loadingText.textContent = text;
        this.loadingOverlay.classList.remove('hidden');
    }
    
    /**
     * 隐藏加载
     */
    hideLoading() {
        this.loadingOverlay.classList.add('hidden');
    }
    
    /**
     * 显示Toast消息
     */
    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        container.appendChild(toast);
        
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
    
    /**
     * 格式化时间
     */
    formatTime(seconds) {
        if (!seconds || isNaN(seconds)) return '00:00';
        const m = Math.floor(seconds / 60);
        const s = Math.floor(seconds % 60);
        return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    }
    
    /**
     * 格式化数字
     */
    formatNumber(num) {
        if (num >= 100000000) {
            return (num / 100000000).toFixed(1) + '亿';
        } else if (num >= 10000) {
            return (num / 10000).toFixed(1) + '万';
        }
        return num.toString();
    }
    
    /**
     * HTML转义
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// 初始化播放器
document.addEventListener('DOMContentLoaded', () => {
    window.player = new VideoPlayer();
});

