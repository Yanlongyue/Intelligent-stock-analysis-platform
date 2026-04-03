#!/bin/bash

# 🚀 一键部署到Gitee Pages + 后端API脚本
# 版本: v1.0
# 作者: 风暴
# 日期: 2026-04-03

echo "🎯 ========================================="
echo "🎯  智能股票分析系统 - Gitee Pages部署工具"
echo "🎯 ========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查Git
check_git() {
    if ! command -v git &> /dev/null; then
        echo -e "${RED}❌ Git未安装，请先安装Git${NC}"
        echo "安装命令: brew install git"
        exit 1
    fi
    echo -e "${GREEN}✅ Git已安装${NC}"
}

# 检查Python
check_python() {
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python3未安装${NC}"
        echo "安装命令: brew install python@3.10"
        exit 1
    fi
    echo -e "${GREEN}✅ Python3已安装${NC}"
}

# 显示菜单
show_menu() {
    echo ""
    echo -e "${BLUE}📋 请选择部署方案：${NC}"
    echo "1. 🚀 快速部署（使用ngrok临时后端）"
    echo "2. 🏢 完整部署（配置云服务器后端）"
    echo "3. 📚 查看部署文档"
    echo "4. 🧪 测试本地环境"
    echo "5. 🚪 退出"
    echo ""
    read -p "请输入选项 [1-5]: " choice
}

# 快速部署方案
quick_deploy() {
    echo ""
    echo -e "${YELLOW}🚀 开始快速部署...${NC}"
    
    # 检查ngrok
    if ! command -v ngrok &> /dev/null; then
        echo -e "${YELLOW}⚠️  ngrok未安装，正在安装...${NC}"
        brew install ngrok/ngrok/ngrok || {
            echo -e "${RED}❌ ngrok安装失败${NC}"
            echo "请手动安装: brew install ngrok/ngrok/ngrok"
            echo "或访问: https://ngrok.com/download"
            return 1
        }
    fi
    
    echo -e "${GREEN}✅ 环境检查完成${NC}"
    
    # 询问Gitee用户名
    read -p "请输入您的Gitee用户名: " gitee_username
    
    if [ -z "$gitee_username" ]; then
        echo -e "${RED}❌ 用户名不能为空${NC}"
        return 1
    fi
    
    # 启动后端服务
    echo "启动真实数据后端API服务..."
    if [ -z "$TUSHARE_TOKEN" ]; then
        echo -e "${YELLOW}⚠️  未检测到 TUSHARE_TOKEN，后端会以模拟数据模式启动${NC}"
    fi
    python3 real_data_backend.py &
    BACKEND_PID=$!
    echo -e "${GREEN}✅ 后端服务已启动 (PID: $BACKEND_PID)${NC}"
    
    # 启动ngrok
    echo "启动ngrok内网穿透..."
    ngrok http 9000 > ngrok.log 2>&1 &
    NGROK_PID=$!
    sleep 5  # 等待ngrok启动
    
    # 获取ngrok地址
    NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o 'https://[^"]*\.ngrok-free\.app')
    
    if [ -z "$NGROK_URL" ]; then
        echo -e "${RED}❌ 获取ngrok地址失败${NC}"
        echo "请检查ngrok日志: tail -f ngrok.log"
        kill $BACKEND_PID $NGROK_PID 2>/dev/null
        return 1
    fi
    
    echo -e "${GREEN}✅ ngrok地址: $NGROK_URL${NC}"

    # 创建配置文件
    echo "正在创建配置文件..."
    cat > config.js << EOF
// 智能股票分析系统 - 统一运行时配置
window.APP_CONFIG = {
    version: '2026.04.03-1',
    api: {
        development: 'http://localhost:9000',
        production: '$NGROK_URL',
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

    if (queryApi) return normalize(queryApi);
    if (isLocalHost) return normalize(config.development);
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
EOF
    
    # 添加远程仓库
    echo "配置Gitee远程仓库..."
    git remote remove gitee 2>/dev/null
    git remote add gitee "https://gitee.com/$gitee_username/stock-analysis-program.git"
    
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}⚠️  远程仓库配置失败，请手动添加${NC}"
        echo "命令: git remote add gitee https://gitee.com/$gitee_username/stock-analysis-program.git"
    else
        echo -e "${GREEN}✅ 远程仓库配置成功${NC}"
    fi

    CURRENT_BRANCH="$(git branch --show-current 2>/dev/null)"
    if [ -z "$CURRENT_BRANCH" ]; then
        CURRENT_BRANCH="master"
    fi
    
    # 推送代码
    echo "推送代码到Gitee..."
    git add .
    if git diff --cached --quiet; then
        echo -e "${YELLOW}ℹ️  当前没有新的文件改动，直接推送现有分支${NC}"
    else
        git commit -m "部署到Gitee Pages - $(date '+%Y-%m-%d %H:%M:%S')" || {
            echo -e "${RED}❌ 自动提交失败，请先处理 Git 状态后重试${NC}"
            kill $BACKEND_PID $NGROK_PID 2>/dev/null
            return 1
        }
    fi
    git push -u gitee "$CURRENT_BRANCH"
    
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}⚠️  代码推送失败，请检查Gitee仓库是否存在${NC}"
        echo "请先访问 https://gitee.com 创建仓库: stock-analysis-program"
    else
        echo -e "${GREEN}✅ 代码推送成功${NC}"
    fi
    
    # 显示访问信息
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}🎉 部署完成！${NC}"
    echo ""
    echo "🔗 访问地址:"
    echo "  主页: https://$gitee_username.gitee.io/stock-analysis-program/"
    echo "  增强版页面: https://$gitee_username.gitee.io/stock-analysis-program/web_interface_enhanced.html"
    echo "  真实数据页面: https://$gitee_username.gitee.io/stock-analysis-program/real_data_frontend.html"
    echo "  后端API: $NGROK_URL"
    echo ""
    echo "📱 手机访问:"
    echo "  浏览器打开上述地址即可"
    echo ""
    echo "🔧 管理命令:"
    echo "  停止后端: kill $BACKEND_PID"
    echo "  停止ngrok: kill $NGROK_PID"
    echo "  查看日志: tail -f ngrok.log"
    echo -e "${BLUE}========================================${NC}"
    
    # 保存进程ID
    echo "$BACKEND_PID" > backend.pid
    echo "$NGROK_PID" > ngrok.pid
}

# 完整部署方案
full_deploy() {
    echo ""
    echo -e "${YELLOW}🏢 开始完整部署...${NC}"
    echo ""
    echo "完整部署需要以下步骤："
    echo "1. 购买云服务器（腾讯云/阿里云）"
    echo "2. 部署后端API服务"
    echo "3. 配置域名和SSL证书"
    echo "4. 部署前端到Gitee Pages"
    echo ""
    echo "请参考部署文档: Gitee部署方案B_前后端分离.md"
    echo ""
    read -p "按Enter键查看详细步骤..." key
    
    # 显示详细步骤
    echo ""
    echo -e "${BLUE}📋 详细步骤：${NC}"
    echo "1. 购买服务器："
    echo "   - 腾讯云轻量服务器：1核2G 约50元/月"
    echo "   - 系统选择：Ubuntu 22.04"
    echo ""
    echo "2. 服务器部署："
    echo "   - SSH登录服务器"
    echo "   - 安装Python3和pip"
    echo "   - 克隆项目代码"
    echo "   - 安装依赖：pip install flask flask-cors"
    echo "   - 通过环境变量配置 TUSHARE_TOKEN"
    echo "   - 启动服务：nohup python3 real_data_backend.py &"
    echo ""
    echo "3. 域名配置："
    echo "   - 购买域名（可选）"
    echo "   - 配置DNS解析到服务器IP"
    echo "   - 申请SSL证书（Let's Encrypt）"
    echo ""
    echo "4. 前端部署："
    echo "   - 修改前端API地址为服务器地址"
    echo "   - 推送代码到Gitee"
    echo "   - 开启Gitee Pages"
    echo ""
    echo "需要进一步帮助吗？(y/n)"
    read -p "> " need_help
    
    if [[ $need_help == "y" || $need_help == "Y" ]]; then
        echo ""
        echo "我可以为您："
        echo "1. 生成服务器部署脚本"
        echo "2. 创建Docker镜像"
        echo "3. 生成Nginx配置"
        echo "4. 创建监控脚本"
        echo ""
        read -p "请选择 [1-4]: " help_option
        
        case $help_option in
            1)
                generate_server_script
                ;;
            2)
                generate_dockerfile
                ;;
            3)
                generate_nginx_config
                ;;
            4)
                generate_monitor_script
                ;;
            *)
                echo -e "${YELLOW}⚠️  返回主菜单${NC}"
                ;;
        esac
    fi
}

# 生成服务器部署脚本
generate_server_script() {
    cat > deploy_to_server.sh << 'EOF'
#!/bin/bash
# 服务器部署脚本

# 更新系统
sudo apt update
sudo apt upgrade -y

# 安装Python和相关工具
sudo apt install -y python3 python3-pip python3-venv git nginx

# 创建项目目录
mkdir -p ~/stock-analysis
cd ~/stock-analysis

# 克隆代码（需要先在Gitee创建仓库）
git clone https://gitee.com/YOUR_USERNAME/stock-analysis-program.git
cd stock-analysis-program

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置Tushare Token
export TUSHARE_TOKEN='your_token_here'
# 生产环境请改为在服务进程或部署平台中安全注入环境变量，避免写入代码文件

# 创建启动脚本
cat > start_server.sh << 'SCRIPT'
#!/bin/bash
source ~/stock-analysis/stock-analysis-program/venv/bin/activate
cd ~/stock-analysis/stock-analysis-program
python3 real_data_backend.py
SCRIPT

chmod +x start_server.sh

# 配置systemd服务
sudo tee /etc/systemd/system/stock-api.service << 'SERVICE'
[Unit]
Description=Stock Analysis API Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER/stock-analysis/stock-analysis-program
ExecStart=/home/$USER/stock-analysis/stock-analysis-program/start_server.sh
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE

sudo systemctl daemon-reload
sudo systemctl enable stock-api
sudo systemctl start stock-api

echo "✅ 部署完成！"
echo "服务状态: sudo systemctl status stock-api"
EOF

    chmod +x deploy_to_server.sh
    echo -e "${GREEN}✅ 服务器部署脚本已生成: deploy_to_server.sh${NC}"
}

# 生成Dockerfile
generate_dockerfile() {
    cat > Dockerfile << 'EOF'
FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建非root用户
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# 暴露端口
EXPOSE 9000

# 启动命令
CMD ["python", "real_data_backend.py"]
EOF

    cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  stock-api:
    build: .
    ports:
      - "9000:9000"
    environment:
      - TUSHARE_TOKEN=${TUSHARE_TOKEN}
      - FLASK_ENV=production
    restart: unless-stopped
    volumes:
      - ./data:/app/data
EOF

    echo -e "${GREEN}✅ Docker配置已生成${NC}"
    echo "   - Dockerfile"
    echo "   - docker-compose.yml"
}

# 测试本地环境
test_local() {
    echo ""
    echo -e "${YELLOW}🧪 开始测试本地环境...${NC}"
    
    # 测试Python后端
    echo "测试Python后端..."
    python3 -c "import json; print('✅ Python导入测试通过')"
    
    # 测试算法配置
    echo "测试算法配置..."
    if [ -f "algorithm_config.py" ]; then
        python3 -c "import algorithm_config; print('✅ 算法配置导入成功')"
    else
        echo -e "${RED}❌ algorithm_config.py 不存在${NC}"
    fi
    
    # 测试Web界面
    echo "测试Web界面..."
    if [ -f "web_interface_enhanced.html" ]; then
        echo -e "${GREEN}✅ Web界面文件存在${NC}"
        echo "文件大小: $(wc -l < web_interface_enhanced.html) 行"
    else
        echo -e "${RED}❌ web_interface_enhanced.html 不存在${NC}"
    fi
    
    # 启动测试服务
    echo ""
    echo -e "${YELLOW}🚀 启动测试服务...${NC}"
    echo "后端服务将在端口 9000 启动"
    echo "按 Ctrl+C 停止测试"
    
    python3 algorithm_backend.py &
    TEST_PID=$!
    
    sleep 3
    
    # 测试API
    echo "测试API连接..."
    curl -s http://localhost:9000/api/health | grep -q "healthy"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ API服务运行正常${NC}"
    else
        echo -e "${RED}❌ API服务测试失败${NC}"
    fi
    
    # 显示测试结果
    echo ""
    echo -e "${BLUE}📊 测试结果：${NC}"
    echo "API地址: http://localhost:9000"
    echo "Web界面: file://$(pwd)/web_interface_enhanced.html"
    echo ""
    echo "🎯 测试完成！"
    echo "按 Enter 键停止测试服务..."
    read
    
    kill $TEST_PID 2>/dev/null
    echo -e "${GREEN}✅ 测试服务已停止${NC}"
}

# 主程序
main() {
    # 检查环境
    echo -e "${BLUE}🔧 环境检查...${NC}"
    check_git
    check_python
    
    while true; do
        show_menu
        
        case $choice in
            1)
                quick_deploy
                ;;
            2)
                full_deploy
                ;;
            3)
                echo ""
                echo -e "${BLUE}📚 部署文档：${NC}"
                echo "1. Gitee部署方案B_前后端分离.md - 完整部署方案"
                echo "2. README.md - 项目说明"
                echo "3. 外网访问完整指南.md - 网络配置"
                echo ""
                read -p "打开哪个文档？ [1-3] (直接Enter查看全部): " doc_choice
                
                case $doc_choice in
                    1)
                        open Gitee部署方案B_前后端分离.md 2>/dev/null || \
                        echo "请使用文本编辑器打开: Gitee部署方案B_前后端分离.md"
                        ;;
                    2)
                        open README.md 2>/dev/null || \
                        echo "请使用文本编辑器打开: README.md"
                        ;;
                    3)
                        open 外网访问完整指南.md 2>/dev/null || \
                        echo "请使用文本编辑器打开: 外网访问完整指南.md"
                        ;;
                    *)
                        echo "文档列表："
                        ls -la *.md | awk '{print NR ". " $9}'
                        ;;
                esac
                ;;
            4)
                test_local
                ;;
            5)
                echo ""
                echo -e "${GREEN}👋 再见！${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}❌ 无效选项，请重新选择${NC}"
                ;;
        esac
    done
}

# 清理函数
cleanup() {
    echo ""
    echo -e "${YELLOW}🧹 清理临时文件...${NC}"
    
    if [ -f "backend.pid" ]; then
        BACKEND_PID=$(cat backend.pid)
        kill $BACKEND_PID 2>/dev/null
        rm -f backend.pid
    fi
    
    if [ -f "ngrok.pid" ]; then
        NGROK_PID=$(cat ngrok.pid)
        kill $NGROK_PID 2>/dev/null
        rm -f ngrok.pid
    fi
    
    rm -f ngrok.log 2>/dev/null
    echo -e "${GREEN}✅ 清理完成${NC}"
}

# 设置退出时清理
trap cleanup EXIT

# 运行主程序
main