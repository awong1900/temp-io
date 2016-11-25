var express = require('express');
var router = express.Router();
var request = require('request');
var uuid = require('node-uuid');

var github = "github"
var weixin = "weixin"
var facebook = "facebook"

/* GET users listing. */
router.get('/', function(req, res, next) {
  // console.log(req.query);
  var type = req.query.type || null;
  var access_token = req.query.access_token || null;

  console.log(type);
  console.log(access_token);
  if (!type || !access_token) {
    res.status(401).json({
      message: "Auth Error."
    });
  }

  if (type == github) {
    var options = {
      url: 'https://api.github.com/user?access_token=' + access_token,
      headers: {
        'User-Agent': 'zuqiuxunlian'
      }
    }
    request(options, function (error, response, body) {
      if (!error && response.statusCode == 200) {
        var github_user = JSON.parse(body);

        db.collection('users').findOne({'github_id': github_user.id}, {"token": 1, "_id": 0}, function (err, user) {
          console.log(user);
          if (!user) {
            var token = uuid.v4().replace(/-/g, '');
            getNextSequence('user_id', function (err, user_id) {
              db.collection('users').insertOne({
                id: user_id,
                github_id: github_user.id,
                avatar_url: github_user.avatar_url,
                token: token,
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString()
              });
              res.json({
                token: token
              });
            });
          } else {
            res.json(user);
          }
        });
      } else {
        res.send('no');
      }
    });
  } else if(type == weixin) {
    res.json({});
  } else if (type == facebook) {
    var options = {
      url: 'https://graph.facebook.com/me?access_token=' + access_token,
      headers: {
        'User-Agent': 'zuqiuxunlian'
      }
    }
    request(options, function (error, response, body) {
      if (!error) {
        var fb_user = JSON.parse(body);

        db.collection('users').findOne({'facebook_id': fb_user.id}, {"token": 1, "_id": 0}, function (err, user) {
          console.log(user);
          if (!user) {
            var token = uuid.v4().replace(/-/g, '');;
            getNextSequence('user_id', function (err, user_id) {
              db.collection('users').insertOne({
                id: user_id,
                facebook_id: fb_user.id,
                avatar_url: fb_user.avatar_url,
                token: token,
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString()
              });
              res.json({
                token: token
              });
            });
          } else {
            res.json(user);
          }
        });
      } else {
        res.send('no');
      }
    });
  }else {
    res.send('respond with a resource');
  }

});

function getNextSequence(name, callback) {
  db.collection('counters').findOneAndUpdate(
    {_id: name},
    { $inc: { seq: 1 } },
    {
      returnOriginal: false,
      upsert: true
    },
    function (err, r) {
      if (err) callback(err);
      callback(null, r.value.seq);
    }
  );
}

module.exports = router;
