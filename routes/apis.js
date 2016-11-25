var express = require('express');
var router = express.Router();

router.get('/', function(req, res, next) {
  res.json({
    "temperatures_url": "http://localhost:3000/api/v1/temperatures/{owner}/{temperature}",
    "temperatures_search_url": "http://localhost:3000/api/v1/search/temperatures?q={query}{&page,per_page,sort,order}",
    "user_url": "http://localhost:3000/api/v1/users/{user}",
    "user_temperatures_url": "http://localhost:3000/api/v1/users/{user}/temperatures{?type,page,per_page,sort}",
    "user_search_url": "http://localhost:3000/api/v1/search/users?q={query}{&page,per_page,sort,order}"
  });
});

router.get('/users', function(req, res, next) {
  db.collection('users').find(
    {},  //TODO 隐藏非公开的temp
    {
      _id: 0,
      token: 0,
      facebook_id: 0,
      github_id: 0
    }).toArray(function(err, users) {
      if (err) next(err);
      res.json(users);
  });
});

router.get('/users/:user_id', function(req, res, next) {
  var user_id = parseInt(req.params.user_id);
  db.collection('users').findOne(
    {id: user_id},  //TODO 隐藏非公开的temp
    {
      _id: 0,
      token: 0,
      facebook_id: 0,
      github_id: 0
    },
    function(err, user) {
      if (err) next(err);
      res.json(user);
  });
});

router.patch('/users/:user_id', function(req, res, next) {
  var user_id = parseInt(req.params.user_id);
  var user = req.body;
  user.updated_at = new Date().toISOString();
  db.collection('users').updateOne(
    {"_id": user_id},
    {$set: user},
    function (err, result) {
      res.json(user);
  });
});

router.delete('/users/:user_id', function(req, res, next) {
  var user_id = parseInt(req.params.user_id);
  db.collection('users').deleteOne({"_id": user_id});
  res.json();
});

module.exports = router;

// fake user
