const keys = require("../../../resources/job-type.keys");

module.exports = {
  job_type: async (desc) => {
    try {
      let descrption = await desc;

      descrption = descrption.replace(/[&\/\\#,+()$~%":*?<>{}]/g, " ");

      let match = descrption.match(new RegExp(keys.join("|"), "i"));

      if (!match) return "";

      //removes white spaces
      match = match.map((word) => {
        return word.trim();
      });

      //removes data if not found in degree.keys
      match = match.filter((x) => {
        return keys.some((y) => {
          return x.toLowerCase() == y.toLowerCase();
        });
      });

      return capitalizeFirstLetter(match[0]);
    } catch (error) {
      console.error(error);
      return "";
    }
  }
};

const capitalizeFirstLetter = (string) => {
  return string[0].toUpperCase() + string.slice(1).toLowerCase();
};
