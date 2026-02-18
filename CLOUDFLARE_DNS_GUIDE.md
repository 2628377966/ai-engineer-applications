# Cloudflare DNS配置指南

## 🎯 架构概述

使用Cloudflare DNS替代AWS Route53，大幅降低DNS成本：
- **AWS Route53**: $0.50/月/zone + 查询费用
- **Cloudflare DNS**: 完全免费

## 📋 前置要求

1. Cloudflare账户（免费计划）
2. 域名（如果没有，可以使用Cloudflare提供的免费子域名）
3. AWS Lambda Function URL（已部署）
4. AWS S3 bucket（已部署）

## 🚀 配置步骤

### 1. 添加域名到Cloudflare

#### 1.1 登录Cloudflare
访问 https://dash.cloudflare.com/ 并登录

#### 1.2 添加站点
1. 点击"添加站点"
2. 输入你的域名（例如：`yourdomain.com`）
3. 选择"免费计划"
4. Cloudflare会显示需要添加的NS记录

#### 1.3 更新域名NS记录
1. 登录你的域名注册商（如GoDaddy、Namecheap等）
2. 将域名的NS记录更新为Cloudflare提供的NS记录
3. 等待DNS传播（通常需要几分钟到24小时）

### 2. 配置前端DNS（指向S3 + CloudFront）

#### 2.1 获取CloudFront分发URL
```bash
aws cloudfront describe-stacks \
  --stack-name smart-payment-checkout-frontend-dev \
  --query "Stacks[0].Outputs[?OutputKey=='CloudFrontURL'].OutputValue" \
  --output text
```

输出示例：
```
https://d1234567890.cloudfront.net
```

#### 2.2 在Cloudflare中添加CNAME记录

**选项A：使用主域名**
```
类型: CNAME
名称: @ (或 www)
目标: d1234567890.cloudfront.net
代理状态: 已代理 (橙色云朵)
TTL: 自动
```

**选项B：使用子域名**
```
类型: CNAME
名称: app
目标: d1234567890.cloudfront.net
代理状态: 已代理 (橙色云朵)
TTL: 自动
```

访问URL：
- 主域名：`https://yourdomain.com`
- 子域名：`https://app.yourdomain.com`

#### 2.3 配置SSL/TLS
1. 进入"SSL/TLS"选项卡
2. 设置模式为"完全"
3. 确保"始终使用HTTPS"已启用

#### 2.4 配置页面规则（可选）
1. 进入"规则" → "页面规则"
2. 添加规则：
   ```
   URL: yourdomain.com/*
   设置: 缓存级别: 绕过
   设置: 浏览器缓存TTL: 尊重现有头信息
   ```

### 3. 配置后端DNS（指向Lambda Function URL）

#### 3.1 获取Lambda Function URL
```bash
aws cloudformation describe-stacks \
  --stack-name smart-payment-checkout-backend-dev \
  --query "Stacks[0].Outputs[?OutputKey=='LambdaFunctionUrl'].OutputValue" \
  --output text
```

输出示例：
```
https://abc123xyz.lambda-url.us-east-1.on.aws
```

#### 3.2 在Cloudflare中添加CNAME记录

**选项A：使用API子域名**
```
类型: CNAME
名称: api
目标: abc123xyz.lambda-url.us-east-1.on.aws
代理状态: 仅DNS (灰色云朵)
TTL: 自动
```

**选项B：使用完整路径**
```
类型: CNAME
名称: api
目标: abc123xyz.lambda-url.us-east-1.on.aws
代理状态: 仅DNS (灰色云朵)
TTL: 自动
```

访问URL：
```
https://api.yourdomain.com
```

**重要提示：**
- 后端API使用"仅DNS"（灰色云朵），避免Cloudflare代理影响Lambda Function URL
- Lambda Function URL已经支持HTTPS，无需Cloudflare SSL

### 4. 配置CORS（如果需要）

#### 4.1 在Lambda Function URL中配置CORS
Lambda Function URL已经配置了CORS：
```yaml
Cors:
  AllowOrigins:
    - "*"
  AllowMethods:
    - POST
    - GET
    - OPTIONS
  AllowHeaders:
    - "*"
  MaxAge: 3600
```

#### 4.2 在Cloudflare中配置CORS（可选）
如果需要更细粒度的CORS控制，可以添加Transform规则：

1. 进入"规则" → "Transform Rules" → "修改请求头"
2. 添加规则：
   ```
   当请求匹配: api.yourdomain.com/*
   添加请求头: Access-Control-Allow-Origin: *
   添加请求头: Access-Control-Allow-Methods: POST, GET, OPTIONS
   添加请求头: Access-Control-Allow-Headers: *
   ```

### 5. 配置缓存策略（前端）

#### 5.1 Cloudflare自动缓存
Cloudflare会自动缓存静态文件：
- HTML: 默认2小时
- CSS/JS: 默认1天
- 图片: 默认1个月

#### 5.2 自定义缓存规则
1. 进入"缓存" → "配置"
2. 设置"浏览器缓存TTL"为"尊重现有头信息"
3. 设置"缓存级别"为"标准"

#### 5.3 清除缓存
```bash
# 通过Cloudflare API清除缓存
curl -X POST "https://api.cloudflare.com/client/v4/zones/YOUR_ZONE_ID/purge_cache" \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"purge_everything":true}'
```

## 🔧 高级配置

### 1. 配置Worker（可选）

如果需要额外的功能，可以使用Cloudflare Workers：

```javascript
// Cloudflare Worker示例
export default {
  async fetch(request) {
    const url = new URL(request.url);
    
    // API请求转发到Lambda
    if (url.pathname.startsWith('/api/')) {
      const apiUrl = 'https://api.yourdomain.com' + url.pathname;
      return fetch(apiUrl, request);
    }
    
    // 其他请求正常处理
    return fetch(request);
  }
}
```

### 2. 配置速率限制（可选）

1. 进入"安全性" → "WAF"
2. 添加速率限制规则：
   ```
   规则名称: API速率限制
   匹配条件: (http.host eq "api.yourdomain.com")
   限制: 100请求/分钟
   操作: 阻止
   ```

### 3. 配置Analytics

1. 进入"分析"选项卡
2. 查看流量、性能、安全统计
3. 设置自定义报告

### 4. 配置Page Rules

#### 4.1 前端缓存规则
```
URL: yourdomain.com/assets/*
设置: 缓存级别: 缓存所有内容
设置: 边缘缓存TTL: 1个月
```

#### 4.2 重定向规则
```
URL: yourdomain.com
设置: 转发URL: 301 - 永久重定向
目标URL: https://www.yourdomain.com
```

## 📊 DNS记录示例

### 完整DNS配置示例

```
类型    名称              目标                                      代理状态
A       @                 192.0.2.1 (你的服务器IP)                  已代理
CNAME   www               yourdomain.com                             已代理
CNAME   app               d1234567890.cloudfront.net                 已代理
CNAME   api               abc123xyz.lambda-url.us-east-1.on.aws      仅DNS
CNAME   cdn               d1234567890.cloudfront.net                 已代理
TXT     @                 "v=spf1 include:_spf.google.com ~all"     -
TXT     _dmarc            "v=DMARC1; p=none; rua=mailto:dmarc@yourdomain.com" -
```

## 🔍 验证配置

### 1. 验证前端DNS
```bash
# 检查DNS解析
nslookup app.yourdomain.com

# 检查HTTP响应
curl -I https://app.yourdomain.com
```

### 2. 验证后端DNS
```bash
# 检查DNS解析
nslookup api.yourdomain.com

# 检查API端点
curl https://api.yourdomain.com/health
```

### 3. 验证SSL证书
```bash
# 检查SSL证书
openssl s_client -connect api.yourdomain.com:443 -servername api.yourdomain.com
```

## 🛠️ 故障排查

### 问题1: DNS解析失败

**症状：** 域名无法访问

**解决方案：**
1. 检查DNS记录是否正确添加
2. 使用 `nslookup` 或 `dig` 检查DNS解析
3. 等待DNS传播（最多24小时）
4. 检查域名NS记录是否正确

### 问题2: 前端无法加载

**症状：** 前端页面显示错误

**解决方案：**
1. 检查CloudFront分发状态
2. 验证S3 bucket权限
3. 检查Cloudflare代理状态（橙色云朵）
4. 清除Cloudflare缓存

### 问题3: 后端API调用失败

**症状：** API请求返回错误

**解决方案：**
1. 检查Lambda Function URL是否正确
2. 验证CORS配置
3. 检查Lambda函数日志
4. 确保使用"仅DNS"代理模式

### 问题4: HTTPS证书错误

**症状：** 浏览器显示证书错误

**解决方案：**
1. 检查SSL/TLS设置
2. 等待证书签发（最多24小时）
3. 确保"始终使用HTTPS"已启用
4. 检查Origin证书配置

## 💰 成本对比

### DNS成本

| 服务 | 月成本 | 年成本 |
|-----|--------|--------|
| AWS Route53 | $0.50 + 查询费用 | $6.00+ |
| Cloudflare DNS | **免费** | **免费** |

**节省：** $6.00+/年

### CDN成本

| 服务 | 流量成本 | 特性 |
|-----|---------|------|
| AWS CloudFront | $0.085/GB | AWS集成 |
| Cloudflare CDN | **免费** | 全球CDN, DDoS防护 |

**节省：** $42.50/月（假设500GB流量）

### 总成本节省

- **DNS节省：** $6.00+/年
- **CDN节省：** $42.50/月
- **总节省：** ~$516/年

## 📚 相关资源

- [Cloudflare DNS文档](https://developers.cloudflare.com/dns/)
- [Cloudflare SSL/TLS文档](https://developers.cloudflare.com/ssl/)
- [Cloudflare Workers文档](https://developers.cloudflare.com/workers/)
- [AWS Lambda Function URL文档](https://docs.aws.amazon.com/lambda/latest/dg/urls-configuration.html)
- [AWS S3文档](https://docs.aws.amazon.com/s3/)

## 🎯 最佳实践

1. **使用子域名分离服务**
   - 前端：`app.yourdomain.com`
   - 后端：`api.yourdomain.com`
   - CDN：`cdn.yourdomain.com`

2. **配置适当的代理模式**
   - 前端：已代理（橙色云朵）
   - 后端：仅DNS（灰色云朵）

3. **启用安全功能**
   - SSL/TLS加密
   - DDoS防护
   - Web应用防火墙（WAF）

4. **监控和告警**
   - 设置DNS监控
   - 配置性能监控
   - 设置安全告警

5. **定期备份**
   - 导出DNS配置
   - 备份Cloudflare设置
   - 记录重要配置

---

**总结：** 使用Cloudflare DNS可以大幅降低成本，同时提供更好的性能和安全性！