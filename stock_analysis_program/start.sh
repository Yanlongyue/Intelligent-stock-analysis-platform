#!/bin/bash

# ============================================================
# 七步法股票分析程序 - 启动脚本
# 版本：v1.0.0
# 作者：风暴 🌪️
# 核心原则：数据是分析的基石，数据错了，分析再多都是错的
# ============================================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函数：打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 函数：显示帮助信息
show_help() {
    echo -e "${GREEN}七步法股票分析程序 - 启动脚本${NC}"
    echo "================================"
    echo "用法: ./start.sh [命令]"
    echo ""
    echo "可用命令:"
    echo "  help          显示帮助信息"
    echo "  summary       显示程序配置摘要"
    echo "  test          运行测试模式"
    echo "  analyze       运行完整分析"
    echo "  analyze-date  运行指定日期的分析"
    echo "  check         检查依赖和环境"
    echo "  install       安装依赖包"
    echo "  clean         清理临时文件"
    echo ""
    echo "示例:"
    echo "  ./start.sh summary     # 显示配置"
    echo "  ./start.sh test        # 运行测试"
    echo "  ./start.sh analyze     # 执行分析"
    echo ""
}

# 函数：检查Python环境
check_python() {
    print_info "检查Python环境..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d ' ' -f2)
        print_success "Python3 已安装: $PYTHON_VERSION"
    else
        print_error "Python3 未安装，请先安装Python3"
        exit 1
    fi
}

# 函数：检查依赖包
check_dependencies() {
    print_info "检查Python依赖包..."
    
    # 检查requirements.txt是否存在
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt 文件不存在"
        exit 1
    fi
    
    # 检查主要依赖包
    for package in "tushare" "pandas" "jinja2" "numpy"; do
        if python3 -c "import $package" 2>/dev/null; then
            print_success "$package 已安装"
        else
            print_warning "$package 未安装"
            return 1
        fi
    done
    
    print_success "所有主要依赖包检查通过"
    return 0
}

# 函数：检查Tushare Token配置
check_token() {
    print_info "检查Tushare Token配置..."
    
    if [ ! -f "config/tushare_config.py" ]; then
        print_warning "Tushare配置文件不存在"
        echo "请创建 config/tushare_config.py 并配置您的Token"
        echo ""
        echo "示例内容："
        echo "TOKEN = \"您的Tushare Pro Token\""
        echo ""
        return 1
    fi
    
    # 检查Token是否已配置
    if grep -q "your_tushare_token_here" config/tushare_config.py; then
        print_warning "Tushare Token 未配置"
        echo "请编辑 config/tushare_config.py 文件，将 your_tushare_token_here 替换为您的实际Token"
        return 1
    fi
    
    print_success "Tushare Token 配置检查通过"
    return 0
}

# 函数：安装依赖
install_dependencies() {
    print_info "开始安装依赖包..."
    
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt 文件不存在"
        exit 1
    fi
    
    pip install -r requirements.txt
    
    if [ $? -eq 0 ]; then
        print_success "依赖包安装完成"
    else
        print_error "依赖包安装失败"
        exit 1
    fi
}

# 函数：清理临时文件
clean_temp_files() {
    print_info "清理临时文件..."
    
    # 清理Python缓存文件
    find . -name "*.pyc" -delete
    find . -name "__pycache__" -type d -exec rm -rf {} +
    
    # 清理日志文件（保留最近7天的）
    if [ -d "logs" ]; then
        find logs -name "*.log" -mtime +7 -delete
    fi
    
    print_success "临时文件清理完成"
}

# 主程序逻辑
main() {
    # 确保在正确的目录
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
    cd "$SCRIPT_DIR"
    
    # 检查命令
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi
    
    COMMAND=$1
    
    case $COMMAND in
        "help")
            show_help
            ;;
            
        "summary")
            print_info "显示程序配置摘要..."
            python3 src/main.py --summary
            ;;
            
        "test")
            print_info "运行测试模式..."
            check_python
            check_dependencies
            check_token
            python3 src/main.py --test
            ;;
            
        "analyze")
            print_info "运行完整七步法分析..."
            check_python
            check_dependencies
            check_token
            python3 src/main.py
            ;;
            
        "analyze-date")
            if [ -z "$2" ]; then
                print_error "请指定分析日期（格式：YYYY-MM-DD）"
                echo "示例: ./start.sh analyze-date 2026-04-02"
                exit 1
            fi
            
            DATE=$2
            print_info "运行指定日期的分析：$DATE"
            check_python
            check_dependencies
            check_token
            python3 src/main.py --date "$DATE"
            ;;
            
        "check")
            print_info "检查环境和依赖..."
            check_python
            check_dependencies
            check_token
            
            if [ $? -eq 0 ]; then
                print_success "✅ 所有检查通过，程序可以正常运行！"
            else
                print_warning "⚠️  部分检查未通过，可能需要修复"
            fi
            ;;
            
        "install")
            install_dependencies
            ;;
            
        "clean")
            clean_temp_files
            ;;
            
        *)
            print_error "未知命令: $COMMAND"
            show_help
            exit 1
            ;;
    esac
}

# 执行主程序
main "$@"