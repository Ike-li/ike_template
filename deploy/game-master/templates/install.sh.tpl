#!/bin/bash

kubectl delete -f job.yaml --wait=true

kubectl apply -f job.yaml

kubectl -n {{ k8s_namespace }} wait job -l job={{ project_dns_name }} --for=condition=complete --timeout=180s

if [ $? -eq 0 ]
then
  kubectl apply -f deployment.yaml
else
  echo "Error !!! Run job timeout"
  exit -1
fi
