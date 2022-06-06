const axios = require("axios");
const emsiCred = require("../../../config/emsi.json");
const qs = require("qs");

module.exports = async () => {
  try {
    let token = await cache.getAsync("token");
    if (token) return token;

    let client_id = await cache.getAsync("emsi_clientId");
    let client_secret = await cache.getAsync("emsi_secret");

    if (!client_id || !client_secret) {
      client_id = emsiCred[0].id;
      client_secret = emsiCred[0].secret;
      await cache.setAsync("emsi_index", 0);
      await cache.setAsync("emsi_clientId", client_id);
      await cache.setAsync("emsi_secret", client_secret);
    }

    const options = {
      method: "post",
      url: "https://auth.emsicloud.com/connect/token",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded"
      },
      data: qs.stringify({
        client_id,
        client_secret,
        grant_type: "client_credentials",
        scope: "emsi_open"
      })
    };

    token = await axios(options).then((res) => {
      return res.data.access_token;
    });

    await cache.setAsync("token", token);

    return token;
  } catch (error) {
    console.log("error?>>>", error.message);
    throw error;
  }
};
