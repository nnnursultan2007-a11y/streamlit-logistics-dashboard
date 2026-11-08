# Qamqor Logistics · Streamlit

Зертханалық №1–6 функцияларын Streamlit интерфейсінде көрсететін логистика dashboard-ы. `main.py` мен `containers.py` бастапқы функциялар мен Maybe/Either контейнерлерін сақтайды.

## Компьютерде іске қосу

PowerShell-ді осы файлдар тұрған папкадан ашып, командаларды бір-бірлеп орындаңыз:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

## Streamlit Community Cloud-қа шығару

`share.streamlit.io` сайтынан **Create app** басып, GitHub репозиторийін таңдаңыз. Branch — `main`, негізгі файл — `app.py`. Deploy басқан соң сайт сілтемесі беріледі. GitHub-тағы код өзгерсе, Cloud қолданбасы сол өзгерістерді жаңартады.

## Dashboard бөлімдері

- Шолу, тапсырыстарды сүзу, қойма кезектері, маршруттар және көліктер.
- Маршрутты толық перебормен немесе 8-ден көп тапсырысқа жақын көрші әдісімен есептеу; кэш уақытын көрсету.
- Functional Core: Maybe/Either арқылы тапсырысты табу, ережемен тексеру, қойма кезегін құру және маршрут жоспарын есептеу.
- Maybe / Either әдістерін мысалдармен интерактивті көрсету.


## Зертханалық жұмыс №5 — Lazy Evaluation

- `iter_orders(orders, pred)` генераторы тапсырыстарды бір-бірден тексеріп, шартқа сай тапсырыстарды `yield` арқылы береді.
- `lazy_assign(orders, vehicles)` тапсырыс ағынынан әр тапсырысқа бос әрі жүк көтерімділігі жеткілікті көлік тағайындайды.
- `Lazy Evaluation` бөлімінде тапсырыс күйін таңдап, генератордан алғашқы 1–10 нәтижені көруге болады. Қалған нәтиже сұралмайынша өңделмейді.

## Зертханалық жұмыс №6 — Event Bus / FRP

- `Event` оқиғаның атауын, уақытын және деректерін сақтайды.
- `EventBus.subscribe()` оқиғаға handler тіркейді, ал `EventBus.publish()` оқиғаны жариялап, тиісті handler функцияларын шақырады.
- `ORDER_ADDED` және `QUEUE_UPDATED` кезек панелін жаңартады.
- `ROUTE_PLANNED` жоспарланған маршруттар панелін, ал `DELIVERED` жеткізілген тапсырыстар панелін жаңартады.
- Streamlit ішіндегі `Event Bus / FRP` бөлімінде оқиғаларды интерактивті жариялап, панельдердің өзгеруін көруге болады.

## Файлдар

`app.py`, `main.py`, `containers.py`, `cities.py`, `warehouses.py`, `orders.py`, `vehicles.py`, `test_main.py`, `requirements.txt`.
