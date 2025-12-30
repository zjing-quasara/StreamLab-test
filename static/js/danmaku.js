/**
 * 高性能弹幕渲染引擎
 * 使用 Canvas 2D 渲染，支持滚动、顶部、底部弹幕
 */

class DanmakuEngine {
    constructor(canvas, video) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.video = video;
        
        // 弹幕数据
        this.danmakus = [];        // 原始弹幕数据
        this.activeDanmakus = [];  // 当前活跃的弹幕
        this.danmakuIndex = 0;     // 当前处理到的弹幕索引
        
        // 配置
        this.config = {
            opacity: 0.8,
            speed: 1.0,
            fontSize: 24,
            fontFamily: '"Noto Sans SC", "Microsoft YaHei", sans-serif',
            areaRatio: 0.5,    // 弹幕显示区域比例
            trackHeight: 32,    // 弹幕轨道高度
            enabled: true
        };
        
        // 轨道管理
        this.tracks = {
            scroll: [],   // 滚动弹幕轨道
            top: [],      // 顶部弹幕轨道
            bottom: []    // 底部弹幕轨道
        };
        
        // 状态
        this.isPlaying = false;
        this.lastTime = 0;
        this.animationId = null;
        
        // 初始化
        this.resize();
        this.bindEvents();
    }
    
    /**
     * 绑定事件
     */
    bindEvents() {
        // 监听视频播放状态
        this.video.addEventListener('play', () => this.start());
        this.video.addEventListener('pause', () => this.pause());
        this.video.addEventListener('seeking', () => this.seek());
        this.video.addEventListener('ended', () => this.pause());
        
        // 监听窗口大小变化
        window.addEventListener('resize', () => this.resize());
        
        // ResizeObserver 监听容器大小
        if (typeof ResizeObserver !== 'undefined') {
            const observer = new ResizeObserver(() => this.resize());
            observer.observe(this.canvas.parentElement);
        }
    }
    
    /**
     * 调整画布大小
     */
    resize() {
        const rect = this.canvas.parentElement.getBoundingClientRect();
        const dpr = window.devicePixelRatio || 1;
        
        this.canvas.width = rect.width * dpr;
        this.canvas.height = rect.height * dpr;
        this.canvas.style.width = rect.width + 'px';
        this.canvas.style.height = rect.height + 'px';
        
        this.ctx.scale(dpr, dpr);
        
        this.width = rect.width;
        this.height = rect.height;
        
        // 重新计算轨道数量
        this.calculateTracks();
    }
    
    /**
     * 计算轨道
     */
    calculateTracks() {
        const areaHeight = this.height * this.config.areaRatio;
        const trackCount = Math.floor(areaHeight / this.config.trackHeight);
        
        this.tracks.scroll = new Array(trackCount).fill(0);
        this.tracks.top = new Array(Math.min(trackCount, 5)).fill(0);
        this.tracks.bottom = new Array(Math.min(trackCount, 5)).fill(0);
    }
    
    /**
     * 加载弹幕数据
     */
    load(danmakus) {
        // 按时间排序
        this.danmakus = danmakus.sort((a, b) => a.time - b.time);
        this.danmakuIndex = 0;
        this.activeDanmakus = [];
        this.calculateTracks();
        
        console.log(`📝 已加载 ${this.danmakus.length} 条弹幕`);
    }
    
    /**
     * 清空弹幕
     */
    clear() {
        this.danmakus = [];
        this.activeDanmakus = [];
        this.danmakuIndex = 0;
        this.ctx.clearRect(0, 0, this.width, this.height);
    }
    
    /**
     * 开始渲染
     */
    start() {
        if (!this.config.enabled) return;
        
        this.isPlaying = true;
        this.lastTime = performance.now();
        this.render();
    }
    
    /**
     * 暂停渲染
     */
    pause() {
        this.isPlaying = false;
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
    }
    
    /**
     * 跳转时重置弹幕
     */
    seek() {
        const currentTime = this.video.currentTime;
        
        // 清空活跃弹幕
        this.activeDanmakus = [];
        
        // 重置轨道
        this.calculateTracks();
        
        // 找到当前时间对应的弹幕索引
        this.danmakuIndex = this.danmakus.findIndex(d => d.time > currentTime);
        if (this.danmakuIndex === -1) {
            this.danmakuIndex = this.danmakus.length;
        }
        
        // 清空画布
        this.ctx.clearRect(0, 0, this.width, this.height);
    }
    
    /**
     * 主渲染循环
     */
    render() {
        if (!this.isPlaying) return;
        
        const now = performance.now();
        const delta = (now - this.lastTime) / 1000;
        this.lastTime = now;
        
        // 清空画布
        this.ctx.clearRect(0, 0, this.width, this.height);
        
        if (!this.config.enabled) {
            this.animationId = requestAnimationFrame(() => this.render());
            return;
        }
        
        const currentTime = this.video.currentTime;
        
        // 添加新弹幕
        this.addNewDanmakus(currentTime);
        
        // 更新和绘制弹幕
        this.updateAndDraw(delta);
        
        // 下一帧
        this.animationId = requestAnimationFrame(() => this.render());
    }
    
    /**
     * 添加新弹幕到活跃列表
     */
    addNewDanmakus(currentTime) {
        while (this.danmakuIndex < this.danmakus.length) {
            const d = this.danmakus[this.danmakuIndex];
            
            if (d.time > currentTime + 0.1) break;
            if (d.time < currentTime - 0.5) {
                this.danmakuIndex++;
                continue;
            }
            
            // 创建活跃弹幕对象
            const danmaku = this.createDanmaku(d);
            if (danmaku) {
                this.activeDanmakus.push(danmaku);
            }
            
            this.danmakuIndex++;
        }
    }
    
    /**
     * 创建弹幕对象
     */
    createDanmaku(data) {
        const fontSize = Math.round(data.size * this.config.fontSize / 25);
        
        // 设置字体以测量文字宽度
        this.ctx.font = `bold ${fontSize}px ${this.config.fontFamily}`;
        const textWidth = this.ctx.measureText(data.text).width;
        
        // 根据弹幕类型分配轨道
        let track, x, y, speed;
        
        if (data.mode === 4) {
            // 底部弹幕
            track = this.findAvailableTrack('bottom', textWidth, 5);
            if (track === -1) return null;
            
            x = (this.width - textWidth) / 2;
            y = this.height - (track + 1) * this.config.trackHeight;
            speed = 0;
            
            this.tracks.bottom[track] = Date.now() + 4000;
        } else if (data.mode === 5) {
            // 顶部弹幕
            track = this.findAvailableTrack('top', textWidth, 5);
            if (track === -1) return null;
            
            x = (this.width - textWidth) / 2;
            y = (track + 1) * this.config.trackHeight;
            speed = 0;
            
            this.tracks.top[track] = Date.now() + 4000;
        } else {
            // 滚动弹幕 (默认)
            track = this.findAvailableTrack('scroll', textWidth, 8);
            if (track === -1) return null;
            
            x = this.width;
            y = (track + 1) * this.config.trackHeight;
            
            // 根据弹幕长度计算速度，保证8秒内穿过屏幕
            speed = (this.width + textWidth) / 8 * this.config.speed;
            
            // 记录轨道占用时间
            const duration = this.width / speed;
            this.tracks.scroll[track] = Date.now() + duration * 1000;
        }
        
        return {
            text: data.text,
            x: x,
            y: y,
            speed: speed,
            color: this.intToColor(data.color),
            fontSize: fontSize,
            width: textWidth,
            mode: data.mode,
            opacity: this.config.opacity,
            createdAt: Date.now(),
            duration: data.mode === 1 ? 8000 : 4000
        };
    }
    
    /**
     * 查找可用轨道
     */
    findAvailableTrack(type, textWidth, duration) {
        const tracks = this.tracks[type];
        const now = Date.now();
        
        for (let i = 0; i < tracks.length; i++) {
            if (tracks[i] < now) {
                return i;
            }
        }
        
        return -1; // 没有可用轨道，丢弃弹幕
    }
    
    /**
     * 更新和绘制弹幕
     */
    updateAndDraw(delta) {
        const now = Date.now();
        
        // 过滤掉已经消失的弹幕
        this.activeDanmakus = this.activeDanmakus.filter(d => {
            // 滚动弹幕：检查是否已经滚出屏幕
            if (d.speed > 0) {
                return d.x + d.width > 0;
            }
            // 固定弹幕：检查是否已经超时
            return now - d.createdAt < d.duration;
        });
        
        // 更新位置并绘制
        for (const d of this.activeDanmakus) {
            // 更新位置
            if (d.speed > 0) {
                d.x -= d.speed * delta;
            }
            
            // 计算透明度（固定弹幕淡出效果）
            let alpha = d.opacity;
            if (d.speed === 0) {
                const elapsed = now - d.createdAt;
                const remaining = d.duration - elapsed;
                if (remaining < 500) {
                    alpha *= remaining / 500;
                }
            }
            
            // 绘制弹幕
            this.drawDanmaku(d, alpha);
        }
    }
    
    /**
     * 绘制单条弹幕
     */
    drawDanmaku(d, alpha) {
        this.ctx.save();
        
        this.ctx.globalAlpha = alpha;
        this.ctx.font = `bold ${d.fontSize}px ${this.config.fontFamily}`;
        this.ctx.textBaseline = 'middle';
        
        // 绘制描边（黑色轮廓）
        this.ctx.strokeStyle = 'rgba(0, 0, 0, 0.8)';
        this.ctx.lineWidth = 2;
        this.ctx.lineJoin = 'round';
        this.ctx.strokeText(d.text, d.x, d.y);
        
        // 绘制填充（弹幕颜色）
        this.ctx.fillStyle = d.color;
        this.ctx.fillText(d.text, d.x, d.y);
        
        this.ctx.restore();
    }
    
    /**
     * 整数颜色转CSS颜色
     */
    intToColor(color) {
        const hex = color.toString(16).padStart(6, '0');
        return `#${hex}`;
    }
    
    /**
     * 设置配置
     */
    setConfig(key, value) {
        this.config[key] = value;
        
        if (key === 'areaRatio') {
            this.calculateTracks();
        }
        
        if (key === 'enabled' && !value) {
            this.ctx.clearRect(0, 0, this.width, this.height);
        }
    }
    
    /**
     * 切换弹幕显示
     */
    toggle() {
        this.config.enabled = !this.config.enabled;
        
        if (!this.config.enabled) {
            this.ctx.clearRect(0, 0, this.width, this.height);
        }
        
        return this.config.enabled;
    }
}

// 导出
window.DanmakuEngine = DanmakuEngine;

