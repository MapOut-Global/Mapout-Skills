const redis = require("redis");
const { promisify } = require("util");

const REDIS_HOST = process.env.REDIS_HOST;
const REDIS_PORT = process.env.REDIS_PORT || 6379;
const password = process.env.REDIS_PASSWORD || null;

const redisClient = redis.createClient({
  host: REDIS_HOST,
  port: REDIS_PORT
});

if (password) {
  redisClient.auth(password, (err, res) => {
    console.log("res", res);
    console.error("err", err);
  });
}

try {
  redisClient.getAsync = promisify(redisClient.get).bind(redisClient);
  redisClient.setAsync = promisify(redisClient.set).bind(redisClient);
  redisClient.lpushAsync = promisify(redisClient.lpush).bind(redisClient);
  redisClient.lrangeAsync = promisify(redisClient.lrange).bind(redisClient);
  redisClient.llenAsync = promisify(redisClient.llen).bind(redisClient);
  redisClient.lremAsync = promisify(redisClient.lrem).bind(redisClient);
  redisClient.lsetAsync = promisify(redisClient.lset).bind(redisClient);
  redisClient.hmsetAsync = promisify(redisClient.hmset).bind(redisClient);
  redisClient.hmgetAsync = promisify(redisClient.hmget).bind(redisClient);
  redisClient.clear = promisify(redisClient.del).bind(redisClient);
} catch (error) {
  console.error("redis error", error);
}

redisClient.on("connect", () => {
  console.log("Redis is connected");
});
redisClient.on("error", (err) => {
  //console.error("Redis error.", err);
});

global.cache = redisClient;
module.exports = redisClient;
