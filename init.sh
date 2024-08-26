#!/bin/bash

# Скрипт для установки TTL на все ключи
while true; do
    keys=$(redis-cli --scan)
    for key in $keys; do
        redis-cli expire $key 172800 # 172800 секунд = 2 дня
    done
    sleep 60  # Запуск скрипта каждые 60 секунд
done