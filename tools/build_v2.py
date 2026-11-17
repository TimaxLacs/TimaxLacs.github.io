#!/usr/bin/env python3
"""Builds v2/index.html (static, RU/EN) from tools/template_v2.html and tools/gh_data.json.

    python3 -I tools/build_v2.py
"""
import datetime, html, json, math, os, sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TPL = os.path.join(ROOT, "tools", "template_v2.html")
DATA = os.path.join(ROOT, "tools", "gh_data.json")
OUT = os.path.join(ROOT, "v2", "index.html")
SNAP = "2026-11-17"

gh = json.load(open(DATA, encoding="utf-8"))

def e(s): return html.escape(s, quote=False)
def T(ru, en): return '<span data-l="ru">%s</span><span data-l="en">%s</span>' % (ru, en)
def fmt(n): return "{:,}".format(n).replace(",", " ")
AST = '<sup class="ast">*</sup>'

GH = "https://github.com/TimaxLacs/"
GHH = "https://github.com/TimaxHack/"
PAGES = "https://timaxlacs.github.io/"

# ---------- derived GitHub numbers ----------
yl, yh = gh["years_lacs"], gh["years_hack"]
all_years = sorted(set(yl) | set(yh))
def ysum(y, k): return yl.get(y, {}).get(k, 0) + yh.get(y, {}).get(k, 0)
YEARS = [(y, ysum(y, "total")) for y in all_years if ysum(y, "total") > 0]
tot = {k: sum(ysum(y, k) for y in all_years) for k in ("total", "commits", "pull_requests", "issues", "reviews")}
repos = [r for acc in gh["repos"].values() for r in acc]
n_repos = len(repos)
stars = sum(r["stargazers_count"] for r in repos)
lang_repo = Counter(r["language"] for r in repos if r["language"])
MARKUP = {"HTML", "CSS", "Roff", "Mako"}
code_bytes = {k: v for k, v in gh["lang_bytes_total"].items() if k not in MARKUP}
n_langs = len(gh["lang_bytes_total"])

# ---------- stats ----------
STATS = [
    ("5", T("лет в разработке", "years in development"), T("с 2021 года", "since 2021"), False),
    ("37", T("моделей за одним API", "models behind one API"), T("6 подключений поставщиков", "6 provider connections"), False),
    ("4", T("коммерческих проекта", "commercial projects"), T("с 2024 года", "since 2024"), False),
    ("8", T("сервисов в платформе", "services in one platform"), T("e-commerce, под NDA", "e-commerce, under NDA"), False),
    (str(n_repos), T("публичных репозиториев", "public repositories"), T("2 аккаунта, без форков", "2 accounts, no forks"), True),
    ("8", T("собственных пакетов в npm", "own npm packages"), T("и 148 в scope Deep.Foundation", "plus 148 in the Deep.Foundation scope"), True),
    (str(gh["org_deep"]["public_repos"]), T("репозиториев в Deep.Foundation", "repositories in Deep.Foundation"), T("организация, участник с 2022", "organisation, member since 2022"), True),
    (fmt(tot["total"]), T("вклада на GitHub", "GitHub contributions"), T("2 аккаунта, 2019–2026", "2 accounts, 2019–2026"), True),
    (fmt(tot["commits"]), T("коммитов", "commits"), T("публичный граф", "public graph"), True),
    (str(tot["pull_requests"] + tot["issues"]), T("PR и issues", "PRs and issues"), T("открыл в публичных репозиториях", "opened in public repositories"), True),
    (str(n_langs), T("языков в репозиториях", "languages in repositories"), T("по определению GitHub", "as detected by GitHub"), True),
    ("3", T("аккаунта на GitHub", "GitHub accounts"), T("основной TimaxLacs", "main one is TimaxLacs"), False),
]
def stat(n, label, sub, ast):
    return '<div class="stat"><b>%s%s</b><span>%s</span><small>%s</small></div>' % (n, AST if ast else "", label, sub)
STATS_HTML = "".join(stat(*s) for s in STATS)
STATSNOTE = T("(*) по публичным данным GitHub и npm на %s. Остальные цифры из описаний проектов и конфигурации кода." % SNAP,
              "(*) from public GitHub and npm data as of %s. The other figures come from project descriptions and source configuration." % SNAP)

# ---------- results ----------
RESULTS = [
    T("<b>37 моделей</b> в LLM-шлюзе, у каждой цепочка из 12–16 замен: недоступность одного поставщика не останавливает продукт.",
      "<b>37 models</b> in the LLM gateway, each with a chain of 12–16 replacements: one provider going down does not stop the product."),
    T("<b>Коэффициенты от 1.7 до 40</b> переводят токены разных моделей в одну внутреннюю валюту: считаются себестоимость запроса и наценка.",
      "<b>Coefficients from 1.7 to 40</b> convert tokens of different models into one internal currency: request cost and margin are computed."),
    T("<b>Новые модели за дни:</b> o1-preview и o1-mini подключены 27.09.2024, deepseek-reasoner 30.01.2025, сразу с тарификацией и фолбэком.",
      "<b>New models within days:</b> o1-preview and o1-mini went live on 27 Sep 2024, deepseek-reasoner on 30 Jan 2025, with billing and fallback from day one."),
    T("<b>8 сервисов</b> в e-commerce платформе, интерфейс на двух языках, три картографических поставщика за одним интерфейсом.",
      "<b>8 services</b> in the e-commerce platform, a bilingual interface, three map providers behind one interface."),
    T("<b>До трёх кругов правок</b> в контент-конвейере: вторая модель проверяет первую отдельным вызовом, состояние переживает падение.",
      "<b>Up to three revision rounds</b> in the content pipeline: a second model reviews the first in a separate call, state survives a crash."),
    T("<b>29 тестовых файлов</b> в tg-runner-orchestrator: оркестратор ботов на конечном автомате с Redis, лицензия MIT.",
      "<b>29 test files</b> in tg-runner-orchestrator: a bot orchestrator on a state machine with Redis, MIT licensed."),
]
RESULTS_HTML = '<div class="results"><h4 class="cap">%s</h4><ul>%s</ul></div>' % (
    T("Результаты в цифрах", "Results in numbers"), "".join("<li>%s</li>" % r for r in RESULTS))

# ---------- jobs ----------
ROLES = [("all", T("Всё", "All")), ("ai", T("ИИ и LLM", "AI and LLM")), ("fullstack", "Fullstack"),
         ("backend", "Backend"), ("devops", "DevOps")]

JOBS = [
    dict(roles="fullstack backend ai", when=T("дек 2025 — н. в.", "Dec 2025 — now"),
         title=T("E-commerce платформа", "E-commerce platform"),
         role=T("Фронтенд, гео-модуль, мобильные сборки, смежный бэкенд · контракт · под NDA",
                "Frontend, geo module, mobile builds, adjacent backend · contract · under NDA"),
         lead=T("Маркетплейс с каталогом и картами. Веду клиентское приложение, участвую в проектировании; на бэкенде — платежи, баланс, обработчики событий. Детали продукта под NDA, о модулях рассказываю свободно.",
                "A marketplace with a catalog and maps. I lead the client app and take part in design; on the backend I own payments, balance and event handlers. Product details are under NDA, but I can talk about the modules freely."),
         bullets=[
             T("<b>Витрина:</b> каталог, карточка товара, поиск с автодополнением, фильтры, регистрация нескольких типов аккаунтов с MFA, библиотека UI-компонентов.",
               "<b>Storefront:</b> catalog, product page, search with autocomplete, filters, sign-up for several account types with MFA, a UI component library."),
             T("<b>Двуязычность RU/EN и автоперевод карточек:</b> словари вынесены из компонентов, перевод идёт через хук, серверный роут и CLI-скрипт, который прогоняет каталог пачкой.",
               "<b>RU/EN and auto-translation of cards:</b> dictionaries moved out of components; translation goes through a hook, a server route and a CLI script that runs the catalog in batches."),
             T("<b>Конвейер наполнения каталога:</b> источники за общим контрактом, дедупликация по внешнему id, штрихкоду и отпечатку характеристик. Нейросети работают после сбора, отдельными очередями для текста и изображений. Факты карточки модель не переписывает, иначе ломается дедупликация; упавший воркер оставляет товар на витрине с исходными данными.",
               "<b>Catalog ingestion pipeline:</b> sources behind a common contract, deduplication by external id, barcode and a characteristics fingerprint. Models run after collection, in separate queues for text and images. A model never rewrites card facts, otherwise deduplication breaks; a failed worker leaves the item on the storefront with its original data."),
             T("<b>Кошелёк и заказы:</b> сервисы баланса и платежей, внешний эквайринг, обработчики смены статуса. Жалобы и блокировки для пользовательского контента, миграция базы на PostGIS, смоук-тесты. Сборки Capacitor под iOS и Android, выкладка через Docker и systemd.",
               "<b>Wallet and orders:</b> balance and payment services, external acquiring, status-change handlers. Complaints and blocks for user-generated content, a database migration to PostGIS, smoke tests. Capacitor builds for iOS and Android, deployment via Docker and systemd."),
             T("<b>Гео-модуль:</b> единый интерфейс поверх Яндекс.Карт, Google Maps и 2ГИС; смена поставщика — один параметр. Геометрия зон: буферы вдоль маршрута со сглаженными переходами (кривые Безье), объединение полигонов с отверстиями, валидация, кэширование. Геокодинг на серверном роуте, чтобы ключи не попадали в браузер; PostGIS, поиск по радиусу; документация по выносу модуля в самостоятельное приложение.",
               "<b>Geo module:</b> one interface over Yandex Maps, Google Maps and 2GIS; switching provider is a single setting. Zone geometry: route buffers with smooth transitions (Bézier curves), polygon union with holes, validation, caching. Geocoding on a server route so keys never reach the browser; PostGIS, radius search; documentation for extracting the module into a standalone app."),
         ],
         tags=["React", "TypeScript", "Hasura GraphQL", "PostgreSQL / PostGIS", "Redis", "MinIO", "Docker", "Capacitor"]),

    dict(roles="fullstack backend devops", when=T("авг 2025 — май 2026", "Aug 2025 — May 2026"),
         title=T("ManyAir — международные переводы", "ManyAir — international transfers"),
         role=T("Фронтенд, смежный бэкенд и сервер · проект заказчика", "Frontend, adjacent backend and server · client project"),
         lead=T("Платформа для управления международными денежными переводами, монорепозиторий на TypeScript.",
                "A platform for managing international money transfers, a TypeScript monorepo."),
         bullets=[
             T("Микросервисы вокруг Hasura GraphQL: router, обработчик событий, рассылка, Telegram-бот, генератор документов, курсы валют.",
               "Microservices around Hasura GraphQL: router, event handler, mailing, Telegram bot, document generator, exchange rates."),
             T("<b>Устойчивая доставка уведомлений:</b> при недоступном канале статус возвращает «не отправлено», приглашение не помечается доставленным.",
               "<b>Resilient notification delivery:</b> when a channel is down the status returns “not sent” and the invitation is never marked as delivered."),
             T("<b>Изоляция данных между ролями:</b> сброс кэша запросов при смене пользователя, ограничение подписок на детали сделки.",
               "<b>Data isolation between roles:</b> the query cache is reset when the user changes, subscriptions to deal details are restricted."),
             T("<b>Вывод из системы устаревшего домена приглашений:</b> таблицы, права Hasura, роуты, обработчики, сгенерированные типы. Покрытие e2e-тестами, скрипты генерации HTML-гайдов и тестовой документации.",
               "<b>Retiring a legacy invitations domain:</b> tables, Hasura permissions, routes, handlers, generated types. E2E test coverage, scripts that generate HTML guides and test documentation."),
             T("Выкладка сервисов, разбор сбоев, настройка почты и DNS.", "Service deployment, incident analysis, mail and DNS setup."),
         ],
         tags=["TypeScript", "React", "Hasura", "PostgreSQL", "Redis", "MinIO", "Playwright", "Docker"]),

    dict(roles="fullstack devops", when="2026",
         title=T('<a href="https://matreshka.club" target="_blank" rel="noopener">Matreshka</a> — публичный сайт', '<a href="https://matreshka.club" target="_blank" rel="noopener">Matreshka</a> — public website'),
         role=T("Фронтенд и запуск · тот же заказчик", "Frontend and launch · same client"),
         lead=T("Публичный сайт AI/e-commerce платформы: React, Vite, TypeScript, Tailwind, фирменный стиль. nginx с SSL, DNS и почта на домене.",
                "Public website of an AI/e-commerce platform: React, Vite, TypeScript, Tailwind, brand styling. nginx with SSL, DNS and domain mail."),
         bullets=[], tags=["React", "Vite", "Tailwind", "shadcn/ui", "nginx", "SSL"]),

    dict(roles="ai backend devops", when="2024 — 2025",
         title=T("Deep.Assistant — агрегатор нейросетей", "Deep.Assistant — an AI aggregator"),
         role=T("Основатель, backend и DevOps · команда из трёх человек", "Founder, backend and DevOps · a team of three"),
         lead=T('Коммерческий продукт: чат с моделями, генерация изображений, музыки и голоса, API-шлюз, мини-приложения в Telegram и VK. Бот: <a href="https://t.me/DeepGPTBot" target="_blank" rel="noopener">@DeepGPTBot</a>, канал <a href="https://t.me/gptDeep" target="_blank" rel="noopener">@gptDeep</a> — 1 553 подписчика.',
                'A commercial product: chat with models, image, music and voice generation, an API gateway, Telegram and VK mini-apps. Bot: <a href="https://t.me/DeepGPTBot" target="_blank" rel="noopener">@DeepGPTBot</a>, channel <a href="https://t.me/gptDeep" target="_blank" rel="noopener">@gptDeep</a> — 1,553 subscribers.'),
         bullets=[
             T("<b>LLM-шлюз.</b> Спроектировал и написал первую версию; шлюз вырос из личного репозитория в инфраструктуру всех запросов продукта. Около 37 моделей через шесть подключений поставщиков за одним OpenAI-совместимым интерфейсом. Основной автор: HTTP-сервер, конфигурация моделей, менеджер токенов, слой работы с базой.",
               "<b>LLM gateway.</b> I designed and wrote the first version; it grew from a personal repository into the infrastructure behind every request in the product. About 37 models through six provider connections behind one OpenAI-compatible interface. Main author: HTTP server, model configuration, token manager, the database layer."),
             T("<b>Таблица деградации вместо простого ретрая:</b> у каждой модели цепочка из 12–16 замен, подобранных так, чтобы ответ оставался пригодным для того же сценария.",
               "<b>A degradation table instead of a plain retry:</b> every model has a chain of 12–16 replacements chosen so the answer stays usable for the same scenario."),
             T("<b>Единый счёт поверх несопоставимых прайсов:</b> у каждой модели свой коэффициент пересчёта токенов во внутреннюю валюту, от 1.7 до 40.",
               "<b>One balance over incomparable price lists:</b> every model has its own coefficient converting tokens to the internal currency, from 1.7 to 40."),
             T("<b>Идемпотентные переводы между счетами:</b> эксклюзивные блокировки с распознаванием зависших, атомарная запись с обратной вычиткой, восстановление незавершённых операций при старте.",
               "<b>Idempotent transfers between accounts:</b> exclusive locks that recognise stale ones, atomic writes with read-back, recovery of unfinished operations on startup."),
             T("<b>Скорость подключения моделей:</b> o1-preview и o1-mini — 27 сентября 2024, deepseek-reasoner — 30 января 2025, сразу с тарификацией и фолбэком.",
               "<b>Speed of onboarding models:</b> o1-preview and o1-mini on 27 Sep 2024, deepseek-reasoner on 30 Jan 2025, each with billing and fallback from day one."),
             T("<b>Telegram-бот (aiogram):</b> переводы внутренней валюты на конечном автомате (модуль с нуля: получатель, сумма, подтверждение, история); синхронизация пользователей с ограничением параллелизма под лимиты Telegram; транскрибация аудио с отдельным коэффициентом тарификации.",
               "<b>Telegram bot (aiogram):</b> internal-currency transfers on a state machine (a module from scratch: recipient, amount, confirmation, history); user sync with bounded concurrency for Telegram limits; audio transcription with its own billing coefficient."),
             T("<b>Поведение в групповых чатах:</b> ответ только на обращения к боту, разбор упоминаний в подписях к фото и документам, выгрузка истории диалога файлом. Оплата через Telegram Stars, окружения TEST и PROD, асинхронные проверки доступности провайдеров.",
               "<b>Group-chat behaviour:</b> replies only when addressed, mentions parsed in photo and document captions, dialog history exported as a file. Telegram Stars payments, TEST and PROD environments, asynchronous provider health checks."),
         ],
         tags=["Node.js", "Express", "Python", "aiogram", "OpenAI API", "OpenRouter", "DeepSeek", "Docker"]),

    dict(roles="ai backend", when=T("2022 — н. в.", "2022 — now"),
         title=T('<a href="https://github.com/deep-foundation" target="_blank" rel="noopener">Deep.Foundation</a> — open source', '<a href="https://github.com/deep-foundation" target="_blank" rel="noopener">Deep.Foundation</a> — open source'),
         role=T("Участник организации", "Organisation member"),
         lead=T("Экосистема ассоциативного хранилища, где единственная сущность — связь: кортеж из идентификатора, типа и ссылок на другие связи. Одной таблицей описываются и данные, и схема, и обработчики.",
                "An ecosystem around associative storage where the only entity is a link: a tuple of an id, a type and references to other links. One table describes data, schema and handlers."),
         bullets=[
             T("<b>deep-files-sync</b> (13 версий): проецирует граф связей на файловую систему, содержимое базы читается и правится через grep, редактор и git. Правки синхронизируются в обе стороны, удаление файла означает отписку.",
               "<b>deep-files-sync</b> (13 releases): projects the link graph onto the file system, so database content can be read and edited with grep, an editor and git. Edits sync both ways; deleting a file means unsubscribing."),
             T("<b>Пакеты ИИ-тулинга в официальном скоупе:</b> <code>@deep-foundation/ai</code>, <code>ai-models</code>, <code>ai-templates</code>, <code>ai-tasks</code>, <code>4o-bot</code>, <code>chatgpt-azure-deep</code>, <code>function_generation</code>, <code>tests_generation</code>. Такой пакет — не библиотека, а выгрузка настроенного графа связей, которая разворачивается в чужом инстансе.",
               "<b>AI tooling packages in the official scope:</b> <code>@deep-foundation/ai</code>, <code>ai-models</code>, <code>ai-templates</code>, <code>ai-tasks</code>, <code>4o-bot</code>, <code>chatgpt-azure-deep</code>, <code>function_generation</code>, <code>tests_generation</code>. Such a package is not a library but an export of a configured link graph that deploys into someone else's instance."),
             T("<b>Диалоги бота как граф:</b> запись переписки в ассоциативное хранилище, диалог, сообщение, автор и ответ выражены типами связей. Решение прожило в проде около шести недель и было заменено файловым хранилищем: сложность не окупилась.",
               "<b>Bot dialogs as a graph:</b> conversations stored in the associative store, with dialog, message, author and reply expressed as link types. It lived in production for about six weeks and was replaced by file storage: the complexity did not pay off."),
             T("Соавтор русскоязычной теоретической документации (около 1 000 строк) и метатеории связей; завёл порядка 36 issue, в основном баг-репорты по развёртыванию платформы с трейсбеками.",
               "Co-author of the Russian theory documentation (about 1,000 lines) and of the links meta-theory; filed around 36 issues, mostly deployment bug reports with tracebacks."),
         ],
         tags=["JavaScript", "TypeScript", "npm", "GraphQL", "Hasura"]),

    dict(roles="fullstack backend ai", when="2026",
         title=T("ЦППК: ПК-стенд GLASAT и аналитика", "CPPK: the GLASAT desktop bench and analysis"),
         role=T("Разработка и исследования · для ЦППК · закрытый репозиторий", "Development and research · for CPPK · private repository"),
         lead=T("ПК-стенд для анализа записей по методике Когана–Вольвача (двигатель и холтер): загрузка WAV и HDF, расчёт, отчёты. Это не клинический сервис. Рядом аналитические материалы и макеты.",
                "A desktop bench that analyses recordings with the Kogan–Volvach method (engine and Holter): WAV and HDF input, calculation, reports. It is not a clinical service. Alongside it, analytical materials and mock-ups."),
         bullets=[
             T("<b>GLASAT:</b> Python 3.11, интерфейс на NiceGUI, графики Plotly, библиотека данных на SQLite, тесты на pytest. Упаковка в передаваемый архив через PyInstaller и команду <code>glasat pack</code>.",
               "<b>GLASAT:</b> Python 3.11, a NiceGUI interface, Plotly charts, a SQLite data library, pytest tests. Packaged into a transferable archive via PyInstaller and the <code>glasat pack</code> command."),
             T('<b>Аналитика:</b> обзор проекта по выгрузке рабочего чата (методика, ЭКГ, рынок), внутренняя карта ниш ЦППК СПб на статических страницах, <a href="https://timaxlacs.github.io/ai-bot-market-brief/" target="_blank" rel="noopener">«Семейный разбор»</a> рынка салонного ИИ-администратора.',
               '<b>Analysis:</b> a project review built from a work-chat export (method, ECG, market), an internal niche map for CPPK St Petersburg on static pages, a <a href="https://timaxlacs.github.io/ai-bot-market-brief/" target="_blank" rel="noopener">family-readable brief</a> on the salon AI-administrator market.'),
             T('<b>Макеты:</b> <a href="https://timaxlacs.github.io/avito/" target="_blank" rel="noopener">страница учебного центра Росавтодора на Авито</a>, публичный макет диагностики на фасаде cppkspb.ru.',
               '<b>Mock-ups:</b> an <a href="https://timaxlacs.github.io/avito/" target="_blank" rel="noopener">Avito page for a Rosavtodor training centre</a>, a public mock-up of diagnostics on the facade of cppkspb.ru.'),
         ],
         tags=["Python", "NiceGUI", "Plotly", "PyInstaller", "pytest", "SQLite", "Next.js"]),

    dict(roles="fullstack", when="2026",
         title=T("Сайты: организации и малый бизнес", "Websites: organisations and small business"),
         role=T("Разработка", "Development"),
         lead=T("Сайт Центра патриотического воспитания «Чкалов Парк» (React, TypeScript, Vite). Шаблон клиентских сайтов для малого бизнеса: Next.js и Payload CMS в одном процессе, локали hy / ru / en, деплой на один VPS через Docker.",
                "The website of a patriotic education centre, Chkalov Park (React, TypeScript, Vite). A template for small-business client sites: Next.js and Payload CMS in one process, hy / ru / en locales, deployed to a single VPS with Docker."),
         bullets=[], tags=["Next.js", "Payload CMS", "React", "Vite", "Docker"]),
]

# ---------- projects ----------
# (cat, year, name, desc_ru, desc_en, url, lang display, lang tokens)
PROJECTS = [
    ("ai", "2026", "Предложка", "Редакционный стол для сообществ: нейросети пишут и перепроверяют посты, материал проходит гейты, встаёт в слот и уходит в ВК, Telegram и MAX. Пять независимых частей с HTTP-контрактом.",
     "An editorial desk for communities: models write and re-check posts, the material passes gates, takes a slot and goes out to VK, Telegram and MAX. Five independent parts behind an HTTP contract.", None, "Python · TS", "python ts"),
    ("ai", "2026", "ai-post-generator", "Одна модель пишет черновик, вторая проверяет отдельным вызовом, замечания возвращаются на правку до трёх кругов. Состояние в SQLite переживает падение процесса.",
     "One model drafts, a second reviews in a separate call, remarks go back for up to three rounds. State lives in SQLite and survives a crash.", GH + "ai-post-generator", "Python", "python"),
    ("ai", "2026", "lightrag-mcp", "MCP-сервер к self-hosted LightRAG: режимы поиска, реранкинг, ответы со ссылками, конфигурация проверяется через zod. Подключён к рабочему редактору как постоянная память по проектам.",
     "An MCP server for self-hosted LightRAG: search modes, reranking, answers with citations, config validated with zod. Connected to my editor as persistent project memory.", GH + "lightrag-mcp", "JavaScript", "js"),
    ("ai", "2026", "cursor-agent-workflows", "Около 1 900 строк спецификаций агентных процессов: конвейер безопасного изменения кода из пяти агентов с запечатанными границами задачи, бутстрап проекта, процесс исследования.",
     "About 1,900 lines of agent-workflow specs: a safe code-change pipeline of five agents with sealed task boundaries, project bootstrap, a research process.", GH + "cursor-agent-workflows", "Markdown", "md"),
    ("ai", "2025", "test-resorning", "Reasoning-конвейер поверх обычных чат-моделей: предсказание намерения, пошаговое решение, состязательная критика, доработка, синтез; вариант на LangChain с Tree of Thoughts.",
     "A reasoning pipeline on top of ordinary chat models: intent prediction, step-by-step solving, adversarial critique, refinement, synthesis; a LangChain variant with Tree of Thoughts.", GH + "test-resorning", "Python", "python"),
    ("ai", "2025", "InnerEcho", "Локальный голосовой ассистент: распознавание речи, языковая модель, синтез с клонированием голоса, автонастройка аудиоустройств. Сравнение моделей синтеза на русском корпусе. Исследовательский прототип.",
     "A local voice assistant: speech recognition, a language model, voice-cloning synthesis, automatic audio-device setup. A comparison of synthesis models on a Russian corpus. A research prototype.", GH + "InnerEcho", "JavaScript · Python", "js python"),
    ("ai", "2025", "ai-lector", "Бот, который перерабатывает аудиолекции под нужный формат. Для обхода лимита на размер файла собран локальный Telegram Bot API server через cmake.",
     "A bot that reworks audio lectures into the format you need. A local Telegram Bot API server was built with cmake to get around the file-size limit.", GH + "ai-lector", "Python", "python"),
    ("ai", "2026", "GLASAT", "ПК-стенд анализа записей по методике Когана–Вольвача: NiceGUI, Plotly, SQLite, упаковка PyInstaller. Не клинический сервис.",
     "A desktop bench for analysing recordings with the Kogan–Volvach method: NiceGUI, Plotly, SQLite, PyInstaller packaging. Not a clinical service.", None, "Python", "python"),
    ("bots", "2026", "tg-runner", "Оркестрация Telegram-ботов: оркестратор на конечном автомате с Redis, воркер в Docker, публикуемый SDK и CLI. Docker Compose, pytest, документация. Четыре репозитория.",
     "Orchestration of Telegram bots: an orchestrator on a state machine with Redis, a Docker worker, a published SDK and a CLI. Docker Compose, pytest, docs. Four repositories.", GH + "tg-runner-orchestrator", "Python", "python"),
    ("bots", "2026", "vk-tg-parser", "Pip-пакет: единый парсер Telegram через MTProto и VK через API с общей моделью данных и мониторингом в реальном времени.",
     "A pip package: one parser for Telegram via MTProto and VK via API, with a shared data model and real-time monitoring.", GH + "vk-tg-parser", "Python", "python"),
    ("bots", "2026", "tg-hashtag-commenter", "Поиск публичных постов по хэштегам в Telegram и VK и комментирование с ограничением частоты и дедупликацией. Три файла: ядро, Telegram на Pyrogram, VK по HTTP API.",
     "Search for public posts by hashtag in Telegram and VK and commenting with rate limiting and deduplication. Three files: core, Telegram on Pyrogram, VK over the HTTP API.", GH + "tg-hashtag-commenter", "Python", "python"),
    ("bots", "2026", "max-bot", "Тестовый бот для мессенджера MAX: polling и webhook, мультимодальная обработка фото нейросетью, квота на пользователя, запасной сценарий при недоступности бэкенда.",
     "A test bot for the MAX messenger: polling and webhook, multimodal photo processing by a model, per-user quota, a fallback when the backend is down.", GH + "max-bot", "JavaScript", "js"),
    ("bots", "2025", "anti-cpam-ai", "Антиспам-бот: модель через OpenRouter выставляет сообщению спам-балл от 1 до 10.",
     "An anti-spam bot: a model via OpenRouter gives each message a spam score from 1 to 10.", GHH + "anti-cpam-ai", "Python", "python"),
    ("bots", "2026", "avtomatika-worker", "Worker SDK для оркестратора Avtomatika (организация avtomatika-ai).",
     "A Worker SDK for the Avtomatika orchestrator (the avtomatika-ai organisation).", GH + "avtomatika-worker", "Python", "python"),
    ("web", "2026", "chkalov-park", "Сайт Центра патриотического воспитания «Чкалов Парк» (Сиверский).",
     "The website of the Chkalov Park patriotic education centre.", GH + "chkalov-park", "TypeScript", "ts"),
    ("web", "2026", "diagnostika-fasad", "Публичный макет диагностики авто на фасаде cppkspb.ru.",
     "A public mock-up of car diagnostics on the facade of cppkspb.ru.", GH + "diagnostika-fasad", "HTML", "html"),
    ("web", "2026", "Макет Авито", "Страница учебного центра Росавтодора (СПб) на Авито: статичная страница с фото.",
     "An Avito page for a Rosavtodor training centre (St Petersburg): a static page with photos.", PAGES + "avito/", "HTML", "html"),
    ("web", "2026", "Семейный разбор", "Рыночный бриф: стоит ли строить салонного ИИ-администратора. Страницы про альтернативы, экономику, источники и методику; статический экспорт Next.js.",
     "A market brief on whether to build a salon AI administrator. Pages on alternatives, economics, sources and methodology; a Next.js static export.", PAGES + "ai-bot-market-brief/", "HTML · Next.js", "html"),
    ("web", "2026", "cppk-strelka", "Предложения по цифровому присутствию ЦППК и сообщества «Стрелка».",
     "Proposals for the digital presence of CPPK and the Strelka community.", GH + "cppk-strelka", "TypeScript", "ts"),
    ("web", "2026", "free-messenger-ideas", "Идеи для мессенджера с максимальной доступностью в условиях блокировок.",
     "Ideas for a messenger with maximum availability under network blocking.", GH + "free-messenger-ideas", "Research", "md"),
    ("tools", "2024", "deep-files-sync", "Граф связей Deep как файловая система: правка базы через grep, редактор и git. 13 версий в npm.",
     "The Deep link graph as a file system: edit the database with grep, an editor and git. 13 releases on npm.", GH + "deep-files-sync", "JavaScript", "js"),
    ("tools", "2025", "xtts-v2-js", "npm-пакет для XTTS-v2: синтез речи с клонированием голоса на 17 языках, сам поднимает Python-окружение.",
     "An npm package for XTTS-v2: speech synthesis with voice cloning in 17 languages that sets up its own Python environment.", GH + "xtts-v2-js", "JavaScript", "js"),
    ("tools", "2025", "zonosJS", "npm-клиент синтеза речи Zonos.",
     "An npm client for Zonos speech synthesis.", GHH + "zonosJS", "JavaScript", "js"),
    ("exp", "2021", "GEFFEST", "Перчатка-манипулятор: положение пальцев и кисти считается через кватернионы (без срывов углов Эйлера), перчатка и манипулятор говорят по радио собственным компактным протоколом. Паял схемы сам; отдельно написал Android-приложение голосового управления на Java и Vosk, работающее без интернета.",
     "A glove-controlled manipulator: finger and wrist pose is computed with quaternions (no Euler-angle flips), the glove and the arm talk over radio with a compact protocol of my own. I soldered the circuits myself; I also wrote an Android voice-control app in Java with Vosk that works offline.", GHH + "GEFFEST", "C++ · Arduino · Java", "cpp java"),
    ("exp", "2025", "Orbiteer", "Анализатор рисков космических миссий: расчёт вероятности столкновений, 3D-визуализация орбит на three.js, API на Sanic.",
     "A space-mission risk analyser: collision probability, 3D orbit visualisation on three.js, an API on Sanic.", GH + "Orbiteer", "Python · HTML", "python html"),
    ("exp", "2021", "ghj", "Компьютерное зрение: бот определяет уровень замерзания Онежского озера по кадрам с уличной камеры.",
     "Computer vision: a bot estimating how frozen Lake Onega is from street-camera frames.", GHH + "ghj", "Python", "python"),
]
CATS = [("all", T("Все", "All")), ("ai", T("ИИ и агенты", "AI and agents")), ("bots", T("Боты и парсеры", "Bots and parsers")),
        ("web", T("Веб и исследования", "Web and research")), ("tools", T("Инструменты", "Tools")), ("exp", T("Эксперименты", "Experiments"))]
LANGCHIPS = [("all", T("Любой", "Any")), ("python", "Python"), ("js", "JavaScript"), ("ts", "TypeScript"), ("html", "HTML"), ("cpp", "C++"), ("java", "Java"), ("md", "Markdown")]

# ---------- showcase (only facts verified by a local audit on 2026-11-17) ----------
SHOWCASE = [
    ("tg-runner-orchestrator", GH + "tg-runner-orchestrator", "Python",
     T("Оркестратор запуска Telegram-ботов на конечном автомате с Redis. README с архитектурой и Docker-быстрым стартом.", "An orchestrator for Telegram bots on a state machine with Redis. A README with architecture and a Docker quick start."),
     ["README 168", T("29 тест-файлов", "29 test files"), "MIT", "pyproject"]),
    ("lightrag-mcp", GH + "lightrag-mcp", "JavaScript",
     T("MCP-сервер к self-hosted LightRAG: режимы поиска, реранкинг, ответы со ссылками.", "An MCP server for self-hosted LightRAG: search modes, reranking, answers with citations."),
     ["README 79", T("тесты", "tests"), T("лицензия", "license"), "package.json"]),
    ("vk-tg-parser", GH + "vk-tg-parser", "Python",
     T("Единый парсер Telegram (MTProto) и VK с общей моделью данных и мониторингом.", "One parser for Telegram (MTProto) and VK with a shared data model and monitoring."),
     ["README 241", T("справочник API", "API reference"), T("тесты", "tests"), "pyproject"]),
]

# ---------- packages ----------
PACKAGES = [
    ("xtts-v2-js", "2025", "v1.0.6", 35, "https://www.npmjs.com/package/xtts-v2-js",
     T("Обёртка над XTTS-v2 с клонированием голоса на 17 языках: сама поднимает Python-окружение, чтобы пакет ставился как обычная зависимость Node.js. 7 версий.",
       "A wrapper over XTTS-v2 with voice cloning in 17 languages: it sets up its own Python environment so the package installs like a normal Node.js dependency. 7 releases.")),
    ("zonosjs", "2025", "v1.0.8", 23, "https://www.npmjs.com/package/zonosjs",
     T("Клиент к локальному серверу синтеза речи Zonos. Вместе с zonos-client 10 версий.", "A client for the local Zonos speech-synthesis server. Together with zonos-client, 10 releases.")),
    ("zonos-client", "2025", "v1.0.0", 12, "https://www.npmjs.com/package/zonos-client",
     T("Низкоуровневый клиент Zonos: запросы к серверу синтеза речи.", "A low-level Zonos client: requests to the speech-synthesis server.")),
    ("deep-files-sync", "2024", "v2.0.5", 22, "https://www.npmjs.com/package/deep-files-sync",
     T("Проекция графа связей Deep на файловую систему: каталоги отражают связи, правки синхронизируются в обе стороны. 13 версий.",
       "A projection of the Deep link graph onto the file system: directories mirror links, edits sync both ways. 13 releases.")),
    ("@timax/passport-*", "2024", "v0.0.2–0.0.5", 78, "https://www.npmjs.com/~timax",
     T("Регистрация и подтверждение по email: четыре пакета (authorization, authorization-ui, verification, verification-ui).",
       "Sign-up and email verification: four packages (authorization, authorization-ui, verification, verification-ui).")),
    ("InnerEcho", "2025", T("репозиторий", "repository"), None, GH + "InnerEcho",
     T("Локальный голосовой стек: распознавание речи (Whisper), языковая модель, синтез с клонированием голоса (XTTS), автонастройка аудиоустройств. Сравнение моделей синтеза на русском корпусе.",
       "A local voice stack: speech recognition (Whisper), a language model, voice-cloning synthesis (XTTS), automatic audio-device setup. A comparison of synthesis models on a Russian corpus.")),
]

# ---------- organisations / accounts ----------
acc = gh["accounts"]
own = {k: len(v) for k, v in gh["repos"].items()}
ORGS = [
    ("Deep.Foundation", T("организация · с 2022", "organisation · since 2022"), "https://github.com/deep-foundation",
     T("Открытая ассоциативная платформа. В организации %d публичных репозиториев (создана в 2020), я участник с 2022 года: пакеты ИИ-тулинга, deep-files-sync, документация." % gh["org_deep"]["public_repos"],
       "An open associative platform. The organisation has %d public repositories (founded in 2020); I have been a member since 2022: AI tooling packages, deep-files-sync, documentation." % gh["org_deep"]["public_repos"])),
    ("TimaxLacs", T("основной аккаунт · с 2021", "main account · since 2021"), "https://github.com/TimaxLacs",
     T("%d собственных репозиториев без форков: боты, парсеры, агентные процессы, голос, сайты." % own["TimaxLacs"],
       "%d own non-fork repositories: bots, parsers, agent workflows, voice, websites." % own["TimaxLacs"])),
    ("TimaxHack", T("аккаунт · с 2019", "account · since 2019"), "https://github.com/TimaxHack",
     T("%d репозиториев без форков. Под ним лежит большинство коммитов в LLM-шлюзе deep-assistant, поэтому он указан." % own["TimaxHack"],
       "%d non-fork repositories. It holds most commits in the deep-assistant LLM gateway, which is why it is listed." % own["TimaxHack"])),
    ("timaxlax", T("аккаунт · с 2024", "account · since 2024"), "https://github.com/timaxlax",
     T("Третий аккаунт, 3 репозитория.", "A third account, 3 repositories.")),
]

# ---------- stack ----------
STACK = [
    (T("Языки", "Languages"), ["Python", "TypeScript", "JavaScript", "SQL", "Bash", "Java", "C++"]),
    (T("Фронтенд", "Frontend"), ["React", "Vite", "Next.js", "Tailwind", "Capacitor", "Payload CMS", "shadcn/ui", "three.js"]),
    (T("Бэкенд", "Backend"), ["Node.js", "Express", "FastAPI", "Sanic", "Hasura GraphQL", "REST", "zod"]),
    (T("Данные", "Data"), ["PostgreSQL / PostGIS", "Redis", "SQLite", "MinIO / S3", "RabbitMQ"]),
    (T("ИИ", "AI"), [T("маршрутизация и фолбэк", "routing and fallback"), T("биллинг токенов", "token billing"), T("очереди генерации", "generation queues"), "RAG", "MCP", "LangChain", T("распознавание речи", "speech recognition"), T("синтез голоса", "voice synthesis"), T("компьютерное зрение", "computer vision")]),
    (T("Боты и парсинг", "Bots and parsing"), ["aiogram", "Pyrogram", "Telethon / MTProto", "VK API", "Telegram Bot API", "MAX", "Playwright"]),
    (T("Тестирование", "Testing"), ["pytest", "node --test", "Playwright e2e", T("смоук-тесты", "smoke tests")]),
    (T("Прод", "Ops"), ["Docker", "Docker Compose", "nginx", "systemd", "Linux", "Git", "CI", T("DNS и почта", "DNS and mail"), "SSL"]),
    (T("Разметка и форматы", "Markup and formats"), ["HTML", "CSS", "Markdown", "JSON", "YAML"]),
    (T("Среда с моделями", "Model tooling"), ["Cursor", "Claude Code", "ClawCode", "subagents"]),
    (T("Предметные области", "Domains"), [T("боты", "bots"), "e-commerce", T("гео-сервисы", "geo services"), T("платежи", "payments"), T("контент-конвейеры", "content pipelines"), T("парсинг", "parsing"), T("обработка сигналов", "signal processing")]),
]

METHOD = [
    (T("Рамка", "Frame"), T("Исследование, ограничения и критерии приёмки фиксирую сам, до того как подключаю модель.", "I fix the research, constraints and acceptance criteria myself before a model gets involved.")),
    (T("Правила", "Rules"), T("Перед работой записываю в репозиторий полный набор правил: как гонять проверки, чего не трогать. Те же ограничения дублирую в CI и хуках, чтобы их нельзя было обойти.", "Before any work I put a complete rule set into the repository: how to run checks, what not to touch. The same limits are duplicated in CI and hooks so they cannot be bypassed.")),
    (T("Узкие шаги", "Narrow steps"), T("Код с моделью пишу узкими шагами и через отдельных субагентов: план, правка, прогон тестов и линтеров. Скоуп файлов фиксирую заранее, параллельные правки изолирую.", "I write code with a model in narrow steps and through separate subagents: plan, edit, tests and linters. The file scope is fixed in advance; parallel edits are isolated.")),
    (T("Независимая проверка", "Independent review"), T("Проверка идёт отдельно и не принимает код, который только что написал исполнитель. Тесты, написанные моделью вместе с реализацией, доказательством не считаю: смотрю негативные и граничные случаи, секреты и зависимости. Без собственного ревью код не отдаю.", "Review runs separately and rejects code the executor has just written. Tests a model wrote together with the implementation are not proof: I check negative and edge cases, secrets and dependencies. Nothing leaves my hands without my own review.")),
]

PATH = [
    ("2019", T("Первый аккаунт на GitHub (TimaxHack).", "The first GitHub account (TimaxHack).")),
    ("2021", T("Начал программировать всерьёз: приложения на Java и C++, перчатка-манипулятор GEFFEST, бот замерзания Онежского озера по кадрам камеры.", "Started programming seriously: Java and C++ apps, the GEFFEST glove manipulator, a Lake Onega freezing bot working from camera frames.")),
    ("2022", T("Присоединился к open-source-экосистеме Deep.Foundation.", "Joined the Deep.Foundation open-source ecosystem.")),
    ("2024", T("Первые коммерческие проекты: LLM-шлюз и Telegram-бот Deep.Assistant, пакет deep-files-sync.", "First commercial projects: the Deep.Assistant LLM gateway and Telegram bot, the deep-files-sync package.")),
    ("2025", T("Голосовой ассистент InnerEcho, reasoning-конвейер, ai-lector. С августа ManyAir, с декабря e-commerce платформа.", "The InnerEcho voice assistant, a reasoning pipeline, ai-lector. ManyAir from August, the e-commerce platform from December.")),
    ("2026", T("Matreshka, tg-runner, vk-tg-parser, Предложка, ai-post-generator, lightrag-mcp, cursor-agent-workflows, GLASAT и аналитика для ЦППК.", "Matreshka, tg-runner, vk-tg-parser, the Predlozhka editorial desk, ai-post-generator, lightrag-mcp, cursor-agent-workflows, GLASAT and analysis for CPPK.")),
]
GANTT = [(T("Deep.Foundation", "Deep.Foundation"), 2022.0, 2026.88), (T("Deep.Assistant", "Deep.Assistant"), 2024.0, 2026.0),
         ("ManyAir", 2025.58, 2026.42), (T("E-commerce", "E-commerce"), 2025.92, 2026.88), ("Matreshka", 2026.0, 2026.88),
         ("GLASAT", 2026.67, 2026.88)]

SECTIONS = [("about", T("Кратко", "About")), ("work", T("Опыт", "Work")), ("path", T("Путь", "Path")),
            ("projects", T("Проекты", "Projects")), ("packages", T("Пакеты и голос", "Packages and voice")),
            ("orgs", T("Организации", "Organisations")), ("activity", T("Активность", "Activity")),
            ("stack", T("Инструменты", "Tools")), ("method", T("Метод", "Method")),
            ("knowledge", T("Знания", "Education")), ("contact", T("Контакты", "Contact"))]
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]
NUM = {sid: ROMAN[i] for i, (sid, _) in enumerate(SECTIONS)}

# ---------- renderers ----------
def h2(sid):
    label = dict(SECTIONS)[sid]
    return '<h2><span class="n">%s</span>%s</h2>' % (NUM[sid], label)

def chips(items, label=None):
    pre = '<span class="lbl">%s</span>' % label if label else ""
    return pre + "".join('<button type="button" data-f="%s" aria-pressed="%s">%s</button>' % (k, "true" if k == "all" else "false", l) for k, l in items)

def job(j):
    b = "".join("<li>%s</li>" % x for x in j["bullets"])
    ul = '<ul class="b">%s</ul>' % b if b else ""
    tags = "".join("<span>%s</span>" % t for t in j["tags"])
    return ('<article class="job" data-roles="%s"><div class="when">%s</div><div class="body"><h3>%s</h3><p class="role">%s</p><p>%s</p>%s<div class="tags">%s</div></div></article>'
            % (j["roles"], j["when"], j["title"], j["role"], j["lead"], ul, tags))

def card(p):
    cat, year, name, dru, den, url, lang, toks = p
    title = '<a href="%s" target="_blank" rel="noopener">%s</a>' % (url, e(name)) if url else "<span>%s</span>" % e(name)
    priv = "" if url else '<em class="priv">%s</em>' % T("закрытый", "private")
    return ('<article class="card" data-cat="%s" data-lang="%s"><div class="cm"><span>%s</span><span>%s</span></div><h3>%s%s</h3><p>%s</p></article>'
            % (cat, toks, year, e(lang), title, priv, T(dru, den)))

def showcase_card(s):
    name, url, lang, desc, checks = s
    ch = "".join('<span class="y">%s</span>' % c for c in checks)
    return ('<article class="card"><div class="cm"><span>%s</span><span>MIT/OSS</span></div><h3><a href="%s" target="_blank" rel="noopener">%s</a></h3><div class="checks">%s</div><p>%s</p></article>'
            % (lang, url, name, ch, desc)).replace("MIT/OSS", "GitHub")

def pkg_card(p):
    name, year, ver, dl, url, desc = p
    st = '<div class="st">%s%s</div>' % (ver, (" · %d %s" % (dl, "загрузок / мес") if False else ""))
    dls = ("<span>%s</span>" % T("%d загрузок за месяц" % dl, "%d downloads last month" % dl)) if dl is not None else "<span>GitHub</span>"
    return ('<article class="card"><div class="cm"><span>%s</span>%s</div><h3><a href="%s" target="_blank" rel="noopener">%s</a></h3><div class="st">%s</div><p>%s</p></article>'
            % (year, dls, url, e(name), ver, desc))

def org_card(o):
    name, kind, url, desc = o
    return ('<article class="card"><div class="cm"><span>%s</span><span></span></div><h3><a href="%s" target="_blank" rel="noopener">%s</a></h3><p>%s</p></article>'
            % (kind, url, name, desc))

def gantt():
    rows = []
    for label, a, b in GANTT:
        rows.append('<div class="g-row"><div class="g-l">%s</div><div class="g-track"><i style="left:%.2f%%;width:%.2f%%"></i></div></div>' % (label, (a - 2021) / 6 * 100, (b - a) / 6 * 100))
    axis = "".join("<span>%d</span>" % y for y in range(2021, 2027))
    return '<div class="gantt">%s<div class="g-row"><div class="g-l"></div><div class="g-axis">%s</div></div></div>' % ("".join(rows), axis)

def bars(items, show=lambda v: fmt(v)):
    mx = max(v for _, v in items)
    return "".join('<div class="bar"><span class="k">%s</span><span class="t"><i style="width:%.1f%%"></i></span><span class="v">%s</span></div>' % (k, v / mx * 100, show(v)) for k, v in items)

def year_bars(items):
    mx = max(v for _, v in items)
    out = []
    for k, v in items:
        lin = v / mx * 100
        lg = math.log10(v + 1) / math.log10(mx + 1) * 100
        out.append('<div class="bar"><span class="k">%s</span><span class="t"><i style="width:%.1f%%" data-lin="%.1f" data-log="%.1f"></i></span><span class="v">%s</span></div>' % (k, lin, lin, lg, fmt(v)))
    return '<div class="ybars">%s</div>' % "".join(out)

MONTHS_RU = ["янв", "фев", "мар", "апр", "май", "июн", "июл", "авг", "сен", "окт", "ноя", "дек"]
MONTHS_EN = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

def calendar():
    cal = [(datetime.date.fromisoformat(d), c) for d, c in gh["calendar_lacs"]]
    pad = (cal[0][0].weekday() + 1) % 7  # Sunday-first rows
    cells = ['<i style="visibility:hidden"></i>'] * pad
    def lvl(c): return 0 if c == 0 else 1 if c <= 2 else 2 if c <= 5 else 3 if c <= 9 else 4
    for d, c in cal:
        cells.append('<i class="l%d" title="%s: %d"></i>' % (lvl(c), d.isoformat(), c) if c else '<i title="%s"></i>' % d.isoformat())
    ncols = (len(cells) + 6) // 7
    labels, last = [], None
    for col in range(ncols):
        idx = col * 7
        d = cal[0][0] - datetime.timedelta(days=pad) + datetime.timedelta(days=idx)
        if d.month != last and (col == 0 or d.day <= 7):
            labels.append('<span style="grid-column:%d">%s</span>' % (col + 1, T(MONTHS_RU[d.month - 1], MONTHS_EN[d.month - 1])))
            last = d.month
    total = sum(c for _, c in cal)
    foot = ('<div class="calfoot"><span>%s</span><span class="sc">%s <i></i><i class="l1"></i><i class="l2"></i><i class="l3"></i><i class="l4"></i> %s</span></div>'
            % (T("%d вклада за 12 месяцев, аккаунт TimaxLacs" % total, "%d contributions in 12 months, the TimaxLacs account" % total), T("меньше", "less"), T("больше", "more")))
    return '<div class="calwrap"><div class="months">%s</div><div class="cal">%s</div></div>%s' % ("".join(labels), "".join(cells), foot)

def activity():
    other = max(tot["total"] - tot["commits"] - tot["pull_requests"] - tot["issues"] - tot["reviews"], 0)
    parts = [(tot["commits"], T("коммиты", "commits")), (tot["pull_requests"], T("пул-реквесты", "pull requests")),
             (tot["issues"], "issues"), (tot["reviews"] + other, T("ревью и прочее", "reviews and other"))]
    s = sum(v for v, _ in parts) or 1
    seg = "".join('<i style="width:%.2f%%"></i>' % (v / s * 100) for v, _ in parts)
    colors = ["var(--accent)", "#8a7d5f", "#5d584b", "#3d3a32"]
    legend = "".join('<span style="--c:%s">%s %s</span>' % (colors[i], l, fmt(v)) for i, (v, l) in enumerate(parts))
    top_code = sorted(code_bytes.items(), key=lambda kv: -kv[1])[:8]
    repo_lang = lang_repo.most_common(7)
    cloud = "".join('<span style="font-size:%dpx">%s</span>' % (15 + int(14 * math.sqrt(v / max(code_bytes.values()))), k) for k, v in sorted(code_bytes.items(), key=lambda kv: -kv[1]))
    note_markup = T("Размер кода в собственных репозиториях по данным GitHub, без HTML и CSS (их %s КБ: в основном страницы и экспорты). Это объём файлов, а не авторские строки." % fmt(round((gh['lang_bytes_total'].get('HTML', 0) + gh['lang_bytes_total'].get('CSS', 0)) / 1024)),
                    "Code size in own repositories according to GitHub, excluding HTML and CSS (%s KB: mostly pages and exports). This is file volume, not authored lines." % fmt(round((gh['lang_bytes_total'].get('HTML', 0) + gh['lang_bytes_total'].get('CSS', 0)) / 1024)))
    return ('''
<div class="two">
  <div>
    <h4 class="cap">%(c1)s%(ast)s</h4>
    <div class="chips yscale" style="margin-bottom:12px"><button type="button" data-m="lin" aria-pressed="true">%(lin)s</button><button type="button" data-m="log" aria-pressed="false">%(log)s</button></div>
    %(years)s
  </div>
  <div>
    <h4 class="cap">%(c2)s%(ast)s</h4>
    <div class="seg">%(seg)s</div>
    <div class="legend">%(legend)s</div>
  </div>
</div>
<h4 class="cap">%(c3)s%(ast)s</h4>
%(cal)s
<div class="two" style="margin-top:34px">
  <div><h4 class="cap">%(c4)s%(ast)s</h4>%(lbytes)s<p class="note">%(nm)s</p></div>
  <div><h4 class="cap">%(c5)s%(ast)s</h4>%(lrepo)s<h4 class="cap" style="margin-top:22px">%(c6)s</h4><div class="cloud">%(cloud)s</div></div>
</div>
<p class="note">%(foot)s</p>''' % dict(
        c1=T("Вклады по годам (2 аккаунта)", "Contributions by year (2 accounts)"), ast=AST,
        lin=T("линейная", "linear"), log=T("логарифм", "log"), years=year_bars(YEARS),
        c2=T("Из чего состоят вклады", "What the contributions are made of"), seg=seg, legend=legend,
        c3=T("Календарь вкладов за год", "Contribution calendar, last year"), cal=calendar(),
        c4=T("Код по языкам, КБ", "Code by language, KB"), lbytes=bars([(k, round(v / 1024)) for k, v in top_code]), nm=note_markup,
        c5=T("Репозитории по языкам", "Repositories by language"), lrepo=bars(repo_lang, show=lambda v: str(v)),
        c6=T("Все языки кода", "All code languages"), cloud=cloud,
        foot=T("Публичные данные GitHub на %s: аккаунты TimaxLacs и TimaxHack, собственные репозитории без форков. Значительная часть работы лежит в закрытых репозиториях заказчиков и не попадает в эти цифры." % SNAP,
               "Public GitHub data as of %s: the TimaxLacs and TimaxHack accounts, own non-fork repositories. A large part of the work sits in clients' private repositories and is not counted here." % SNAP)))

NAV = "".join('<a href="#%s" data-s="%s"><span class="rn">%s</span>%s</a>' % (sid, sid, NUM[sid], label) for sid, label in SECTIONS)

ABOUT = '''%s
<p class="lede">%s</p>
<p>%s</p>
<p>%s</p>
%s''' % (
    h2("about"),
    T("Встраиваю языковые модели в работающие продукты. Написал первую версию <em>LLM-шлюза</em> для коммерческого агрегатора нейросетей: маршрутизация между поставщиками, фолбэк, биллинг по токенам.",
      "I put language models into products that are already running. I wrote the first version of an <em>LLM gateway</em> for a commercial AI aggregator: provider routing, fallback, token billing."),
    T("Сейчас по контракту веду клиентскую часть e-commerce платформы и строю собственные инструменты вокруг агентов: редакционный стол для сообществ, MCP-сервер к базе знаний, процессы с независимой проверкой. Программирую с 2021 года, коммерческие проекты веду с 2024-го. Всё описанное ниже сделано на практике и открыто для проверки по репозиториям.",
      "Right now I lead the client side of an e-commerce platform on contract and build my own tooling around agents: an editorial desk for communities, an MCP server for a knowledge base, workflows with independent review. I have been programming since 2021 and shipping commercial projects since 2024. Everything below was done in practice and can be checked in the repositories."),
    T("Образование: СПбПУ Петра Великого, техническая специальность; институт СПО СПбПУ, базовый инженерно-технический курс. Дальше ушёл в продуктовую разработку. С 2021 года работаю с разными командами над отдельными проектами, сменил восемь команд.",
      "Education: Peter the Great St. Petersburg Polytechnic University, a technical degree track; the SPbPU college institute, a basic engineering course. After that I moved into product development. Since 2021 I have worked with different teams on separate projects and have changed eight teams."),
    RESULTS_HTML)

KNOWLEDGE = '''%s
<dl class="kv">
  <dt>%s</dt><dd>%s</dd>
  <dt>%s</dt><dd>%s</dd>
  <dt>%s</dt><dd>%s</dd>
  <dt>%s</dt><dd>%s</dd>
  <dt>%s</dt><dd>%s</dd>
</dl>''' % (
    h2("knowledge"),
    T("Образование", "Education"), T("Санкт-Петербургский политехнический университет Петра Великого — техническая специальность. Институт СПО СПбПУ — базовый инженерно-технический курс.", "Peter the Great St. Petersburg Polytechnic University — a technical degree track. SPbPU college institute — a basic engineering course."),
    T("Языки", "Languages"), T("Русский — родной. Английский — технический и письменный, профессиональный уровень.", "Russian — native. English — technical and written, professional level."),
    T("Навыки", "Skills"), T("Управление командой, питчинг.", "Team management, pitching."),
    T("Что не взлетело", "What did not fly"), T("ArtApollo (2023–2025): студия, где заказы отрисовывают нейросети; команда до 30 человек, первые платные заказы, корпоративный заказ на 12 человек, проект закрыт. Cyber Vestis: прототип умной одежды с климат-контролем, ПО для сенсорного дисплея и телеметрия температуры тела; рабочий прототип есть, до инвестиций не дошли.", "ArtApollo (2023–2025): a studio where orders are drawn by neural networks; a team of up to 30, first paid orders, a corporate order for 12 people, the project closed. Cyber Vestis: a smart-clothing prototype with climate control, touch-display software and body-temperature telemetry; a working prototype exists, it never reached investment."),
    T("Формат", "Format"), T("Санкт-Петербург, удалённо. Контрактная разработка, продуктовые команды.", "Saint Petersburg, remote. Contract development, product teams."))

CONTACT = '''%s
<div class="contact">
  <a class="btn" href="mailto:chakirov.timyr@gmail.com">chakirov.timyr@gmail.com</a>
  <a class="btn ghost" href="%s" data-pdf="ru">%s</a>
</div>
<dl class="kv">
  <dt>Telegram</dt><dd><a href="https://t.me/TimaxLacs">@TimaxLacs</a></dd>
  <dt>GitHub</dt><dd><a href="https://github.com/TimaxLacs">TimaxLacs</a> · <a href="https://github.com/TimaxHack">TimaxHack</a> · <a href="https://github.com/timaxlax">timaxlax</a></dd>
  <dt>npm</dt><dd><a href="https://www.npmjs.com/~timax">~timax</a></dd>
  <dt>%s</dt><dd><a href="https://matreshka.club">matreshka.club</a> · <a href="https://t.me/DeepGPTBot">@DeepGPTBot</a> · <a href="https://t.me/gptDeep">@gptDeep</a></dd>
</dl>''' % (h2("contact"), "/resume.pdf", T("Скачать PDF", "Download PDF"), T("Продукты", "Products"))

rep = {
    "%%NAV%%": NAV, "%%STATS%%": STATS_HTML, "%%STATSNOTE%%": STATSNOTE, "%%ABOUT%%": ABOUT,
    "%%H2_WORK%%": h2("work"), "%%GANTT%%": gantt(), "%%ROLECHIPS%%": chips(ROLES, T("Показать опыт для", "Show experience for")), "%%JOBS%%": "".join(job(j) for j in JOBS),
    "%%H2_PATH%%": h2("path"), "%%PATH%%": "".join("<li><b>%s</b><span>%s</span></li>" % (y, t) for y, t in PATH),
    "%%H2_PROJECTS%%": h2("projects"), "%%SHOWCASE%%": "".join(showcase_card(s) for s in SHOWCASE),
    "%%CHIPS%%": chips(CATS, T("Категория", "Category")), "%%LANGCHIPS%%": chips(LANGCHIPS, T("Язык", "Language")),
    "%%CARDS%%": "".join(card(p) for p in PROJECTS),
    "%%H2_PACKAGES%%": h2("packages"), "%%PACKAGES%%": "".join(pkg_card(p) for p in PACKAGES),
    "%%PKGNOTE%%": T("Загрузки за последний месяц на %s по api.npmjs.org. Кроме личных пакетов, в npm-scope @deep-foundation я числюсь мейнтейнером 148 пакетов команды." % SNAP,
                     "Downloads over the last month as of %s from api.npmjs.org. Besides my own packages, I am listed as a maintainer of 148 team packages in the @deep-foundation npm scope." % SNAP),
    "%%H2_ORGS%%": h2("orgs"), "%%ORGS%%": "".join(org_card(o) for o in ORGS),
    "%%H2_ACTIVITY%%": h2("activity"), "%%ACTIVITY%%": activity(),
    "%%H2_STACK%%": h2("stack"), "%%STACK%%": "".join('<div class="sg"><h4>%s</h4><p>%s</p></div>' % (g, "".join("<span>%s</span>" % x for x in items)) for g, items in STACK),
    "%%H2_METHOD%%": h2("method"), "%%METHOD%%": "".join("<li><b>%d</b><div><h4>%s</h4><p>%s</p></div></li>" % (i, t, d) for i, (t, d) in enumerate(METHOD, 1)),
    "%%KNOWLEDGE%%": KNOWLEDGE, "%%CONTACT%%": CONTACT, "%%UPDATED%%": SNAP,
    "%%PDF_RU%%": "/resume.pdf", "%%PDF_EN%%": "/resume.en.pdf",
}
tpl = open(TPL, encoding="utf-8").read()
for k, v in rep.items():
    tpl = tpl.replace(k, v)
left = [l.strip()[:80] for l in tpl.splitlines() if "%%" in l]
assert not left, left[:3]
open(OUT, "w", encoding="utf-8").write(tpl)
print("ok", len(tpl), "bytes ->", OUT)
