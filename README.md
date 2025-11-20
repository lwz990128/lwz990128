# 卡密验证与 Token 收录站点

一个使用 FastAPI 构建的简易后台，可自发行卡密、验证卡密并收录 token。

## 功能

- 生成卡密：支持自定义前缀、数量与有效天数。
- 核验卡密：验证是否存在、是否过期、是否已被使用。
- 收录 Token：验证通过后提交 token，自动绑定并记录时间。
- 查看卡密：快速查看当前系统中已发行的卡密状态。

## 本地运行

1. 安装依赖：

```bash
pip install -r requirements.txt
```

2. 启动服务：

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

3. 打开浏览器访问 `http://localhost:8000`，按照页面流程进行验证与录入。

数据默认保存在 `app/data/store.json`，可根据需要自行替换为数据库存储。
