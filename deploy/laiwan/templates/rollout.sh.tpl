#!/bin/bash

echo '###### All versions reserved:'
echo
kubectl -n {{ k8s_namespace }} rollout history deployment/{{ project_dns_name }}

currentVersion=$(kubectl -n {{ k8s_namespace }} rollout history deployment/{{ project_dns_name }} |tail -n 2| head -n 1 |awk '{print $1}')

echo "###### The current REVISION is $currentVersion"
read -p "###### Type ENTER to rollout the last version OR input the version to rollout: " version
echo

{% raw %}
if [ "${#version}" -eq 0 ]; then
{% endraw %}
	echo "###### Rollout to **Last** version"
	kubectl -n {{ k8s_namespace }} rollout undo deployment/{{ project_dns_name }}
else
	echo "###### Rollout to **$version** version"
	kubectl -n {{ k8s_namespace }} rollout undo deployment/{{ project_dns_name }} --to-revision="$version"
fi

echo
kubectl -n {{ k8s_namespace }} get pods -l app={{ project_dns_name }} -w
