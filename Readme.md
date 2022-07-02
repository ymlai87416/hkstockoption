# Stock option worksheet presented by Super rich fund

Started by three mans in HK to spectaculate HK stock.

Production URL: [http://trade.ymlai87416.com/hkstockopton](http://trade.ymlai87416.com/hkstockopton)

### Web

Written in Angular

```
ng build --prod --deploy-url /hkstockopton
DOCKER_BUILDKIT=1 docker build -t ymlai87416/hkstock-web:1.0 .
```

### API

Written in Spring

```
DOCKER_BUILDKIT=1 docker build -t ymlai87416/hkstock-api:1.0 .
```

### Batch job

```
DOCKER_BUILDKIT=1 docker build -t ymlai87416/hkstock-batch:1.0 .
```
