apiVersion: batch/v1
kind: Job
metadata:
  name: {{ project_dns_name }}-sync-db
  namespace: {{ k8s_namespace }}
spec:
  template:
    metadata:
      name: {{ project_dns_name }}
      labels:
        app: {{ project_dns_name }}
        job: {{ project_dns_name }}
    spec:
      containers:
      - name: {{ project_dns_name }}-job
        image: {{ docker_registry }}/laiwanio/{{ project }}:{{ docker_tag }}
        env:
          - name: STAGE
            value: {{ stage }}
{% for key, value in config.items() %}
          - name: {{ key | upper }}
            value: "{{ value }}"
{% endfor %}
        command: ["bash"]
        args: ["-c", "python manage.py sync_db && python manage.py migrate"]

      imagePullSecrets:
      - name: {{ docker_pull_secret }}
      restartPolicy: Never

---
kind: ConfigMap
apiVersion: v1
metadata:
  namespace: {{ k8s_namespace }}
  name: {{ project_dns_name }}-route-config
data:
  route.yaml: |
    services:
      - name: {{ project }}
        host: {{ project_dns_name }}.{{ k8s_namespace }}.svc.cluster.local
        port: 80
        routes:
{% for route in kong_routes %}
{% if route.type == 'service' and stage == 'production' %}
{% continue %}
{% endif %}
          - paths: {{ route.route }}
            strip_path: false
{% if 'plugins' in route %}
            plugins:
{% for plugin in route['plugins'] %}
{% if plugin == 'cors' %}
              - name: cors
{% endif %}
{% if plugin == 'oauth2' %}
              - name: oauth2
                config:
                  global_credentials: true
                  enable_password_grant: true
{% endif %}
{% if plugin == 'acl' %}
              - name: acl
                config:
                  whitelist:
                    - read
                    - write
{% endif %}
{% endfor %}
{% endif %}
{% endfor %}

---
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ project_dns_name }}-sync-route
  namespace: {{ k8s_namespace }}
spec:
  template:
    metadata:
      labels:
        app: {{ project_dns_name }}
        job: {{ project_dns_name }}
    spec:
      restartPolicy: OnFailure
      volumes:
      - name: config
        configMap:
          name: {{ project_dns_name }}-route-config
          items:
          - key: route.yaml
            path: route.yaml
      containers:
      - name: sync-kong-route
        image: registry-vpc.cn-hongkong.aliyuncs.com/appdev/kong_cli:0.1
        imagePullPolicy: IfNotPresent
        env:
          - name: KONG_URL
            value: {{ config.kong_url }}
        volumeMounts:
        - name: config
          mountPath: /config
        command: ["bash"]
        args: ["-c", "kong --yaml /config/route.yaml"]
