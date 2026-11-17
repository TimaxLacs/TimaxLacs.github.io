# Тимур Шакиров — резюме

Fullstack-разработчик. Языковые модели в продуктовых системах. Санкт-Петербург, удалённо.

**Резюме онлайн: [timaxlacs.github.io/v2](https://timaxlacs.github.io/v2/)**
&nbsp;·&nbsp; [PDF, русский](https://timaxlacs.github.io/resume.pdf)
&nbsp;·&nbsp; [PDF, English](https://timaxlacs.github.io/resume.en.pdf)

*Timur Shakirov: fullstack developer, language models inside production systems. The résumé is bilingual: use the RU / EN switch on the page.*

## Что на странице

| Раздел | Содержание |
|---|---|
| Шапка | статус «Открыт к предложениям», кнопки PDF / GitHub / контакты, 12 цифр |
| Кратко | чем занимаюсь, образование, результаты в цифрах |
| Опыт | диаграмма по годам, фильтр по роли (ИИ, Fullstack, Backend, DevOps), подробные записи: e-commerce платформа, ManyAir, Matreshka, Deep.Assistant, Deep.Foundation, ПК-стенд GLASAT и аналитика для ЦППК, сайты |
| Путь | хронология 2019–2026 |
| Проекты | витрина из трёх репозиториев и 26 карточек с фильтрами по категории и языку |
| Пакеты и голос | npm-пакеты с загрузками, голосовой стек InnerEcho |
| Организации | Deep.Foundation и три аккаунта GitHub |
| Активность | вклады по годам (линейная и логарифмическая шкала), календарь за год, состав вкладов, код по языкам |
| Инструменты | стек по 11 группам |
| Метод | как я работаю с языковыми моделями |
| Знания | образование, языки, навыки, что не взлетело |
| Контакты | почта, Telegram, GitHub, npm, продукты |

Есть светлая и тёмная темы (переключатель ◐), печатная версия и превью для ссылок.

## Устройство

Страница статическая: один HTML-файл без фреймворков и сборщика, шрифты подключаются с Google Fonts.

```
v2/
├── index.html    страница целиком: разметка, стили, скрипт
├── portrait.jpg  портрет
└── og.png        превью для ссылок
tools/
├── build_v2.py       генератор: собирает v2/index.html
├── template_v2.html  шаблон страницы (стили и скрипт)
├── gh_data.json      снимок публичных данных GitHub на 2026-11-17
└── og.html           исходник превью
resume.pdf, resume.en.pdf   PDF версии, печатаются из этой же страницы
```

Правки текста вносятся в `tools/build_v2.py`, оформления в `tools/template_v2.html`. Сборка:

```bash
python3 -I tools/build_v2.py
```

Посмотреть локально:

```bash
cd v2 && python3 -m http.server 8000
```

После этого страница открывается на `http://localhost:8000`. Параметр `?lang=en` включает английскую версию.

PDF печатаются из страницы через Chrome:

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --no-pdf-header-footer \
  --virtual-time-budget=9000 --print-to-pdf=resume.pdf "http://localhost:8000/?lang=ru"
```

## Публикация

Сайт выкладывается через GitHub Pages. Любой пуш в `main` запускает workflow [`pages.yml`](.github/workflows/pages.yml), который публикует репозиторий целиком. Страница резюме доступна по адресу `/v2/`.

## Откуда цифры

- Звёздочкой `*` на странице отмечены цифры из публичных данных GitHub и npm на 2026-11-17. Значительная часть работы лежит в закрытых репозиториях заказчиков, поэтому публичный граф показывает её лишь частично.
- Остальные цифры взяты из описаний проектов и проверены по коду: например, 37 моделей в LLM-шлюзе посчитаны по его конфигурации.
