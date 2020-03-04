# Kraken

Deploy your projects to k8s cluster with ease! (maybe)

### Development

Создать новую virtualenv

```bash
virtualenv venv
```

---------------

Активировать venv и установить проект локально
```bash
. venv/bin/activate
pip3 install --editable .
```

После этого можно использовать в консоли

```bash
kraken --help
```

---------------

По окончанию работы, для выхода из текущей virtualenv

```bash
deactivate
```

---------------

Запуск тестов:

```bash
pytest
```