const urlRegex = require("url-regex");
const { findPhoneNumbersInText, parsePhoneNumberFromString } = require("libphonenumber-js");

const { regular } = require("./dictionary");
const tldKeys = require("../../../resources/tld.keys");
const companyKeys = require("../../../resources/company.keys");
const collegeKeys = require("../../../resources/college.keys");
const jobTitleKeys = require("../../../resources/job-title.key");
const abbreviations = require("../score/degree/abbrevations.json");
const degreeKeys = require("../../../resources/degree.keys").map((o) => {
  return o.degree;
});

const getDate = (data) => {
  let dateObj = {
    dateArr: [],
    dateRegexArr: []
  };

  return new Promise((resolve, reject) => {
    data.forEach((o) => {
      o = o
        .replace(/[&\/\\#,.$~%":*?<>{}]/g, "")
        .trim()
        .replace(new RegExp("mar[d-z]", "i"), "")
        .replace(new RegExp("dec[f-z]", "i"), "")
        .replace(new RegExp("jun[f-z]", "i"), "");
      let match = o.match(
        new RegExp(
          /(\b\d{1,2}\D{0,3})?\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|(Nov|Dec)(?:ember)?)\D?(\d{1,2}(st|nd|rd|th)?)?(([,.\-\/])\D?)?((19[7-9]\d|20\d{2})|\d{2})*/gi,
          "gi"
        )
      );
      const prematch = o.match(/(Present|Current|Presen)/i);

      if (match) {
        if (match.length == 1 && prematch) {
          match.push("Present");
          dateObj.dateRegexArr.push(match);
          dateObj.dateArr.push(match.join(" - "));
        } else {
          dateObj.dateRegexArr.push(match);
          dateObj.dateArr.push(match.join(" - "));
        }
      }
    });

    resolve(dateObj);
  });
};

const getDegree = async (data) => {
  try {
    let arrDegree = new Array();
    const dataRegex = new RegExp(degreeKeys.join("|"));

    data.forEach((o) => {
      o = o
        .replace(/[&\/\\#,+()$~%":*?<>{}]/g, " ")
        .replace(/\MS Excel/gi, " ")
        .replace(/\MS Word/gi, " ")
        .replace(/\MS Office/gi, " ")
        .replace(/\MS SQL/gi, " ")
        .replace(/\MySQL/gi, " ")
        .replace(/\MySQL/gi, " ")
        .replace(/\MVC/gi, " ")
        // .replace(/\CGPA|GPA/gi, " ")
        // .replace(/[+-]?([0-9]*[.])?[0-9]+/gi, "")
        .replace(/\  /g, " ");
      let dateMatch = o.match(
        new RegExp(
          /(\b\d{1,2}\D{0,3})?\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|(Nov|Dec)(?:ember)?)\D?(\d{1,2}(st|nd|rd|th)?)?(([,.\-\/])\D?)?((19[7-9]\d|20\d{2})|\d{2})*/
        ),
        "gi"
      );
      let match = o.match(new RegExp(dataRegex));
      if (match && !dateMatch) {
        const matchDegree = filterDegree(match[0]);
        if (matchDegree == "Bachelor's") {
          const tempDegreeArr = match.input.trim().split(" ");
          if (tempDegreeArr.includes("Engineering")) {
            arrDegree.push("Bachelor of Technology");
          } else {
            arrDegree.push(match.input.trim());
          }
        } else {
          arrDegree.push(matchDegree);
        }
      }
    });

    arrDegree = [...new Set(arrDegree)];

    return arrDegree;
  } catch (error) {
    console.error(error);
    return "";
  }
};

const getCollege = async (data) => {
  try {
    let arrCollege = new Array();
    const dataRegex = new RegExp(collegeKeys.join("|"));

    data.forEach((o) => {
      o = o.replace(/\High School|college's|Boards/i, "");

      const headingMatch = o
        .replace(/[&#,.()$~%":*?<>{}]/g, "")
        .replace(new RegExp("()"), "")
        .replace(/ +/g, "")
        .match(/\w+\/\w+\/\w+/);

      let match = o.match(new RegExp(dataRegex, "i"));
      if (match && !headingMatch) {
        arrCollege.push(match.input.trim());
      }
    });

    return arrCollege;
  } catch (error) {
    console.error(error);
    return "";
  }
};

const getTitle = async (data) => {
  try {
    let arrTitle = new Array();
    const dataRegex = jobTitleKeys.join("|");

    data.forEach((o) => {
      let match = o.replace(new RegExp("Intern[a-z]", "i"), "").replace(new RegExp("Engineering", "i"), "").match(new RegExp(dataRegex, "i"));
      if (match) {
        if (
          !match.input.toLowerCase().includes(`${match[0].toLowerCase()}ship`) &&
          !match.input.toLowerCase().includes(`${match[0].toLowerCase()}ing`) &&
          !match.input.toLowerCase().includes("responsible") &&
          !match.input.toLowerCase().includes("with") &&
          !match.input.toLowerCase().includes("for")
        ) {
          arrTitle.push(
            match.input
              .replace(/[#,$~%"*?<>{}]/, " ")
              .replace(new RegExp("  "), " ")
              .trim()
          );
        }
      }
    });
    return arrTitle;
  } catch (error) {
    console.error(error);
    return "";
  }
};

const getCompany = async (data) => {
  try {
    let arrCompany = new Array();
    const dataRegex = companyKeys.join("|");

    data.forEach((o) => {
      let match = o.match(new RegExp(dataRegex));
      if (match) {
        arrCompany.push(match.input);
      }
    });

    return arrCompany;
  } catch (error) {
    console.error(error);
    return "";
  }
};

const getContact = (data) => {
  let parse_contact = findPhoneNumbersInText(data);

  if (parse_contact.length) {
    const phoneNumber = parsePhoneNumberFromString(parse_contact[0].number.number);
    return phoneNumber.formatInternational();
  } else {
    let match = data.match(new RegExp(regular.phone[0])) || [""];

    match = match
      .map((n) => {
        if (n.length >= 10) {
          return n.trim();
        }
      })
      .filter(Boolean);

    return match[0];
  }
};

const getWebsite = (data) => {
  const tldRegex = new RegExp(tldKeys.join("|"));
  const degreeRegex = new RegExp(degreeKeys.join("|"));
  let matches = data.match(urlRegex({ strict: false })) || [""];

  matches = matches.filter((o) => {
    if (
      !o.match(new RegExp(regular.email[0])) &&
      !o.match(new RegExp(degreeRegex), "i") &&
      !o.match(new RegExp("asp.net"), "i") &&
      o.match(new RegExp(tldRegex))
    ) {
      return o;
    }
  });
  return matches[0];
};

const filterDegree = (degree) => {
  let matchDegree;
  const secondary = ["Secondary", "10th", "10TH", "High School", "Class X"];
  const higherSecondary = ["Higher Secondary", "12th", "12TH", "10+2", "Intermediate", "Class XII"];

  for (i = 0; i < abbreviations.length; i++) {
    let data = abbreviations[i];
    if (degree.match(new RegExp(data.degree), "i")) {
      matchDegree = data.degree;
      break;
    } else if (degree.match(new RegExp(data.abbreviation.join("|")), "i")) {
      matchDegree = data.degree;
      break;
    }
  }

  if (!matchDegree) {
    if (secondary.includes(degree)) {
      matchDegree = secondary[0];
    } else if (higherSecondary.includes(degree)) {
      matchDegree = higherSecondary[0];
    } else {
      matchDegree = degree;
    }
  }

  return matchDegree;
};

module.exports = {
  getDate,
  getDegree,
  getCollege,
  getTitle,
  getCompany,
  getContact,
  getWebsite
};
