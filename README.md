## Shorty

#### Installation:

On Windows: 
```
python -m venv venv
.\venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
.\reset_db.cmd
flask run
```

On Linux:
```
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
source reset_db.cmd
python app.py
```
