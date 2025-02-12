# Registry
This is a WIP feature.

## Generate a cert for private registry with self-signed cert
```
openssl req -x509 -newkey rsa:4096 -sha256 -days 365 -nodes \
  -keyout registry.key -out registry.crt -subj "/CN=docker-registry.default.svc.cluster.local" \
  -addext "subjectAltName = DNS:docker-registry.default.svc.cluster.local,DNS:docker-registry,DNS:localhost:30500,IP:127.0.0.1"

kubectl create secret tls registry-tls --cert=registry.crt --key=registry.key -n default
```

## Github Runner trust the self-signed cert
kubectl create secret generic docker-registry-cert \
  --from-file=ca.crt=registry.crt \
  -n github-runner
```

