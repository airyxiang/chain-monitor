#!/bin/bash

pip-compile \
		--extra-index-url https://${FURY_AUTH}:@pypi.fury.io/trustdev/ \
		--extra-index-url https://download.sqreen.io/python/alpine \
		requirements.in

pip-compile \
  --extra-index-url https://${FURY_AUTH}:@pypi.fury.io/trustdev/ \
  --extra-index-url https://download.sqreen.io/python/alpine \
  dev-requirements.in
