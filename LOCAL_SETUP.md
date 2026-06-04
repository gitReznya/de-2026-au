# Локальная работа с репозиторием

## Клонирование

```bash
git clone https://github.com/gitReznya/de-2026-au.git
cd de-2026-au
```

## Проверка структуры

```bash
find . -maxdepth 3 -type f | sort
```

## Проверка shell-файлов

```bash
find . -name "*.sh" -print -exec bash -n {} \;
```

## Запуск калькулятора подсетей

```bash
python3 scripts/calc_subnets.py
```

## Как адаптировать под другой вариант

1. Открой `TABLES.md`.
2. Замени VLAN/IP/порты/домен.
3. Открой `prompts/ip-calc-prompt.md` и пересчитай адресацию.
4. Открой `prompts/variant-adapter-prompt.md` и адаптируй команды.
5. Проверь команды на стенде.

## Важное

Не запускай `.sh` файлы на рабочей системе. Это команды для лабораторного стенда ДЭ.
