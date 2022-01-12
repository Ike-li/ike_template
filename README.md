# ike_template

## 说明
使用 poetry 进行包管理，用法类似 npm/yarn:
```bash
# 安装依赖库
$ poetry install

# 添加库
$ poetry add flask

# 移除库
$ poetry remove flask
```

## Commands
添加新的模块，会自动创建包和测试文件:
```bash
python manage.py add example
```

## 如何配置.drone.yaml文件
1. 配置 `.project_config/project_config.yaml` 中的 drone 需要启动的 service
2. 运行 setup_config.py 脚本生成 `.drone.yml` 文件

## 如何生成翻译文件
```bash
# 生成初始的文件
pybabel extract -F i18n/babel.cfg -o i18n/messages.pot .

# 初始化需要翻译的语言
pybabel init -i i18n/messages.pot -d i18n/translations -l zh

# 如果已经初始化了, 直接更新翻译
pybabel update -i i18n/messages.pot -d i18n/translations

# 编译文件
pybabel compile -d i18n/translations
```

PS.
1. 修改 i18n 相关 string 后可以直接运行 update_i18n.sh
2. 不要手动修改 messages.pot 文件
3. 在上下文之外的地方定义的 i18n string, 需要使用 `lazy_gettext` 函数, 参考 `extensions/flask_api/exceptions.py`

## Jaeger host

http://localhost:16686/

## 使用日志
```python
import logging

logger = logging.getLogger(__name__)

logger.info('did something')
# > [2020-10-12 16:11:09 +0800] [14096] [INFO] did something

logger.error('some error')
# > [2020-10-12 16:11:09 +0800] [14096] [ERROR] some error

try:
    raise Exception
except Exception as e:
    logger.error('some exception', exc_info=True)

# >
# exc_info=True 打印完整的异常栈信息
# [2020-10-12 16:11:09 +0800] [14096] [ERROR] some exception
# Traceback (most recent call last):
#   File "C:/Users/xx/xx/xx.py", line 57, in <module>
#     raise Exception
# Exception

```
