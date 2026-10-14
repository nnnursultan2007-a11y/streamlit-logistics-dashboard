# Qamqor Logistics · Streamlit

Зертханалық №1–4 функцияларын Streamlit интерфейсінде көрсететін логистика dashboard-ы. `main.py` мен `containers.py` бастапқы функциялар мен Maybe/Either контейнерлерін сақтайды.

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

## Файлдар

`app.py`, `main.py`, `containers.py`, `cities.py`, `warehouses.py`, `orders.py`, `vehicles.py`, `test_main.py`, `requirements.txt`.
