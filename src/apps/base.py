import logging.config
import pkgutil
from importlib import import_module

from flask import Flask, current_app, request
from flask_babel import Babel
from opentelemetry.instrumentation.flask import FlaskInstrumentor

from extensions.cassandra_cql import CassandraCqlClient
from extensions.project_config import get_config

babel = Babel(default_locale="en", configure_jinja=False)


@babel.localeselector
def get_locale():
    """Get local from Accept-Languages header"""
    return request.accept_languages.best_match(
        current_app.config["LANGUAGES"].keys()
    )


def create_app(config_name: str = None) -> Flask:
    """Create Flask APP"""
    config = get_config(config_name)
    logging.config.dictConfig(config.log_config())
    app = Flask(config.SERVICE_NAME)
    app.config.from_object(config)

    # 注册组件
    FlaskInstrumentor().instrument_app(app)

    babel.init_app(app)

    # 需要先初始化 traceing，所以延迟 import cassandra
    from extensions.cassandra_orm import CassandraSessionBuilder

    CassandraSessionBuilder(app).register_cassandra_session()
    CassandraCqlClient(app).register_cassandra_cql()

    # 导入所有的子模块
    for module in pkgutil.iter_modules(["apps"]):
        if module.ispkg is False:
            continue
        sub_app = import_module(f"apps.{module.name}")
        for blueprint in sub_app.blueprints:
            app.register_blueprint(blueprint)
        app.logger.info(f"Imported app: {module.name}")
    return app
