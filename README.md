## Install

```
py -m venv src/.venv
src\.venv\Scripts\activate.bat
pip install -r src/requirements.txt
```

## Run

Commands inside of venv:

```
cd src
scrapy crawl tesco -o ../res.json -a url="https://www.tesco.com/groceries/en-GB/shop/household/kitchen-roll-and-tissues/all"
```

## Contribute

After adding new dependencies (requirements) save them to file
```
pip freeze > src/requirements.txt
```
