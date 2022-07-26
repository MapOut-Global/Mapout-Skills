const ProfessionToSkill = require('./Model/model');
const mongoose = require('mongoose');


module.exports = {

    search : async (req,res)=>{
      try{
        const {searchText} = req.query;
        let matchStageValue ;

        if(searchText){
           matchStageValue = { $text: { $search: searchText }}
        } else {
           matchStageValue = {}
        }

        const data = await ProfessionToSkill.aggregate([
            { $match:  matchStageValue },
            {
                $group: {
                     _id: {$toUpper: [{$substr: ['$profession', 0, 1]}]},
                     professions: {$push: '$profession'},
                }
            },
            {
                 $sort: {
                     _id: 1
                 }
            }
        ])

        //console.log(data.length);

        res.status(200).send(data);
      } catch(err){
        console.error(err);
        res.sendStatus(500);
      }
    }
}