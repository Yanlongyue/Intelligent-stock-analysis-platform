// 智能股票分析系统 - 统一运行时配置
window.APP_CONFIG = {
    version: '2026.04.08-2',
    api: {
        // 本地开发环境 API 地址
        development: 'http://localhost:9000',
        // 生产环境 API 地址
        // 推荐值：'same-origin'，表示前端与后端部署在同一域名下，自动使用当前站点 origin
        // Nginx 统一入口部署时必须使用 same-origin（通过 /api/ 反向代理到后端 9000）
        production: 'same-origin',
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
    const isHttpsPage = window.location.protocol === 'https:';

    const normalize = (value) => (value || '').trim().replace(/\/+$/, '');
    const isInsecureApi = (value) => /^http:\/\//i.test(normalize(value));
    const isSameOriginMode = (value) => ['same-origin', 'sameorigin', 'origin'].includes(normalize(value).toLowerCase());
    const resolveSameOrigin = () => normalize(window.location.origin || '');

    if (queryApi) {
        if (isSameOriginMode(queryApi)) {
            return resolveSameOrigin();
        }
        return isHttpsPage && isInsecureApi(queryApi) ? '' : normalize(queryApi);
    }

    if (isLocalHost) {
        return normalize(config.development);
    }

    if (isSameOriginMode(config.production)) {
        return resolveSameOrigin();
    }

    const productionApi = normalize(config.production);
    if (isHttpsPage && isInsecureApi(productionApi)) {
        return '';
    }

    return productionApi;
};

/**
 * 获取当前 API 配置状态详情
 */
window.getApiConfigStatus = function getApiConfigStatus() {
    const hostname = window.location.hostname;
    const isLocalHost = hostname === 'localhost' || hostname === '127.0.0.1';
    const isHttpsPage = window.location.protocol === 'https:';
    const config = (window.APP_CONFIG && window.APP_CONFIG.api) || {};
    const normalize = (value) => (value || '').trim().replace(/\/+$/, '');
    const isSameOriginMode = (value) => ['same-origin', 'sameorigin', 'origin'].includes(normalize(value).toLowerCase());
    const requestedApi = config.allowQueryOverride === false
        ? normalize(isLocalHost ? config.development : config.production)
        : normalize((new URLSearchParams(window.location.search).get('api')) || (isLocalHost ? config.development : config.production));
    const mixedContentBlocked = Boolean(!isLocalHost && isHttpsPage && requestedApi && !isSameOriginMode(requestedApi) && /^http:\/\//i.test(requestedApi));
    const apiBaseUrl = window.resolveApiBaseUrl();

    return {
        apiBaseUrl,
        requestedApi,
        requestedMode: isSameOriginMode(requestedApi) ? 'same-origin' : 'custom',
        isConfigured: Boolean(apiBaseUrl),
        mode: isLocalHost ? 'development' : 'production',
        version: window.APP_CONFIG && window.APP_CONFIG.version,
        hasProductionConfig: Boolean(config.production),
        canUseQueryOverride: config.allowQueryOverride !== false,
        currentUrl: location.href,
        blockedReason: mixedContentBlocked ? 'mixed-content' : '',
        blockedApiBaseUrl: mixedContentBlocked ? requestedApi : '',
        tunnelHints: config.tunnel || {}
    };
};
