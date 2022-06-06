const axios = require("axios");
const FormData = require("form-data");
const getToken = require("./auth");
const fetch = require("node-fetch");
const emsiCred = require("../../../config/emsi.json");

// const getEmsiCred = async () => {
//   let i = Number(await cache.getAsync("emsi_index")) + 1;
//   if (i >= emsiCred.length - 1) i = 0;
//   await Promise.all([cache.setAsync("emsi_index", i), cache.setAsync("emsi_clientId", emsiCred[i].id), cache.setAsync("emsi_secret", emsiCred[i].secret)]);
// };

// module.exports = async (desc) => {
//   try {
//     let result;
//     let core = [];
//     let soft = [];
//     let descrption = desc.replace(/\./g, " ").replace(/\,/g, " ").replace(/\//g, " ");

//     result = await extract(descrption);

//     if (result.message) {
//       console.warn("EMSI Credentials expired");
//       await cache.clear("token");
//       await getEmsiCred();
//       result = await extract(descrption);
//     }

//     const skillsArr = result.data.skills;

//     for (i of skillsArr) {
//       if (i.skill.type.name == "Hard Skill") {
//         core.push(i.skill.name);
//       } else {
//         soft.push(i.skill.name);
//       }
//     }

//     return { core, soft };
//   } catch (error) {
//     console.error(error);
//     return "";
//   }
// };

// // EMSI data extract
// const extract = async (desc) => {
//   try {
//     const token = await getToken();

//     const options = {
//       method: "POST",
//       headers: {
//         authorization: `Bearer ${token}`,
//         "content-type": "application/json"
//       },
//       body: JSON.stringify({ text: desc }),
//       json: true
//     };

//     const result = await fetch("https://emsiservices.com/skills/versions/latest/extract/trace", options)
//       .then((res) => res.json())
//       .then((json) => {
//         return json;
//       });

//     return result;
//   } catch (error) {
//     throw new Error(error);
//   }
// };

module.exports = async (desc) => {
  try {
    let skill_data = {
      core: [],
      soft: []
    };

    if (!desc) return skill_data;

    let data = new FormData();
    data.append("text", desc);

    const config = {
      method: "post",
      url: "http://score.mapout.com/skills/skill_extractor",
      headers: {
        ...data.getHeaders()
      },
      data: data
    };
    const result = await axios(config).then((response) => {
      return response.data;
    });

    skill_data.soft = result["SOFT SKILL"]
      ? result["SOFT SKILL"].map((d) => {
          return d[0].replace(/(^|\s)\S/g, (letter) => letter.toUpperCase());
        })
      : [];
    skill_data.core = result["HARD SKILL"]
      ? result["HARD SKILL"].map((d) => {
          return d[0].replace(/(^|\s)\S/g, (letter) => letter.toUpperCase());
        })
      : [];

    return skill_data;
  } catch (error) {
    throw error;
  }
};
