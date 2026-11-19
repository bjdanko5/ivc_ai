---
type: project
project: ivc_ai
created: 2026-11-19
updated: 2026-11-19
---

# Эксплуатация сайта-руководства

## Запуск и остановка
```bat
py -3 C:\ivc_ai\tools\run_wiki_lan.py
```
- Адрес: http://192.168.11.218:4000 (порт может сдвинуться - лаунчер печатает фактический).
- Остановка: Ctrl+C в окне лаунчера. Повторный запуск безопасен (retry-цикл внутри).
- Доступ: только LAN, наружу не публикуется.

## Контент и конфиг
- Контент: 20_Knowledge/Server_Setup/docs (01-10 + index). Источник правды по командам - 07.
- Конфиг: 20_Knowledge/Server_Setup/mkdocs.yml. Меню = блок nav; новая заметка = строка в nav.
- Live reload: правки md подхватываются сами; после массовых перезаписей скриптом - перезапустить лаунчер.

## Траблы
- WinError 10013 на bind: динамическое резервирование портов Windows; лаунчер сам повторит/сдвинет порт. Постоянно - netsh int ipv4 show excludedportrange protocol=tcp, выбрать порт вне диапазонов.
- Баннер Material for MkDocs про EOL 2027 - информационный, игнорировать.
- WARNING про nav-файл: файла нет в docs/ или имя в nav отличается; сверить.

## Коммит
```bat
py -3 C:\ivc_ai\tools\ivc_git_sync.py -m "site: ..." --push
```

## Связи
- [[vault_map]]
- [[chat_playbook]]
- [[07_Automation_Scripts]]

