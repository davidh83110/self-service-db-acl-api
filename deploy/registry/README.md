TODO: TLS SUpport
```
openssl req -x509 -newkey rsa:4096 -sha256 -days 365 -nodes \
  -keyout registry.key -out registry.crt -subj "/CN=docker-registry.default.svc.cluster.local" \
  -addext "subjectAltName = DNS:docker-registry.default.svc.cluster.local,DNS:docker-registry,DNS:localhost:30500,IP:127.0.0.1"


kubectl create secret tls registry-tls --cert=registry.crt --key=registry.key -n default

kubectl create secret generic docker-registry-cert \
  --from-file=ca.crt=registry.crt \
  -n github-runner
```