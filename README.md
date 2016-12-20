# temp-io
A useful IOT device to obtain the current temperature.

It can be placed anywhere in the wifi cover, windows, balconies, backyards, lawns.

## Feature
- Based on the Seeed Wio platform
- RESTFul API with json
- Use Firebase authentication

## Quick Started
- GET /v1/users/:id/temps/:id, Get current temperature
- GET /v1/users/:id/temps/:id/temperatures, Get temperature history
- More API: [API docs](http://developer.temp-io.life/)

## Return Examples
Current temperature
```
{
  "id": "id123",
  "key": "key123",
  "online": false,
  "temperature": 25,
  "temperature_f": 70,
  "temperature_updated_at": "2016-11-22T02:25:01.000Z",
  "read_period": 60,
  "has_sleep": true,
  "name": "Home",
  "description": "Home south glass",
  "owner": {
    "id": 1,
    "name": "awong1900",
    "avatar_url": "https://avatars.githubusercontent.com/u/4022612?v=3",
    "created_at": "2016-11-22T02:25:01.000Z",
    "updated_at": "2016-11-22T02:25:01.000Z"
  },
  "private": false,
  "open": true,
  "status": "normal",
  "status_text": "The device is not wake up more three read period.",
  "activated": true,
  "gps": "33,23",
  "picture_url": "https://temp.io/1.jpg",
  "created_at": "2016-11-22T02:25:01.000Z",
  "updated_at": "2016-11-22T02:25:01.000Z"
}
```

Temperature history
```
{
  "temperatures": [
    {
      "temperature": 25,
      "temperature_f": 70,
      "created_at": "2016-11-22T02:25:01.000Z"
    }
  ]
}
```
