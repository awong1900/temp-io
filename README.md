# temp-io
nodejs web app for temp display with wio link

## 功能需求
- 屋内屋外温度
- 登入可修改，未登入只能查看
- 支持第三方登入

## 资源API
API 前缀 /api/v1
### Github RESTFul API Style
- GET /users/:username 获得其他人的用户资料
- GET /user 用户信息，加token
- GET /user/temperatures 获取本人的温度列表，加token
- GET /users/:username/temperatures 获取其他人的温度列表
- POST /user/temperatures 创建一个温度，加token
- GET /temperatures/:username/:id 获得任意用户温度列表
- PATCH /temperatures/:username/:id 修改温度，加token
- DELETE /temperatures/:username/:id 删除温度，加token
- GET /temperatures 获得所有公开的温度列表

### APIGEE Style
- GET /users/:username 获得用户资料，（加token获得私有信息）
- GET /users/:username/temperatures 创建一个温度，（加token获得私有信息）
- POST /users/:username/temperatures 创建一个温度，必须加token
- GET /users/:username/temperatures/:id 获得任意用户温度
- PATCH /users/:username/temperatures/:id 修改温度，加token
- DELETE /users/:username/temperatures/:id 删除温度，加token
- GET /temperatures 获得所有公开的温度列表

## 访问路径
- /login?  登入

## 第三方授权登入
拿到授权后的token，在用token拿到用户ID后，然后去API服务器验证用户是否存在。

## 返回json设计
user:
{
  "login":  "awong1900",
  "id": 4022612,
  "facebook_id": 1221,
  "weixin_id": null,
  "token": "facebook oauth2 token",
  "avatar_url": "https://avatars.githubusercontent.com/u/4022612?v=3",
  "temperatures_url": "https://api.temp.io/users/awong1900/temperatures",
  "created_at": "2013-04-01T01:28:05Z",
  "updated_at": "2016-03-07T12:35:08Z",
}

temperature:
{
  "id": 53286538,
  "name": "home",
  "full_name": "awong1900/home",
  "owner": {
    "login":  "awong1900",
    "id": 4022612,
    "facebook_id": 1221,
    "weixin_id": null,
    "token": "facebook oauth2 token",
    "avatar_url": "https://avatars.githubusercontent.com/u/4022612?v=3",
    "temperatures_url": "https://api.temp.io/users/awong1900/temperatures",
  },
  "private": false,
  "html_url": "https://github.com/awong1900/home",
  "description": null,
  "url": "https://api.github.com/repos/awong1900/home",
  "created_at": "2016-03-07T01:30:30Z",
  "updated_at": "2016-03-07T01:30:30Z",
}

## MongoDB Model设计
### collection('users')
mongoDB 推荐嵌入存储数据。（嵌入数据较少情况下）。
{
  "_ id": "double",
  "facebook_id": "string",
  "weixin_id": "string",
  "name": "string",
  "created_at": "data",
  "updated_at": "date",
  "temps": [
    {
      "id": "double",
      "name": "string",
      "api": "string"
      "created_at": "data",
      "updated_at": "date",
    }
  ]
}
