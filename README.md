# resource_module_explorer
A prototype web based resouce module explorer

Quick state
```
podman run -it -p 8080:8080 nmake/rme

-or-

docker run -it -p 8080:8080 nmake/rme
```

Building
```
podman build -t rme .
podmand run -it -p 8080:8080
```

```
docker build -t rme .
docker run -it -p 8080:8080
```


```
git clone git@github.com:nmake/resource_module_explorer.git
cd resource_module_explorer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

browse to http://localhost:8080
