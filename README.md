### Setup Instructions 

```
python -m venv venv
./venv/Scripts/activate
pip install -r requirements.txt
```

### To generate resume
> `sample_texts` variable needs to be edited to pass raw data about candidate

> to use model , download model from link and change path in line 24 - generate_resume.py

> ensure torch with cuda is installed for gpu inference
```
python generate_resume.py
```
