var uuid = require('node-uuid');

// 全局匹配并替换
console.log(uuid.v4().replace(/-/g, ''));
