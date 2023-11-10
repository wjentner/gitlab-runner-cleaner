# Gitlab Runner Cleaner

This is a simple script that will clean up leftover resources created.
The most common cause are timeouts of the kubernetes API.

> DANGER: This script uses a simple heuristic. 
> Please make sure that the script does not accidentally delete important resources in your namespace.
> The script will not have any user interactions once started.

## Configuration

The script can be configured using environment variables.

| Variable              | Description                                                                                                                                                                                                                                                               | Default                 |
|-----------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------|
| `GRC_NAMESPACE`       | Set the kubernetes namespace to clean up the resources in. If not set explicitly, the namespace will be determined in the following order: 1. pod namespace (if script runs inside pod); 2. namespace of context (determined from config); 3. namespace will be `default` | `null`                  |
| `GRC_CONTEXT`         | If the kubernetes config has multiple contexts, the context can be specified here. If it is not set, the current context will be used.                                                                                                                                    | `null`                  |
| `GRC_HOUR_THRESHOLD`  | A number that determines the minimum age of the resource to delete (in hours). Defaults to `1.5` (1 hour 30 minutes) as one hour is the default timeout for gitlab jobs.                                                                                                  | `1.5`                   |
| `GRC_RESOURCE_PREFIX` | Only resources with that prefix and above the age threshold (see `GRC_HOUR_THRESHOLD`) will be deleted.                                                                                                                                                                   | `runner-`               |
| `GRC_RESOURCES`       | A comma-separated list of resources to clean up. Must be of `pod`, `secret`, `configmap`. Other resources will be ignored.                                                                                                                                                | `pod,secret,configmap` |
| `GRC_NUM_RETRIES` | An integer number that determines the number of retries before the script fails. This is included as the main reason for this script are timeouts with the kubernetes api.                                                                                                | `10` |

## Usage

### Kubernetes CronJob (preferred)

### Docker

```shell
docker run --rm -v ~/.kube/config:/root/.kube/config -e GRC_NAMESPACE=<GITLAB-RUNNER-NAMESPACE> ghcr.io/wjentner/gitlab-runner-cleaner:latest
```

### Docker-compose

This file mounts your default kubernetes config into the container.
Make sure to adjust the environment variables.

Docker compose file:
```yaml
services:
  clean_runners:
    image: ghcr.io/wjentner/gitlab-runner-cleaner:latest
    volumes:
      # Linux / Mac
      - '~/.kube/config:/root/.kube/config'
      # Windows
      - 
    environment:
      GRC_NAMESPACE: '<GITLAB RUNNER NAMESPACE>'
      # GRC_CONTEXT: '<KUBERNETES CONTEXT>'
      # GRC_HOUR_THRESHOLD: 1.5
      # GRC_RESOURCE_PREFIX: 'runner-'
      # GRC_RESOURCES: 'pod,secret,configmap'
      # GRC_NUM_RETRIES: 10
```

Now run:
```shell
docker compose run clean_runners
```

