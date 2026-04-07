// 智能股票分析系统 - 统一运行时配置
window.APP_CONFIG = {
    version: '2026.04.07-2',
    api: {
        // 本地开发环境 API 地址
        development: 'http://localhost:9000',
        // 生产环境（公网/GitHub Pages）API 地址
        // 填写方式（三选一）：
        //   1) 直接填写：production: 'https://xxxx.ngrok-free.app'
        //   2) Cloudflare Tunnel：production: 'https://你的域名.trycloudflare.com'
        //   3) 留空：通过 URL 参数 ?api=https://xxx 临时指定
        production: 'https://firm-event-rating-five.trycloudflare.com',
        // 是否允许通过 URL 参数 ?api=xxx 覆盖配置
        allowQueryOverride: true,
        // 公网穿透工具配置说明
        tunnel: {
            ngrok: {
                name: 'ngrok',
                cmd: 'ngrok http 9000',
                setupUrl: 'https://dashboard.ngrok.com/get-started/your-authtoken',
                note: '需要先注册并配置 authtoken'
            },
            cloudflare: {
                name: 'Cloudflare Tunnel',
                cmd: 'cloudflared tunnel --url http://localhost:9000',
                setupUrl: 'https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/',
                note: '免费、无需注册即可使用临时域名'
            },
            localtunnel: {
                name: 'localtunnel (npx)',
                cmd: 'npx localtunnel --port 9000',
                setupUrl: null,
                note: '无需安装，直接运行 npx 即可'
            }
        }
    }
};

/**
 * 解析当前环境的 API 基础地址
 * 优先级：URL参数 > 环境判断(development/production)
 */
window.resolveApiBaseUrl = function resolveApiBaseUrl() {
    const config = (window.APP_CONFIG && window.APP_CONFIG.api) || {};
    const params = new URLSearchParams(window.location.search);
    const queryApi = config.allowQueryOverride === false ? '' : (params.get('api') || '').trim();
    const hostname = window.location.hostname;
    const isLocalHost = hostname === 'localhost' || hostname === '127.0.0.1';

    const normalize = (value) => (value || '').trim().replace(/\/+$/, '');

    if (queryApi) {
        return normalize(queryApi);
    }

    if (isLocalHost) {
        return normalize(config.development);
    }

    return normalize(config.production);
};

/**
 * 获取当前 API 配置状态详情
 */
window.getApiConfigStatus = function getApiConfigStatus() {
    const hostname = window.location.hostname;
    const isLocalHost = hostname === 'localhost' || hostname === '127.0.0.1';
    const apiBaseUrl = window.resolveApiBaseUrl();
    const config = (window.APP_CONFIG && window.APP_CONFIG.api) || {};

    return {
        apiBaseUrl,
        isConfigured: Boolean(apiBaseUrl),
        mode: isLocalHost ? 'development' : 'production',
        version: window.APP_CONFIG && window.APP_CONFIG.version,
        hasProductionConfig: Boolean(config.production),
        canUseQueryOverride: config.allowQueryOverride !== false,
        currentUrl: location.href,
        tunnelHints: config.tunnel || {}
    };
};