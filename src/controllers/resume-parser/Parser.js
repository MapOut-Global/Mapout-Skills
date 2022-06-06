const { json } = require("express/lib/response");
const { PythonShell } = require("python-shell");
const mongoose = require('mongoose');
const parsedData = require("./Model/parsermodel");
const { collection } = require("./Model/parsermodel");

const MongoClient = require('mongodb').MongoClient
const uri = 'mongodb+srv://mapout:mapout@mapoutdb.hj2on.mongodb.net/mapout-staging?authSource=admin&replicaSet=atlas-1389yt-shard-0&w=majority&readPreference=primary&appname=MongoDB%20Compass&retryWrites=true&ssl=true'
const client = new MongoClient(uri)
const connection = client.connect() // initialized connection

module.exports = async (req , res) => {
//console.log("/api/resume-parser  | ", req.body);
//console.log("the link  :  ", req.body.url);
  try {
    var userID = req.query.userID
    var url = req.query.url
    //console.log("URL : ",url)
    let options = {
      mode: "text",
      pythonOptions: ["-u"],
      pythonPath: "python3",
      args: [url] 
      //args : ["https://demo1-app-bucket.s3.ap-south-1.amazonaws.com/sample_resume_2021.pdf"]
    };  

    const result = await new Promise((resolve, reject) => {
      PythonShell.run("./src/controllers/resume-parser/resume_parser.py", options, (err, result) => {
        if (err) {
          reject(err);
        } else {
          resolve(result);  
        }
      });
    });
    //console.log(result[0])
    //console.log(typeof result)
    //console.log(typeof result[0])
    let result1 = result[0].replace(/"/g,'')
    //console.log(result1)
    let result2 = result1.replace(/'/g,'"')
    console.log(result2)
    var final = result2.replace(String.fromCharCode(92),String.fromCharCode(92,92));
    data = JSON.parse(final)
    console.log("parsed data");
        
    let isExists = await parsedData.find({ user_id: mongoose.Types.ObjectId(userID) });
    myquery = {user_id : mongoose.Types.ObjectId(userID)}
    let mongooseData = {
    user_id: mongoose.Types.ObjectId(userID),
    education: data.education,
    technical_skills: data.coreskills,
    soft_skills: data.softskills,
    experience: data.experience,
    }
    if (isExists.length == 0) {
    const rp = new parsedData(mongooseData);
    rp.save();
    }
    else{
    let updateData = {
    $set : {
    updatedAt: new Date(),
    education: data.education,
    technical_skills: data.coreskills,
    soft_skills: data.softskills,
    experience: data.experience
    }
    }

    const connect = connection
    connect.then(() => {
        const db = client.db('mapout-test')
        const coll = db.collection('parserAccuracy')
        coll.findOneAndUpdate(myquery,updateData,{upsert:true})
        //console.log(coll.find({}))
    })
    
    console.log("Updated")
    //parsedData.save()
    //rp.save();
    }
    console.log("DONE")
   
    //console.log(JSON.parse(result2))
    //let json1 = JSON.parse(result);
    //let result1 = result
    //console.log(result1.replace(/'/g, '"'));
    //console.log(typeof result1);
    //console.log(result1.toString().replaceAll(`'`,`"`))
    //console.log(result[0].replaceAll("'",'"'))
    res.status(200).send({ status: true, data: data });  
  }
   catch (error) {
    console.error(error.message);
    res.status(500).send({
      status: false,
      message: "Something went wrong",
      error: error.message
    });
  }
};


