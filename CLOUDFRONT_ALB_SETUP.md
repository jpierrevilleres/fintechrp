# CloudFront/ALB SSL Offloading - Deployment Steps
# ==========================================

## ✅ Infrastructure Already Configured

Your setup:
- CloudFront Distribution: d21foi2wtblvh8.cloudfront.net
- ALB: fintechrp-dynamic-content-alb (port 80 & 443 listeners)
- Target Group: fintechrp-target-group (HTTP:80, 1 healthy target)
- SSL Certificates: Configured on ALB and CloudFront
- DNS Provider: Namecheap
- Current: Let's Encrypt SSL on EC2 nginx (to be removed)

## 🎯 What We're Doing

**Goal:** Remove SSL from EC2 nginx, let CloudFront/ALB handle all SSL/HTTPS

**Current Flow:**
```
User → CloudFront (HTTPS) → ALB (HTTPS:443) → EC2 nginx (HTTPS:443 with Let's Encrypt) → Django
```

**Target Flow:**
```
User → CloudFront (HTTPS) → ALB (HTTP:80) → EC2 nginx (HTTP:80) → Django
```

## 📋 Deployment Steps

### Step 1: Update Namecheap DNS (if not already done)

Point your domain to CloudFront:
1. Log into Namecheap
2. Go to Advanced DNS for fintechrp.com
3. Update records:
   ```
   Type: CNAME Record
   Host: @
   Value: d21foi2wtblvh8.cloudfront.net
   TTL: Automatic

   Type: CNAME Record
   Host: www
   Value: d21foi2wtblvh8.cloudfront.net
   TTL: Automatic
   ```

### Step 2: Verify CloudFront Configuration

Check that CloudFront is configured to forward HTTP to ALB:
- Origin Protocol: HTTP only (to ALB port 80)
- Viewer Protocol Policy: Redirect HTTP to HTTPS
- Origin Request Policy: Forward Host header

### Step 3: Update ALB Listener

Currently you have both listeners (HTTP:80 and HTTPS:443). 
**Recommended:** Keep only HTTP:80 listener forwarding to target group.

Optional: You can keep HTTPS:443 for direct ALB access, but CloudFront should use HTTP:80.

### Step 4: Deploy New Nginx Configuration

### 4.1 Backup Current Nginx Config
```bash
ssh -i django.key.pem ubuntu@13.62.64.45
cd /etc/nginx/sites-available
sudo cp fintechrp fintechrp.backup.letsencrypt
```

### 4.2 Upload New Configuration
From local machine:
```powershell
scp -i F:/WEBSITE/RSA/django.key.pem nginx_alb_cloudfront.conf ubuntu@13.62.64.45:/tmp/
```

### 4.3 Install New Configuration
```bash
ssh -i F:/WEBSITE/RSA/django.key.pem ubuntu@13.62.64.45
sudo cp /tmp/nginx_alb_cloudfront.conf /etc/nginx/sites-available/fintechrp
sudo nginx -t
sudo systemctl reload nginx
```

### 4.4 Verify Nginx
```bash
# Check nginx is listening on port 80 only
sudo netstat -tlnp | grep nginx

# Should show:
# tcp  0  0  0.0.0.0:80  0.0.0.0:*  LISTEN  xxx/nginx
```

## Step 5: Verification & Testing

### 5.1 Test Health Check
```bash
curl http://localhost/health
# Should return: OK
```

### 5.2 Test from ALB
Once ALB is configured, check target health in AWS console.

### 5.3 Test HTTPS Redirect
```bash
curl -I http://fintechrp.com
# Should see 301/302 redirect to https://fintechrp.com from CloudFront
```

### 5.4 Test Full Stack
```bash
curl -I https://fintechrp.com
# Should return 200 OK with CloudFront headers
```

### 5.5 Check Django Sees HTTPS
Access admin panel and check Django debug toolbar or logs:
- request.is_secure() should return True
- request.scheme should be 'https'

## Step 6: Optional - Disable/Remove Let's Encrypt

### 6.1 Stop Certbot Auto-Renewal
```bash
sudo systemctl stop certbot.timer
sudo systemctl disable certbot.timer
```

### 6.2 Remove Cron Jobs (if any)
```bash
sudo crontab -l | grep certbot
# Remove any certbot renewal cron jobs
sudo crontab -e
```

### 6.3 Keep Certificates (Optional)
You can keep the Let's Encrypt certificates as backup, but they won't be used.

## Rollback Plan

If something goes wrong:

```bash
# Restore old nginx config
sudo cp /etc/nginx/sites-available/fintechrp.backup.letsencrypt /etc/nginx/sites-available/fintechrp
sudo nginx -t
sudo systemctl reload nginx

# Update ALB to forward to port 443
# Update EC2 security group to allow 443 from ALB
```

## Architecture Benefits

✅ Improved Performance:
   - CloudFront edge caching reduces latency
   - Static assets served from CloudFront edge locations
   - SSL/TLS termination offloaded from EC2

✅ Better Security:
   - DDoS protection via CloudFront
   - WAF can be attached to CloudFront
   - SSL certificates managed by AWS (auto-renewal)

✅ Reduced EC2 Load:
   - No SSL/TLS computation overhead
   - More CPU/memory for application

✅ Easier Certificate Management:
   - AWS Certificate Manager handles renewals
   - No more Let's Encrypt manual updates

## Monitoring

### CloudFront Metrics
- Requests, BytesDownloaded, BytesUploaded
- 4xx/5xx Error Rate
- Cache Hit Rate

### ALB Metrics
- TargetResponseTime
- HealthyHostCount
- UnHealthyHostCount
- RequestCount

### EC2 Nginx Logs
```bash
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Django/Gunicorn Logs
```bash
tail -f /home/ubuntu/fintechrp/gunicorn-access.log
tail -f /home/ubuntu/fintechrp/gunicorn-error.log
```

## Common Issues & Solutions

### Issue: Redirect Loop
**Symptom:** Browser shows "too many redirects"
**Cause:** Django doesn't see X-Forwarded-Proto header
**Solution:** Verify SECURE_PROXY_SSL_HEADER is set in Django settings (already done)

### Issue: Mixed Content Warnings
**Symptom:** Browser console shows mixed content errors
**Cause:** Hardcoded HTTP URLs in templates
**Solution:** Use relative URLs or request.build_absolute_uri()

### Issue: ALB Health Check Failing
**Symptom:** Target shows unhealthy in ALB console
**Cause:** /health endpoint not responding or security group blocking
**Solution:** 
- Check nginx config has /health location
- Verify EC2 security group allows port 80 from ALB SG
- Test locally: curl http://localhost/health

### Issue: Static Files Not Loading
**Symptom:** CSS/JS/images return 404
**Cause:** CloudFront cache behavior not forwarding properly
**Solution:** 
- Add cache behaviors for /static/* and /media/*
- Or configure origin to forward all paths
- Clear CloudFront cache (invalidation)

## Cost Optimization

- Enable CloudFront compression for text assets
- Set appropriate cache TTLs for static assets
- Use CloudFront price class (consider US+EU if most traffic is there)
- Monitor CloudFront data transfer costs
- Consider S3 for static assets to reduce EC2 data transfer costs

## Next Steps

**Ready to deploy? Follow these commands:**

```powershell
# 1. Commit configuration files
git add nginx_alb_cloudfront.conf CLOUDFRONT_ALB_SETUP.md
git commit -m "Add CloudFront/ALB nginx configuration for SSL offloading"
git push origin fix/remove-duplicate-stylecss

# 2. Deploy to EC2 (run each command carefully)
# Backup current config
ssh -i F:/WEBSITE/RSA/django.key.pem ubuntu@13.62.64.45 "sudo cp /etc/nginx/sites-available/fintechrp /etc/nginx/sites-available/fintechrp.backup.letsencrypt"

# Upload new config
scp -i F:/WEBSITE/RSA/django.key.pem nginx_alb_cloudfront.conf ubuntu@13.62.64.45:/tmp/

# Install and test
ssh -i F:/WEBSITE/RSA/django.key.pem ubuntu@13.62.64.45 "sudo cp /tmp/nginx_alb_cloudfront.conf /etc/nginx/sites-available/fintechrp && sudo nginx -t && sudo systemctl reload nginx"

# 3. Verify
# Test health check
ssh -i F:/WEBSITE/RSA/django.key.pem ubuntu@13.62.64.45 "curl -I http://localhost/health"

# 4. Update EC2 security group to allow HTTP (80) from ALB security group only

# 5. Test your site
# Open https://fintechrp.com in browser
```

---
Last Updated: November 16, 2025
Deployment Status: Ready to deploy
