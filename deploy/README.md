# Kubernetes Deploy
We will need to use `kind` and `helm` to launch the application locally.
- [Kind - Run Kubernetes Locally](https://kind.sigs.k8s.io/)

## Quick Start
```commandline
sh ./start.sh
```
- This [start.sh](./start.sh) will help you to bootstrap everything.


## Prerequisites
### Install Kind (MacOS)
```commandline
brew install kind
```

### Create a kind Cluster
```commandline
kind create cluster --config ./kind-conf.yaml -n kind-flask
```

- Allow `3000` port on the [kind-conf.yaml](kind-conf.yaml) for allowing port be accessed from local. 

For other Linux distribution, please visit the [Kind website - Installation](https://kind.sigs.k8s.io/docs/user/quick-start/#installation) for installation guide.

### Launch Ingress-Nginx
```commandline
helm install ingress-nginx ingress-nginx/ingress-nginx -f ./ingress-nginx-values.yaml
```
> We use `hostPort` here for Ingress because we run application locally, 
> if we go to cloud environments, 
> we should use LoadBalancer type Service or Load balancers from Cloud Providers and its controller, 
> e.g. AWS Application Load Balancer and Load Balancer Controller. 

### Inject Secrets to Cluster
```commandline
kubectl apply -f ./secrets.yaml
```

## Deploy Redis and Flask
### Launch Redis
```commandline
helm upgrade -i redis oci://registry-1.docker.io/bitnamicharts/redis -f ./redis-values.yaml
```
> We should be a custom Helm Chart of Redis, better managed on our own.
> But now I am using a public Chart for quick launching a Redis as demo needed.

### Launch Flask Application
```commandline
helm upgrade -i flask-app ./charts -f flask-app-values.yaml
```

### Check Result
```
kubectl get pod
curl -L http://localhost:3000/
```


## Cleanup
```commandline
kind delete cluster -n kind-flask
```


## NOTE
- Putting Flask and Redis together in a mono Helm Chart might not be a good idea, 
because you don't want them to affect each other when you're just trying to upgrade one of them. 
One Chart, do one thing.
- In real environment, what I will do --
  - Clear directory structure for different environments --
    - redis/values.prod.yaml / redis/values.stg.yaml
    - flask/values.prod.yaml / flask/values.stg.yaml
    - Also consider `FluxCD` or `Helmfile` and `ArgoCD` for Helm releases Managements and GitOps implementations.
  - Use [external-secrets](https://github.com/external-secrets/external-secrets) to retrieve secrets from Cloud Provider services, e.g. AWS SecretsManager.
    - Native Kubernetes Secret is base64 encode, not encryption.
  - Use Cloud Load Balancer instead of `hostPort`, using `host netowrk` is considered as an insecured approach.
  - Build our own Redis and Ingress-Nginx Helm Chart for customization. (optional)
- How do I create this Helm Chart -- `helm create flask-app .`, this command will generate a very comphersive chart template for us.