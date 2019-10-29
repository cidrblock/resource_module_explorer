docker build -t rme .
docker tag rme nmake/rme:latest
docker push nmake/rme:latest
