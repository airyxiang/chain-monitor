TAG = latest
DOCKER_LOCAL = transaction-service:$(TAG)
DOCKER_REPO = 621554677845.dkr.ecr.us-east-1.amazonaws.com/transaction-service
DOCKER_PROD_REPO = 621554677845.dkr.ecr.us-east-1.amazonaws.com/prod-transaction-service
DOCKER_STAGING_REPO = 890812429068.dkr.ecr.us-east-1.amazonaws.com/tutoken-staging-transaction-service
DOCKER_REMOTE = $(DOCKER_REPO):$(TAG)
DOCKER_PROD_REMOTE = $(DOCKER_PROD_REPO):$(TAG)
DOCKER_STAGING_REMOTE = $(DOCKER_STAGING_REPO):$(TAG)

.PHONY: build
build:
	docker build -t $(DOCKER_LOCAL) --build-arg FURY_AUTH .

buildstaging:
	docker build -t $(DOCKER_LOCAL) --build-arg \
	BASE_IMAGE="tron2020/base_image:python3.10.5-slim-bullseye" \
	--build-arg FURY_AUTH .

push:
	docker tag $(DOCKER_LOCAL) $(DOCKER_REMOTE)
	docker push $(DOCKER_REMOTE)

pushprod:
	docker tag $(DOCKER_LOCAL) $(DOCKER_PROD_REMOTE)
	docker push $(DOCKER_PROD_REMOTE)

pushstaging:
	docker tag $(DOCKER_LOCAL) $(DOCKER_STAGING_REMOTE)
	docker push $(DOCKER_STAGING_REMOTE)

buildpush: build push

buildpushprod: build pushprod

buildpushstaging: build pushstaging

buildlocal:
	docker-compose build

start:
	docker-compose up -d -t1

startuwsgi:
	DEVELOP=0 docker-compose up -d -t1

stop:
	docker-compose down -t1

buildproto:
	chain_monitor/api/grpc/makeprotobufs

buildproto-async:
	chain_monitor/api/grpc/makeprotobufs-async

proto: buildproto
	mkdir -p dist && \
	cp -r chain_monitor/api/grpc/dist/*.tar.gz dist

proto-async: buildproto-async
	mkdir -p dist && \
	cp -r chain_monitor/api/grpc/chain_monitor_protobuf_async/dist/*.tar.gz dist

proto-all: proto proto-async

taskdefs:
	cd deployment && ./compile.py

clean:
	rm -rf dist/*

pip-compile:
	docker build -f requirements/piptools.Dockerfile -t piptools ./requirements
	docker run --rm -v $(PWD)/requirements:/code -w /code -e FURY_AUTH=${FURY_AUTH} piptools ./prepare_requirements.sh
