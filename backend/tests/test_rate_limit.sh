#!/bin/bash

# API限流和防刷策略自动化测试脚本
# 使用方法: ./test_rate_limit.sh [base_url] [test_user] [test_password]

BASE_URL="${1:-http://localhost:8000}"
TEST_USERS=("testuser001" "testuser002" "testuser003")
TEST_PASSWORDS=("testuser001" "testuser002" "testuser003")
CURRENT_USER_INDEX=0
AUTH_TOKEN=""
REFRESH_TOKEN=""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 测试结果统计
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# 临时文件
RESPONSE_FILE="/tmp/test_response_$$"
HEADERS_FILE="/tmp/test_headers_$$"

# 清理函数
cleanup() {
    rm -f "$RESPONSE_FILE" "$HEADERS_FILE"
}
trap cleanup EXIT

# 获取下一个测试用户
get_next_user() {
    local user="${TEST_USERS[$CURRENT_USER_INDEX]}"
    local password="${TEST_PASSWORDS[$CURRENT_USER_INDEX]}"
    CURRENT_USER_INDEX=$(((CURRENT_USER_INDEX + 1) % ${#TEST_USERS[@]}))
    echo "$user:$password"
}

# 用户登录获取token
login_user() {
    local user_pass="$1"
    local username="${user_pass%:*}"
    local password="${user_pass#*:}"

    make_request "POST" "$BASE_URL/auth/login" "Content-Type: application/json" \
        '{"username":"'$username'","password":"'$password'"}'

    local status_code=$(grep "HTTP" "$HEADERS_FILE" | cut -d' ' -f2)
    local response_body=$(cat "$RESPONSE_FILE")

    if [[ "$status_code" == "200" ]]; then
        # 提取token (假设响应格式包含access_token)
        AUTH_TOKEN=$(echo "$response_body" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
        REFRESH_TOKEN=$(echo "$response_body" | grep -o '"refresh_token":"[^"]*"' | cut -d'"' -f4)
        return 0
    else
        AUTH_TOKEN=""
        REFRESH_TOKEN=""
        return 1
    fi
}

# 获取认证头
get_auth_header() {
    if [[ -n "$AUTH_TOKEN" ]]; then
        echo "Authorization: Bearer $AUTH_TOKEN"
    else
        echo ""
    fi
}

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  API限流和防刷策略自动化测试${NC}"
    echo -e "${BLUE}  测试地址: $BASE_URL${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

print_test_start() {
    echo -e "${YELLOW}[TEST] $1${NC}"
    ((TOTAL_TESTS++))
}

print_pass() {
    echo -e "${GREEN}  ✓ PASS: $1${NC}"
    ((PASSED_TESTS++))
}

print_fail() {
    echo -e "${RED}  ✗ FAIL: $1${NC}"
    echo -e "${RED}     预期: $2${NC}"
    echo -e "${RED}     实际: $3${NC}"
    ((FAILED_TESTS++))
}

print_info() {
    echo -e "${BLUE}  ℹ INFO: $1${NC}"
}

# 获取响应头和响应体
make_request() {
    local method="$1"
    local url="$2"
    local headers="$3"
    local data="$4"

    if [ -n "$data" ]; then
        curl -s -X "$method" "$url" -H "$headers" -d "$data" -D "$HEADERS_FILE" -o "$RESPONSE_FILE"
    else
        curl -s -X "$method" "$url" -H "$headers" -D "$HEADERS_FILE" -o "$RESPONSE_FILE"
    fi

    return $?
}

# 检查响应头
check_header() {
    local header_name="$1"
    local expected_value="$2"
    local actual_value=$(grep -i "^$header_name:" "$HEADERS_FILE" | cut -d' ' -f2 | tr -d '\r')

    if [[ "$actual_value" == "$expected_value" ]]; then
        print_pass "响应头 $header_name: $actual_value"
        return 0
    else
        print_fail "响应头 $header_name" "$expected_value" "$actual_value"
        return 1
    fi
}

# 检查响应状态码
check_status_code() {
    local expected_code="$1"
    local actual_code=$(grep "HTTP" "$HEADERS_FILE" | cut -d' ' -f2)

    if [[ "$actual_code" == "$expected_code" ]]; then
        print_pass "HTTP状态码: $actual_code"
        return 0
    else
        print_fail "HTTP状态码" "$expected_code" "$actual_code"
        return 1
    fi
}

# 测试1: 基础限流头信息测试
test_basic_rate_limit_headers() {
    print_test_start "基础限流头信息测试"

    make_request "GET" "$BASE_URL/auth/login" "Content-Type: application/json"

    local rate_limit=$(grep -i "^X-RateLimit-Limit:" "$HEADERS_FILE" | cut -d' ' -f2 | tr -d '\r')
    local rate_remaining=$(grep -i "^X-RateLimit-Remaining:" "$HEADERS_FILE" | cut -d' ' -f2 | tr -d '\r')

    if [[ -n "$rate_limit" && "$rate_limit" -eq 10 ]]; then
        print_pass "X-RateLimit-Limit 头存在且值为10"
    else
        print_fail "X-RateLimit-Limit 头" "10" "$rate_limit"
    fi

    if [[ -n "$rate_remaining" && "$rate_remaining" -le 10 ]]; then
        print_pass "X-RateLimit-Remaining 头存在且值有效: $rate_remaining"
    else
        print_fail "X-RateLimit-Remaining 头" "≤10" "$rate_remaining"
    fi

    echo ""
}

# 测试2: 登录接口限流测试
test_login_rate_limit() {
    print_test_start "登录接口限流测试 (10次/分钟)"

    local triggered_limit=false
    local normal_count=0

    for i in {1..12}; do
        make_request "POST" "$BASE_URL/auth/login" "Content-Type: application/json" \
            '{"username":"'$TEST_USER'","password":"'$TEST_PASSWORD'"}'

        local status_code=$(grep "HTTP" "$HEADERS_FILE" | cut -d' ' -f2)
        local remaining=$(grep -i "^X-RateLimit-Remaining:" "$HEADERS_FILE" | cut -d' ' -f2 | tr -d '\r')

        if [[ "$status_code" == "429" ]]; then
            triggered_limit=true
            print_info "在第 $i 次请求触发限流 (429)"
            break
        elif [[ "$i" -le 10 ]]; then
            ((normal_count++))
        fi

        sleep 0.1
    done

    if [[ "$triggered_limit" == true && "$normal_count" -ge 9 ]]; then
        print_pass "登录接口限流正常工作"
    else
        print_fail "登录接口限流" "10次后触发429" "正常请求:$normal_count, 触发限流:$triggered_limit"
    fi

    echo ""
}

# 测试3: User-Agent检测测试
test_user_agent_detection() {
    print_test_start "User-Agent检测测试"

    # 测试可疑User-Agent
    make_request "GET" "$BASE_URL/auth/login" "User-Agent: python-requests/2.28.1"

    local bot_score=$(grep -i "^X-Bot-Score:" "$HEADERS_FILE" | cut -d' ' -f2 | tr -d '\r')
    local bot_suspicious=$(grep -i "^X-Bot-Suspicious:" "$HEADERS_FILE" | cut -d' ' -f2 | tr -d '\r')

    if [[ -n "$bot_score" ]]; then
        print_pass "检测到X-Bot-Score头: $bot_score"
    else
        print_fail "X-Bot-Score头" "存在" "缺失"
    fi

    # 测试正常User-Agent
    make_request "GET" "$BASE_URL/auth/login" "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

    local normal_bot_score=$(grep -i "^X-Bot-Score:" "$HEADERS_FILE" | cut -d' ' -f2 | tr -d '\r')

    if [[ -n "$normal_bot_score" && "$normal_bot_score" -lt "$bot_score" ]]; then
        print_pass "正常User-Agent得分更低: $normal_bot_score < $bot_score"
    else
        print_info "正常User-Agent得分: ${normal_bot_score:-缺失}"
    fi

    echo ""
}

# 测试4: 蜜罐路径检测
test_honeypot_detection() {
    print_test_start "蜜罐路径检测测试"

    local honeypot_paths=("/admin.php" "/.env" "/.git" "/phpmyadmin" "/_debug")
    local detected_count=0

    for path in "${honeypot_paths[@]}"; do
        make_request "GET" "$BASE_URL$path" "User-Agent: python-requests/2.28.1"

        local bot_detected=$(grep -i "^X-Bot-Detected:" "$HEADERS_FILE" | cut -d' ' -f2 | tr -d '\r')
        local status_code=$(grep "HTTP" "$HEADERS_FILE" | cut -d' ' -f2)

        if [[ "$bot_detected" == "true" ]]; then
            ((detected_count++))
            print_pass "蜜罐路径 $path 触发检测 (状态码: $status_code)"
        else
            print_info "路径 $path 未触发检测 (状态码: $status_code)"
        fi
    done

    if [[ "$detected_count" -gt 0 ]]; then
        print_pass "蜜罐检测正常工作，触发了 $detected_count 个路径"
    else
        print_fail "蜜罐检测" "至少触发1个路径" "未触发任何路径"
    fi

    echo ""
}

# 测试5: 快速请求检测
test_rapid_request_detection() {
    print_test_start "快速请求检测 (行为模式)"

    local rapid_requests=10
    local suspicious_count=0

    for i in $(seq 1 $rapid_requests); do
        make_request "GET" "$BASE_URL/auth/login" "User-Agent: python-requests/2.28.1"

        local bot_score=$(grep -i "^X-Bot-Score:" "$HEADERS_FILE" | cut -d' ' -f2 | tr -d '\r')

        if [[ -n "$bot_score" && "$bot_score" -gt 5 ]]; then
            ((suspicious_count++))
        fi
    done

    if [[ "$suspicious_count" -gt 5 ]]; then
        print_pass "快速请求检测正常，$suspicious_count/$rapid_requests 请求得分较高"
    else
        print_info "快速请求检测: $suspicious_count/$rapid_requests 请求得分较高"
    fi

    echo ""
}

# 测试6: 限流统计API
test_rate_limit_stats() {
    print_test_start "限流统计API测试"

    make_request "GET" "$BASE_URL/rate-limit/stats?scope=ip&identifier=127.0.0.1" "Content-Type: application/json"

    local response_body=$(cat "$RESPONSE_FILE")
    local status_code=$(grep "HTTP" "$HEADERS_FILE" | cut -d' ' -f2)

    if [[ "$status_code" == "200" ]]; then
        if [[ "$response_body" == *"\"scope\":\"ip\""* && "$response_body" == *"\"identifier\":\"127.0.0.1\""* ]]; then
            print_pass "限流统计API返回正确数据"
        else
            print_fail "限流统计API数据" "包含正确的scope和identifier" "数据格式异常"
        fi
    else
        print_fail "限流统计API" "200" "$status_code"
    fi

    echo ""
}

# 测试7: 配置查询API
test_rate_limit_config() {
    print_test_start "限流配置API测试"

    make_request "GET" "$BASE_URL/rate-limit/config" "Content-Type: application/json"

    local response_body=$(cat "$RESPONSE_FILE")
    local status_code=$(grep "HTTP" "$HEADERS_FILE" | cut -d' ' -f2)

    if [[ "$status_code" == "200" ]]; then
        if [[ "$response_body" == *"\"algorithm\""* && "$response_body" == *"\"limit\""* ]]; then
            print_pass "限流配置API返回正确配置信息"
        else
            print_fail "限流配置API数据" "包含algorithm和limit配置" "数据格式异常"
        fi
    else
        print_fail "限流配置API" "200" "$status_code"
    fi

    echo ""
}

# 测试8: 综合攻击模拟
test_combined_attack_simulation() {
    print_test_start "综合攻击模拟测试"

    local attack_count=5
    local blocked_count=0

    for i in $(seq 1 $attack_count); do
        # 模拟攻击特征：可疑UA + 快速请求 + 错误凭证
        make_request "POST" "$BASE_URL/auth/login" "User-Agent: python-requests/2.28.1" \
            '{"username":"admin","password":"wrongpassword"}'

        local status_code=$(grep "HTTP" "$HEADERS_FILE" | cut -d' ' -f2)

        if [[ "$status_code" == "429" || "$status_code" == "403" ]]; then
            ((blocked_count++))
        fi

        sleep 0.2
    done

    if [[ "$blocked_count" -gt 0 ]]; then
        print_pass "防护系统有效，阻止了 $blocked_count/$attack_count 个攻击请求"
    else
        print_info "攻击模拟测试: 阻止了 $blocked_count/$attack_count 个请求"
    fi

    echo ""
}

# 测试结果汇总
print_summary() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  测试完成总结${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo -e "总测试数: $TOTAL_TESTS"
    echo -e "通过测试: ${GREEN}$PASSED_TESTS${NC}"
    echo -e "失败测试: ${RED}$FAILED_TESTS${NC}"
    echo -e "通过率: $(( PASSED_TESTS * 100 / TOTAL_TESTS ))%"

    if [[ "$FAILED_TESTS" -eq 0 ]]; then
        echo -e "${GREEN}所有测试通过！限流和防刷系统工作正常。${NC}"
    else
        echo -e "${YELLOW}部分测试失败，请检查相关配置和日志。${NC}"
    fi

    echo -e "${BLUE}========================================${NC}"
}

# 主执行函数
main() {
    print_header

    # 检查服务是否可用
    if ! curl -s "$BASE_URL/auth/login" > /dev/null; then
        echo -e "${RED}错误: 无法连接到API服务 $BASE_URL${NC}"
        echo -e "${YELLOW}请确保服务正在运行，然后重试。${NC}"
        exit 1
    fi

    # 执行所有测试
    test_basic_rate_limit_headers
    test_login_rate_limit
    test_user_agent_detection
    test_honeypot_detection
    test_rapid_request_detection
    test_rate_limit_stats
    test_rate_limit_config
    test_combined_attack_simulation

    # 输出总结
    print_summary
}

# 运行主函数
main "$@"