const fs = require("fs");
const axios = require("axios");
const textract = require("textract");
const getSkills = require("../emsi/skills");
const { titles, regular } = require("./dictionary");
const { getDate, getDegree, getCollege, getTitle, getCompany, getContact, getWebsite } = require("./resume.data");

module.exports = async (req, res) => {
  try {
    let resumeArr = new Array();
    let match = new Array();
    let resObj = new Object();

    //conacat arrays of title
    let allTitles = [].concat(...Object.values(titles));
    const allTitlesRegex = allTitles.join("|");
    const { link } = await req.body;

    console.log(`/api/resume | ${link}`);

    const resumeName = await getResumePath(link);

    console.log("resumeName |", resumeName);

    //parse text from pdf link
    const resumeData = await new Promise((resolve, reject) => {
      setTimeout(() => {
        textract.fromUrl(
          `${process.env.HOSTNAME}/get/resume/${resumeName}`,
          {
            preserveLineBreaks: true
          },
          (err, data) => {
            if (err) {
              reject(err);
            } else {
              resolve(data);
            }
          }
        );
      }, 2500);
    });

    //parse name | email | contact | website
    let name = resumeData.match(new RegExp(regular.name[0], "gm")) || [""];
    let email = resumeData.match(new RegExp(regular.email[0])) || [""];
    let contact = getContact(resumeData);
    let profile = getWebsite(resumeData);
    let skills = await getSkills(resumeData);

    resObj.name = name[0].trim();
    resObj.email = email[0].trim();
    resObj.contact = contact;
    resObj.profile = profile;
    resObj.skills = skills.core;

    resumeArr = await cleanTextByRows(resumeData);

    resumeArr = resumeArr.map((o) => {
      return o.trim();
    });

    //get resume titles' name & index (Eg. Education, Experience, etc)
    //resLen filters the data if title length > 3
    resumeArr.forEach((res, idx) => {
      let resLen = res.split(" ").length;
      let tmatch = res.match(new RegExp(allTitlesRegex, "i"));
      if (tmatch && resLen <= 3) {
        match.push({ idx, res: res.trim(), tmatch: tmatch[0] });
      }
    });
    //if match array is empty it removes resLen filter
    if (!match.length) {
      resumeArr.forEach((res, idx) => {
        let tmatch = res.match(new RegExp(allTitlesRegex, "i"));
        if (tmatch) {
          match.push({ idx, res: res.trim(), tmatch: tmatch[0] });
        }
      });
    }

    //filter array with unique titles
    match = getUniqueListBy(match, "tmatch");

    //segregate the matched array into required keys
    for (i in match) {
      i = Number(i);
      let start = match[i].idx + 1;
      let end = resumeArr.length - 1;
      if (match[i + 1]) {
        end = match[i + 1].idx;
      }

      if (match[i].res.match(new RegExp("Experie", "i"))) {
        resObj.experience = await splitExp(resumeArr.slice(start, end));
      } else if (match[i].res.match(new RegExp("Skills", "i")) && !resObj.skills) {
        resObj.skills = resumeArr.slice(start, end);
      } else if (match[i].res.match(new RegExp("Education", "i"))) {
        resObj.education = await splitEdu(resumeArr.slice(start, end));
      }
    }

    res.status(200).send(resObj);
  } catch (error) {
    console.error(error);
    res.status(500).send({
      status: false,
      message: error.message
    });
  }
};

//  download resume to temp folder
const getResumePath = async (link) => {
  const tmpfileName = Date.now() + ".pdf";
  axios({
    method: "get",
    url: link,
    responseType: "stream"
  }).then((response) => {
    if (!fs.existsSync(__basedir + "/resources/temp/resume")) {
      fs.mkdirSync(__basedir + "/resources/temp/resume", { recursive: true });
    }
    response.data.pipe(fs.createWriteStream(__basedir + `/resources/temp/resume/${tmpfileName}`));
  });
  return tmpfileName;
};

//convert parsed text to rows
const cleanTextByRows = async (data) => {
  let rows,
    clearRows = new Array();

  rows = data.split("\n");

  clearRows = rows.map((element) => {
    if (element.length > 2) {
      return cleanStr(element);
    }
  });

  return clearRows.filter(Boolean);
};

//removes noises
const cleanStr = (str) => {
  return str.replace(/\r?\n|\r|\t|\n/g, "").trim();
};

//filter array with unique titles
const getUniqueListBy = (arr, key) => {
  return [...new Map(arr.map((item) => [item[key].toLowerCase(), item])).values()];
};

//split education array into degree, college, date
const splitEdu = async (data) => {
  const concatArr = new Array();
  const { dateArr, dateRegexArr } = await getDate(data);
  const degreeArr = await getDegree(data);
  const collegeArr = await getCollege(data);
  const dateRegex = new RegExp(dateRegexArr.flat().join("|"), "ig");

  let largestLen = [dateArr.length, degreeArr.length, collegeArr.length].sort((a, b) => {
    return b - a;
  })[0];

  for (i = 0; i < largestLen; i++) {
    const date = dateArr[i] || "";
    concatArr.push({
      college: collegeArr[i]
        ? collegeArr[i]
            .replace(dateRegex, "")
            .replace(/(  -|  – |  –)/i, "")
            .trim()
        : "",
      degree: degreeArr[i]
        ? degreeArr[i]
            .replace(dateRegex, "")
            .replace(/(  -|  – |  –)/i, "")
            .trim()
        : "",
      date
    });
  }

  return concatArr;
};

//split experience array into title, company, date
const splitExp = async (data) => {
  try {
    const concatArr = new Array();
    const { dateArr, dateRegexArr } = await getDate(data);
    const titleArr = await getTitle(data);
    const companyArr = await getCompany(data);
    const dateRegex = new RegExp(dateRegexArr.flat().join("|"), "ig");

    for (i = 0; i < titleArr.length; i++) {
      concatArr.push({
        title: titleArr[i]
          ? titleArr[i]
              .replace(dateRegex, "")
              .replace(/(  -|  – |  –)/i, "")
              .trim()
          : "",
        company: companyArr[i]
          ? companyArr[i]
              .replace(dateRegex, "")
              .replace(/(  -|  – |  –)/i, "")
              .trim()
          : "",
        date: dateArr[i] || ""
      });
    }

    return concatArr;
  } catch (error) {
    console.error("error");
    return "";
  }
};
