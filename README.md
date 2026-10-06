# Qamqor Logistics — Streamlit dashboard

Бұл жоба бастапқы зертханалық жұмыстың `lambda`, closure және recursion логикасын сақтайды. Интерфейс сол `main.py`, `cities.py`, `warehouses.py`, `orders.py` және `vehicles.py` модульдерінен дерек алады.

## Іске қосу

Барлық файлды бір папкада сақтап, сол папканы терминалда ашыңыз. Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Streamlit берген жергілікті мекенжай браузерде ашылады. Келесі жолы виртуалды ортаны іске қосқаннан кейін мына команда жеткілікті:

```powershell
python -m streamlit run app.py
```

Linux немесе macOS жүйесінде виртуалды ортаны белсендіру командасы:

```bash
source .venv/bin/activate
```

## Бөлімдер

- **Шолу:** тапсырыс саны мен жалпы салмақ, дайын тапсырыстар, қойма жүктемесі.
- **Тапсырыстар:** күй, қойма және салмақ бойынша сүзгі.
- **Қоймалар:** таңдалған қоймадағы тапсырыстардың рекурсивті кезегі.
- **Маршруттар:** бастапқы маршруттардың рекурсивті өтуі.
- **Көліктер:** парк пен қолжетімді жүк сыйымдылығы.
- **Алгоритмдер:** lambda/reduce, closure және recursion нәтижелері.

`main.py` командалық жолдан да бұрынғыдай орындала береді: `python main.py`.
