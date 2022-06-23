# automated_shift_generator_api

## 開発環境

### 起動方法

```bash
docker compose up
```

[http://localhost:5000/api/v1/part_time_jobs](http://localhost:5000/api/v1/part_time_jobs?q=1)等にアクセス

### mongodb接続方法

```bash
docker compose exec mongo bash
```

```bash
mongo admin -u root -p
```
パスワードを要求されるのでexampleと入力

### mongo-expressのアクセス方法

[http://localhost:8081](http://0.0.0.0:8081/)にアクセス

