# Stock option worksheet presented by Super rich fund

Started by three mans in HK to spectaculate HK stock.

Production URL: [http://trade.ymlai87416.com/hkstockoption](http://trade.ymlai87416.com/hkstockoption)

### Web

Written in Angular

```
ng build --prod --deploy-url /hkstockoption/ --base-href /hkstockoption/
DOCKER_BUILDKIT=1 docker build -t ymlai87416/hkstock-web:1.0 .
```

### API

Written in Spring

```
DOCKER_BUILDKIT=1 docker build -t ymlai87416/hkstock-api:1.0 .
```

### Batch job

Use airflow to run batch job
```
DOCKER_BUILDKIT=1 docker build -t ymlai87416/hkstock-batch:1.0 .
```

![alt text](./img/airflow_batch.png)
