# Python Example

```bash
ops-ready-kit analyze examples/python-fastapi --output /tmp/python-fastapi-ops
```

Expected detections:

- Python
- FastAPI
- Missing Dockerfile unless the example adds one
- Missing Kubernetes manifests unless the example adds them

## Dockerfile Signals

When a Dockerfile exists, ops-ready-kit summarizes:

- base images
- exposed ports
- healthcheck presence
- runtime user
- workdir
- command
