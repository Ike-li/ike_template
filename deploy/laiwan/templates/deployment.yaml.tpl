apiVersion: v1
kind: Service
metadata:
  name: {{ project_dns_name }}
  namespace: {{ k8s_namespace }}
spec:
  ports:
  - port: 80
    targetPort: 8000
  selector:
    server: {{ project_dns_name }}

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ project_dns_name }}
  namespace: {{ k8s_namespace }}
spec:
  strategy:
    rollingUpdate:
      # 默认为 1，当 replicas 为 1 时，新的 pod 创建的同时就会删除老的 pod
      # 设置为 0，当 replicas 为 1 时，新的 pod 启动成功后才删除老的 pod
      maxUnavailable: 0
  replicas: {{ server.replicas }}
  revisionHistoryLimit: 10
  selector:
    matchLabels:
      server: {{ project_dns_name }}
  template:
    metadata:
      labels:
        # 设置 app = xxx label 用于在需要时，过滤出该服务用到的所有 k8s resources
        app: {{ project_dns_name }}
        # 设置 server = xxx 用于 Service 组件通过 selector 拿到所有的 HTTP Endpoints
        server: {{ project_dns_name }}
    spec:
      nodeSelector:
        stage: {{ stage }}
      containers:
      - name: {{ project_dns_name }}
        image: {{ docker_registry }}/laiwanio/{{ project }}:{{ docker_tag }}
        imagePullPolicy: Always
        lifecycle:
          preStop:
            exec:
              command:
              - sh
              - -c
              - "sleep 3"
        env:
        - name: STAGE
          value: {{ stage }}
{% for key, value in config.items() %}
        - name: {{ key | upper }}
          value: "{{ value }}"
{% endfor %}
        ports:
        - containerPort: 8000
        resources:
          requests:
            cpu: {{ server.requests.cpu }}
            memory: {{ server.requests.memory }}
          limits:
            cpu: {{ server.limits.cpu }}
            memory: {{ server.limits.memory }}
        livenessProbe:
          httpGet:
            path: /healthz
            port: 8000
          timeoutSeconds: 2
          # 留给 container 启动 gunicorn 的时间
          initialDelaySeconds: 2
        readinessProbe:
          httpGet:
            path: /readiness
            port: 8000
          timeoutSeconds: 2
          initialDelaySeconds: 2
        # 需要执行多条命令时使用，PID 为 1 的命令是 cmd3
        # command: ["bash"]
        # args: ["-c", "cmd1 && cmd2 && cmd3"]
        command: ["gunicorn", "wsgi:app"]
        args: ["-c", "extensions/gunicorn_config.py"]
      imagePullSecrets:
      - name: {{ docker_pull_secret }}
