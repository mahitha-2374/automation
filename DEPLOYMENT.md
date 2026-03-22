# Deployment Configuration

## Environment Variables

```bash
# Flask
FLASK_ENV=production
FLASK_APP=api/server.py

# Streamlit
STREAMLIT_LOGGER_LEVEL=error
```

## Production Deployment

### Option 1: Cloud Platform (AWS Lightsail / DigitalOcean)

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Build
docker build -t iam-tool .

# Run
docker run -d -p 8501:8501 -p 5000:5000 iam-tool
```

### Option 2: Local Server

```bash
# Install systemd service
sudo cp iam-automation.service /etc/systemd/system/
sudo systemctl enable iam-automation
sudo systemctl start iam-automation
```

### Option 3: Kubernetes

```bash
kubectl apply -f k8s/deployment.yaml
```

## Reverse Proxy (Nginx)

```nginx
server {
    listen 80;
    server_name iam-tool.example.com;

    location / {
        proxy_pass http://localhost:8501;
    }

    location /api/ {
        proxy_pass http://localhost:5000;
    }
}
```

## Monitoring

Check logs:

```bash
tail -f logs/app.log
```

Monitor ports:

```bash
netstat -tlnp | grep -E "8501|5000"
```

## Backup Strategy

```bash
# Backup learning memory
cp memory/knowledge.json backups/knowledge_$(date +%Y%m%d).json

# Backup outputs
tar -czf backups/output_$(date +%Y%m%d_%H%M%S).tar.gz output/
```
