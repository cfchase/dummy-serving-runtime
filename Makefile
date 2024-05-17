build:
	podman build -t quay.io/cfchase/dummy-runtime:latest -f docker/Dockerfile .

push:
	podman push quay.io/cfchase/dummy-runtime:latest

run:
	podman run -ePORT=8080 -p8080:8080 quay.io/cfchase/dummy-runtime:latest

deploy:
	oc apply -f templates/sr-is.yaml

undeploy:
	oc delete -f templates/sr-is.yaml

test-v1:
	curl -H "Content-Type: application/json" localhost:8080/v1/models/model:predict -d @./scripts/v1_input.json | jq
