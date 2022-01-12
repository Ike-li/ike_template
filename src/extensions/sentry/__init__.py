"""
从环境变量中读取
SENTRY_ENVIRONMENT
SENTRY_DSN
配置
"""
import raven


def initialize_sentry_client():
    return raven.Client(enable_breadcrumbs=False)


sentry = initialize_sentry_client()
