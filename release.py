#!/usr/bin/env python
import boto3
import click
import subprocess

ecs_client = boto3.client('ecs')


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    '-e', '--env', default='prod', type=click.Choice(['prod', 'staging'])
)
@click.option('--build/--no-build', default=True)
@click.option('--deploy/--no-deploy', default=True)
def deploy(env, build=True, deploy=True):
    click.confirm(f'Please confirm you want to deploy to {env}', abort=True)

    if build:
        build_service(env)
    if deploy:
        deploy_service(env)


@cli.command(name='deploy-admin')
@click.option('--build/--no-build', default=True)
def deploy_admin_cmd(build=True):
    click.confirm('Please confirm you want to deploy to admin', abort=True)
    if build:
        build_service('prod')
    deploy_admin()


@cli.command()
@click.option(
    '-e', '--env', default='prod', type=click.Choice(['prod', 'staging'])
)
def build(env):
    build_service(env)


def _login_ecr():
    result = subprocess.run('aws ecr get-login --no-include-email', shell=True, check=True, capture_output=True)
    ecr_login_cmd = result.stdout
    subprocess.run(ecr_login_cmd, shell=True, check=True)


def build_service(env):
    _login_ecr()
    if env == 'prod':
        subprocess.run('make buildpush', shell=True, check=True)
    if env == 'staging':
        subprocess.run('make buildpushstaging', shell=True, check=True)


def deploy_service(env):
    print(f'--> Deploying to {env}')

    if env == 'prod':
        services = [
            'transaction-service-grpc',
            'transaction-service-worker',
            'transaction-service-worker-monitoring',
        ]
        for service in services:
            print(f'--> Deploying service {service}')
            ecs_client.update_service(
                cluster='transaction-service',
                service=service,
                forceNewDeployment=True,
            )
        single_services = [
            'transaction-service-scheduler',
        ]
        for service in single_services:
            print(f'--> Deploying service {service}')
            ecs_client.update_service(
                cluster='transaction-service',
                service=service,
                forceNewDeployment=True,
                deploymentConfiguration={
                    'maximumPercent': 100,
                    'minimumHealthyPercent': 0,
                },
            )

        deploy_admin()
    else:
        services = ('tutoken-staging-transaction-service-grpc', 'tutoken-staging-transaction-service-worker')
        for service in services:
            print(f'--> Deploying service {service} (cluster tutoken-staging-transaction-service)')
            ecs_client.update_service(
                cluster='tutoken-staging-transaction-service',
                service=service,
                forceNewDeployment=True,
            )


def deploy_admin():
    print('--> Deploying admin')
    ecs_client.update_service(
        cluster='admin',
        service='transaction-service-admin',
        forceNewDeployment=True,
    )


if __name__ == '__main__':
    cli()
