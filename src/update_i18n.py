#!/usr/bin/env python3
import importlib
import os

import pip


def install(package):
    if hasattr(pip, "main"):
        pip.main(["install", package])
    else:
        pip._internal.main(["install", package])


install("zhconv")
zhconv = importlib.import_module("zhconv")


# 解决 MacOS 大小写不敏感
def git_rename(old_path, new_path):
    run(f"git mv {old_path} {old_path}.tmp")
    run(f"git mv {old_path}.tmp {new_path}")


def run(cmd):
    print("> ", cmd)
    os.system(cmd)


def chinese_to_simple_chinese():
    with open("i18n/translations/zh/LC_MESSAGES/messages.po") as zh:
        zh_content = zh.read()
        # 将翻译第一行以后的找出来
        zh_translation = "#: %s" % zh_content.split("#: ", 1)[1]

    with open("i18n/translations/zh_Hans/LC_MESSAGES/messages.po") as zh_hans:
        zh_hans_content = zh_hans.read()
        zh_hans_header = zh_hans_content.split("#: ", 1)[0]
        zh_hans_translation = zhconv.convert(zh_translation, "zh-hans")

    with open(
        "i18n/translations/zh_Hans/LC_MESSAGES/messages.po", "w"
    ) as zh_hant_new:
        zh_hant_new.write(zh_hans_header + zh_hans_translation)

    print("simple chinese done")


def chinese_simple_to_traditional():
    with open("i18n/translations/zh/LC_MESSAGES/messages.po") as zh:
        zh_content = zh.read()
        # 将翻译第一行以后的找出来
        zh_translation = "#: %s" % zh_content.split("#: ", 1)[1]

    with open("i18n/translations/zh_Hant/LC_MESSAGES/messages.po") as zh_hant:
        zh_hant_content = zh_hant.read()
        zh_hant_header = zh_hant_content.split("#: ", 1)[0]
        zh_hant_translation = zhconv.convert(zh_translation, "zh-hant")

    with open(
        "i18n/translations/zh_Hant/LC_MESSAGES/messages.po", "w"
    ) as zh_hant_new:
        zh_hant_new.write(zh_hant_header + zh_hant_translation)

    print("tranditional chinese done")


run("mkdir -p i18n/translations")

with open("i18n/babel.cfg", "w") as f:
    f.writelines(["[python: **.py]"])

# 创建新的语言
# 中文（默认是简体中文)
if not os.path.exists("i18n/translations/zh"):
    run("pybabel init -i i18n/messages.pot -d i18n/translations -l zh")

# 简体中文
if not os.path.exists("i18n/translations/zh_Hans"):
    run("pybabel init -i i18n/messages.pot -d i18n/translations -l zh_Hans")

# 繁体中文
if not os.path.exists("i18n/translations/zh_Hant"):
    run("pybabel init -i i18n/messages.pot -d i18n/translations -l zh_Hant")

print("抓取语言模版")
run("pybabel extract -F i18n/babel.cfg -o i18n/messages.pot .")

print("更新翻译")
run("pybabel update -i i18n/messages.pot -d i18n/translations")

# 使用简体中文翻译成繁体中文
chinese_simple_to_traditional()

chinese_to_simple_chinese()

print("编译翻译")
run("pybabel compile -d i18n/translations")

#  产生 fatal: bad source 不影响程序运行
git_rename("i18n/translations/zh_hans", "i18n/translations/zh_Hans")
git_rename("i18n/translations/zh_hant", "i18n/translations/zh_Hant")
