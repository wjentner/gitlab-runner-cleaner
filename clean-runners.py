import datetime
import os

from kubernetes import client, config
from datetime import datetime, timezone


def _get_current_namespace() -> str:
    """
    copied from https://github.com/kubernetes-client/python/issues/363#issuecomment-1122471443
    :return:
    """
    ns_path = "/var/run/secrets/kubernetes.io/serviceaccount/namespace"
    if os.path.exists(ns_path):
        with open(ns_path) as f:
            return f.read().strip()
    try:
        _, active_context = config.list_kube_config_contexts()
        return active_context["context"]["namespace"]
    except KeyError:
        return "default"


NAMESPACE: str = os.getenv('GRC_NAMESPACE') or _get_current_namespace()
CUTOFFHR: float = float(os.getenv('GRC_HOUR_THRESHOLD') or 1.5)
RETRY: int = int(os.getenv('GRC_NUM_RETRIES') or 10)
CONTEXT: str | None = os.getenv('GRC_CONTEXT')
RESOURCE_PREFIX: str = os.getenv('GRC_RESOURCE_PREFIX') or 'runner-'
CLEAN_RESOURCES: list[str] = ['pod', 'secret', 'configmap']
if os.getenv('GRC_RESOURCES'):
    CLEAN_RESOURCES = str(os.getenv('GRC_RESOURCES')).split(',')
    CLEAN_RESOURCES = [item[0:-1].lower() + item[-1].lower().replace('s', '') for item in CLEAN_RESOURCES]

# Configs can be set in Configuration class directly or using helper utility
config.load_kube_config(context=CONTEXT)
v1 = client.CoreV1Api()


def _delete_resource(list, resource: str, delete_func):
    if resource not in CLEAN_RESOURCES:
        print(f'skip {resource}s')
        return
    print(f"Delete {resource} older than {CUTOFFHR} hours")
    now = datetime.now(timezone.utc)
    for i in list.items:
        diff = now - i.metadata.creation_timestamp
        hdiff = diff.total_seconds() / 3600
        if i.metadata.name.startswith(RESOURCE_PREFIX) and hdiff > CUTOFFHR:
            print(
                f'{resource} {i.metadata.name} created at {i.metadata.creation_timestamp} is {diff.total_seconds() / 3600} hours old, deleting ...')
            delete_func(name=i.metadata.name, namespace=NAMESPACE)
    print(f'done deleting {resource}\n\n')


count = 0
while count < RETRY:
    try:
        _delete_resource(v1.list_namespaced_pod(namespace=NAMESPACE, watch=False), 'pod', v1.delete_namespaced_pod)
        _delete_resource(v1.list_namespaced_secret(namespace=NAMESPACE, watch=False), 'secret',
                         v1.delete_namespaced_secret)
        _delete_resource(v1.list_namespaced_config_map(namespace=NAMESPACE, watch=False), 'configmap',
                         v1.delete_namespaced_config_map)
        break
    except Exception as e:
        print(e)
        count += 1

if count >= RETRY:
    raise Exception('I was not able to delete all resources')

print('Exiting script')
