SHELL = /usr/bin/env bash -xeuo pipefail

stack_name:=ffxiv-item-name-database-scraper
template_path:=template.yml

package:
	poetry run sam package --s3-bucket $$SAM_ARTIFACT_BUCKET --output-template-file $(template_path) --template-file sam.yml

deploy: package
	poetry run sam deploy \
		--stack-name $(stack_name) \
		--template-file $(template_path) \
		--capabilities CAPABILITY_IAM \
		--role-arn $$CLOUDFORMATION_DEPLOY_ROLE_ARN \
		--no-fail-on-empty-changeset
	poetry run aws cloudformation describe-stacks \
		--stack-name $(stack_name) \
		--query Stacks[0].Outputs