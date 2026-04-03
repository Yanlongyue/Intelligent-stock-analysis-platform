// 智能股票分析系统 - 统一运行时配置
window.APP_CONFIG = {
    version: '2026.04.03-1',
    api: {
        development: 'http://localhost:9000',
        // 生产环境请填写真实可访问的后端 API 地址，例如：https://your-api.example.com
        production: '',
        allowQueryOverride: true
    }
};

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

window.getApiConfigStatus = function getApiConfigStatus() {
    const hostname = window.location.hostname;
    const isLocalHost = hostname === 'localhost' || hostname === '127.0.0.1';
    const apiBaseUrl = window.resolveApiBaseUrl();

    return {
        apiBaseUrl,
        isConfigured: Boolean(apiBaseUrl),
        mode: isLocalHost ? 'development' : 'production',
        version: window.APP_CONFIG && window.APP_CONFIG.version
    };
};