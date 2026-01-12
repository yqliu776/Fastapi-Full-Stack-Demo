# API限流和防刷策略测试文档

## 测试环境
- 基础URL: http://localhost:8000
- 测试工具: curl + bash脚本
- 预期响应头: X-RateLimit-* 系列头信息

## 测试账号信息
请提供测试账号，我将基于这些账号进行测试：
- 用户名: [待提供]
- 密码: [待提供]
- Token: [待获取]

## 一、限流策略测试

### 1.1 登录接口限流测试
**策略**: 登录接口限制为每分钟10次请求

```bash
# 测试用例1: 正常登录请求
 curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_user",
    "password": "test_password"
  }'

# 预期响应:
# - 状态码: 200/401 (成功/认证失败)
# - X-RateLimit-Limit: 10
# - X-RateLimit-Remaining: 9 (第一次请求后)
```

```bash
# 测试用例2: 触发限流 - 连续11次请求
 for i in {1..11}; do
  echo "请求 $i:"
  curl -s -X POST "http://localhost:8000/auth/login" \
    -H "Content-Type: application/json" \
    -d '{
      "username": "test_user",
      "password": "test_password"
    }' \
    -w "HTTP状态: %{http_code}, 剩余请求: %{header{X-RateLimit-Remaining}}\n"
 done

# 预期结果:
# - 前10次: 正常响应 (200/401)
# - 第11次: 429 Too Many Requests
# - 响应包含 Retry-After 头
```

### 1.2 注册接口限流测试
**策略**: 注册接口限制为每小时5次请求

```bash
# 测试用例3: 注册接口限流测试
 for i in {1..6}; do
  echo "注册请求 $i:"
  curl -s -X POST "http://localhost:8000/users/register" \
    -H "Content-Type: application/json" \
    -d '{
      "username": "newuser'$i'",
      "email": "newuser'$i'@example.com",
      "password": "password123"
    }' \
    -w "HTTP状态: %{http_code}\n"
 sleep 1
 done

# 预期结果:
# - 前5次: 正常响应
# - 第6次: 429 Too Many Requests
```

### 1.3 默认限流规则测试
**策略**: 默认每分钟100次请求，突发容量10

```bash
# 测试用例4: 一般API接口测试
 curl -X GET "http://localhost:8000/rate-limit/config" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -w "Limit: %{header{X-RateLimit-Limit}}, Remaining: %{header{X-RateLimit-Remaining}}\n"

# 预期响应:
# - X-RateLimit-Limit: 100
# - X-RateLimit-Remaining: 99 (首次请求)
```

### 1.4 不同限流算法测试

```bash
# 测试用例5: 令牌桶算法 (突发流量测试)
# 快速连续发送10个请求
 for i in {1..10}; do
  curl -s "http://localhost:8000/rate-limit/config" \
    -H "Authorization: Bearer YOUR_TOKEN" \
    -w "请求$i - 剩余: %{header{X-RateLimit-Remaining}}\n" &
 done
 wait

# 预期结果: 令牌桶允许突发流量
```

```bash
# 测试用例6: 滑动窗口算法
# 修改配置后测试连续请求
# 需要在配置中设置 RATE_LIMIT_ALGORITHM=sliding_window
```

## 二、防刷策略测试

### 2.1 User-Agent检测测试
**策略**: 检测可疑的用户代理字符串

```bash
# 测试用例7: 可疑User-Agent (python-requests)
 curl -X GET "http://localhost:8000/auth/login" \
  -H "User-Agent: python-requests/2.28.1" \
  -H "X-Bot-Debug: true" \
  -w "Bot Score: %{header{X-Bot-Score}}\n"

# 预期响应:
# - X-Bot-Score: > 0 (可疑分数)
# - X-Bot-Suspicious: true
```

```bash
# 测试用例8: 可疑User-Agent (curl)
 curl -X GET "http://localhost:8000/auth/login" \
  -H "User-Agent: curl/7.68.0" \
  -w "Bot Score: %{header{X-Bot-Score}}\n"

# 预期响应: 正常浏览器UA得分较低
```

```bash
# 测试用例9: 正常User-Agent (Chrome)
 curl -X GET "http://localhost:8000/auth/login" \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36" \
  -w "Bot Score: %{header{X-Bot-Score}}\n"

# 预期响应: 得分较低，不被标记为可疑
```

### 2.2 蜜罐陷阱测试
**策略**: 检测对隐藏/管理路径的访问

```bash
# 测试用例10: 访问蜜罐路径
 paths=(
  "/admin.php"
  "/wp-admin"
  "/config.php"
  "/.env"
  "/phpmyadmin"
  "/.git"
  "/api/private"
  "/_debug"
 )

 for path in "${paths[@]}"; do
  echo "测试路径: $path"
  curl -s -I "http://localhost:8000$path" \
    -H "User-Agent: python-requests/2.28.1" \
    -w "HTTP状态: %{http_code}, X-Bot-Detected: %{header{X-Bot-Detected}}\n"
 done

# 预期结果:
# - 触发蜜罐检测
# - X-Bot-Detected: true
# - 可能被阻止访问 (403)
```

### 2.3 行为模式检测测试
**策略**: 检测自动化行为模式

```bash
# 测试用例11: 规律间隔请求 (机器人特征)
 for i in {1..10}; do
  curl -s "http://localhost:8000/auth/login" \
    -H "User-Agent: python-requests/2.28.1" \
    -o /dev/null \
    -w "请求$i - 状态: %{http_code}\n"
  sleep 1  # 精确1秒间隔，模拟机器人
 done

# 预期结果: 可能触发行为检测
```

```bash
# 测试用例12: 超快速请求 (超过人类速度)
 for i in {1..10}; do
  curl -s "http://localhost:8000/auth/login" \
    -H "User-Agent: python-requests/2.28.1" \
    -o /dev/null \
    -w "请求$i - 状态: %{http_code}\n" &
 done
 wait

# 预期结果: 触发快速请求检测
```

```bash
# 测试用例13: 突发大量请求
 for i in {1..70}; do
  curl -s "http://localhost:8000/auth/login" \
    -H "User-Agent: python-requests/2.28.1" \
    -o /dev/null \
    -w "." &
 done
 wait
 echo "完成70个并发请求"

# 预期结果: 触发每分钟请求数限制
```

### 2.4 验证码挑战测试
**策略**: 高度可疑请求触发验证码

```bash
# 测试用例14: 触发验证码挑战
# 组合多种可疑行为
 for i in {1..15}; do
  curl -s -X POST "http://localhost:8000/auth/login" \
    -H "User-Agent: python-requests/2.28.1" \
    -H "X-Forwarded-For: 192.168.1.$i" \
    -d '{"username":"admin","password":"admin123"}' \
    -w "请求$i - 状态: %{http_code}\n" &
 done
 wait

# 预期结果:
# - 状态码: 429
# - 响应消息: "请完成验证码验证"
# - X-Challenge-Required: captcha
```

## 三、综合测试用例

### 3.1 组合攻击测试

```bash
# 测试用例15: 模拟真实攻击场景
 attack_script() {
  # 使用不同IP和User-Agent
  local ip="192.168.1.$((RANDOM % 255))"
  local ua_index=$((RANDOM % 3))
  local user_agents=(
    "python-requests/2.28.1"
    "curl/7.68.0"
    "Wget/1.20.3"
  )

  curl -s -X POST "http://localhost:8000/auth/login" \
    -H "User-Agent: ${user_agents[$ua_index]}" \
    -H "X-Forwarded-For: $ip" \
    -d '{"username":"admin","password":"password123"}' \
    -o /dev/null \
    -w "IP: $ip, UA: ${user_agents[$ua_index]}, 状态: %{http_code}\n"
 }

# 启动10个并发攻击
 for i in {1..10}; do
  attack_script &
 done
 wait

# 预期结果: 多种防护机制同时触发
```

### 3.2 白名单绕过测试

```bash
# 测试用例16: 添加IP到白名单
 curl -X POST "http://localhost:8000/rate-limit/whitelist" \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "127.0.0.1",
    "expire_time": 3600
  }'

# 然后再次进行限流测试，验证白名单效果
```

### 3.3 黑名单封禁测试

```bash
# 测试用例17: 添加可疑IP到黑名单
 curl -X POST "http://localhost:8000/rate-limit/blacklist" \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "192.168.1.100",
    "expire_time": 3600
  }'

# 从该IP发起的请求应该被直接拒绝
```

## 四、监控和统计测试

### 4.1 限流统计查询

```bash
# 测试用例18: 查询限流统计
 curl -X GET "http://localhost:8000/rate-limit/stats?scope=ip&identifier=127.0.0.1"

# 预期响应:
# {
#   "code": 200,
#   "message": "获取限流统计成功",
#   "data": {
#     "scope": "ip",
#     "identifier": "127.0.0.1",
#     "rate_limit_key": "rate_limit:ip:127.0.0.1",
#     "whitelisted": false,
#     "blacklisted": false
#   }
# }
```

### 4.2 配置查询

```bash
# 测试用例19: 查询当前限流配置
 curl -X GET "http://localhost:8000/rate-limit/config"

# 预期响应: 当前系统限流配置的详细信息
```

### 4.3 黑白名单列表

```bash
# 测试用例20: 查询白名单
 curl -X GET "http://localhost:8000/rate-limit/whitelist"

# 测试用例21: 查询黑名单
 curl -X GET "http://localhost:8000/rate-limit/blacklist"
```

## 五、性能测试

### 5.1 并发压力测试

```bash
# 测试用例22: 高并发测试
 ab -n 1000 -c 50 -T 'application/json' \
  -p login_data.json \
  -H "User-Agent: python-requests/2.28.1" \
  http://localhost:8000/auth/login

# login_data.json 内容:
# {"username":"test","password":"test"}
```

### 5.2 长时间稳定性测试

```bash
# 测试用例23: 持续压力测试
 for minute in {1..5}; do
  echo "第 $minute 分钟测试"
  for i in {1..120}; do  # 每分钟120个请求
    curl -s "http://localhost:8000/auth/login" \
      -H "User-Agent: python-requests/2.28.1" \
      -o /dev/null &
    sleep 0.5
  done
  wait
  echo "第 $minute 分钟完成"
 done
```

## 六、测试结果记录模板

| 测试用例 | 描述 | 预期结果 | 实际结果 | 状态 |
|---------|------|----------|----------|------|
| TC01 | 正常登录请求 | 200/401, 剩余9次 | 待测试 | 待验证 |
| TC02 | 触发限流 | 第11次429 | 待测试 | 待验证 |
| TC03 | 注册限流 | 第6次429 | 待测试 | 待验证 |
| TC04 | 一般接口限流 | 剩余99次 | 待测试 | 待验证 |
| TC05 | 令牌桶突发 | 允许突发 | 待测试 | 待验证 |
| TC06 | User-Agent检测 | 可疑UA高分 | 待测试 | 待验证 |
| TC07 | 蜜罐陷阱 | 403拒绝 | 待测试 | 待验证 |
| TC08 | 行为检测 | 机器人特征识别 | 待测试 | 待验证 |
| TC09 | 验证码挑战 | 429+验证码 | 待测试 | 待验证 |
| TC10 | 组合攻击 | 多重防护 | 待测试 | 待验证 |

## 七、自动化测试脚本

创建一个自动化测试脚本 `test_rate_limit.sh`:

```bash
#!/bin/bash

BASE_URL="http://localhost:8000"
TEST_RESULTS=""

# 颜色定义
 RED='\033[0;31m'
 GREEN='\033[0;32m'
 YELLOW='\033[1;33m'
 NC='\033[0m' # No Color

# 测试函数
 test_case() {
  local test_name="$1"
  local command="$2"
  local expected="$3"

  echo -e "${YELLOW}测试: $test_name${NC}"
  result=$(eval "$command" 2>/dev/null)

  if [[ "$result" == *"$expected"* ]]; then
    echo -e "${GREEN}✓ 通过${NC}"
    TEST_RESULTS+="✓ $test_name\n"
  else
    echo -e "${RED}✗ 失败${NC}"
    echo "预期: $expected"
    echo "实际: $result"
    TEST_RESULTS+="✗ $test_name\n"
  fi
 }

# 执行测试
 echo "开始限流和防刷测试..."

# 测试1: 检查限流头信息
 test_case "限流头信息" \
  "curl -s -I $BASE_URL/auth/login | grep -o 'X-RateLimit-Limit: [0-9]*'" \
  "X-RateLimit-Limit: 10"

# 测试2: 检查Bot检测头
 test_case "Bot检测头" \
  "curl -s -I -H 'User-Agent: python-requests/2.28.1' $BASE_URL/auth/login | grep -o 'X-Bot-Score'" \
  "X-Bot-Score"

# 测试3: 蜜罐路径检测
 test_case "蜜罐路径检测" \
  "curl -s -I -H 'User-Agent: python-requests/2.28.1' $BASE_URL/admin.php | grep -o 'X-Bot-Detected'" \
  "X-Bot-Detected"

# 输出总结
echo -e "\n${YELLOW}测试总结:${NC}"
echo -e "$TEST_RESULTS"
```

## 注意事项

1. **测试前准备**:
   - 确保Redis服务正常运行
   - 清理之前的测试数据
   - 准备测试用账号凭证

2. **安全考虑**:
   - 在测试环境中进行
   - 避免对生产环境造成影响
   - 测试完成后清理测试数据

3. **性能监控**:
   - 监控服务器资源使用情况
   - 观察响应时间变化
   - 检查错误日志

4. **配置调整**:
   - 根据实际测试结果调整阈值
   - 优化防护策略
   - 平衡安全性与用户体验

请提供测试账号信息，我将为你执行这些测试并记录实际结果。