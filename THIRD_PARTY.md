# Локальные библиотеки

Файлы включены в `app/static/vendor` и раздаются самим FastAPI.
Установка через Node.js/npm не требуется.

| Библиотека | Версия | Лицензия | Источник файлов |
|---|---|---|---|
| Tabler Core | 1.4.0 | MIT | @tabler/core: dist/css/tabler.min.css, dist/css/tabler-vendors.min.css, dist/js/tabler.min.js |
| Bootstrap (внутри Tabler JS) | 5.3.7 | MIT | включён в tabler.min.js |
| HTMX | 2.0.11 | 0BSD | htmx.org: dist/htmx.min.js |
| Chart.js | 4.5.1 | MIT | chart.js: dist/chart.umd.min.js |
| Tom Select | 2.4.3 | Apache-2.0 | tom-select: dist/js/tom-select.complete.min.js, dist/css/tom-select.bootstrap5.min.css |
| Litepicker | 2.0.12 | MIT | litepicker: dist/litepicker.js (стили включены в JS) |

Вендорные дистрибутивы получены из соответствующих версий пакетов через jsDelivr
при сборке этой поставки. Готовое приложение не обращается к jsDelivr или npm.
Файлы лицензий находятся рядом с библиотеками; исходные заголовки сохранены.
В шаблонах используется небольшой набор встроенных SVG-иконок.
