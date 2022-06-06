const keys = require("../../../resources/college.keys");

module.exports = {
  college: async (desc) => {
    try {
      let data = await desc.replace(/[\/\\#+()$~%"*?<>{}]/g, " ").trim();

      const match = data.match(new RegExp(keys.join("|"), "i"));

      if (match) {
        return data;
      }
    } catch (error) {
      console.error(error);
      return "";
    }
  },
};
