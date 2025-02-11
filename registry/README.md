```
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout registry.key -out registry.crt -subj "/CN=docker-registry.default.svc.cluster.local"

kubectl create secret tls registry-tls --cert=registry.crt --key=registry.key -n default
```