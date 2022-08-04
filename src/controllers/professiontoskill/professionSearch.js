const ProfessionToSkill = require('./Model/model');

module.exports = {
    search : async (req,res)=>{
      try{
        const {searchText} = req.query;

        const executeQuery =  ({match}) => ProfessionToSkill.aggregate([
          { $match:  match },
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
        ]);

        const regExpResult = await executeQuery({
          match: {
            profession: new RegExp(searchText, 'i'),
          }
        });

        res.status(200).json(regExpResult);
      } catch(err){
        console.error(err);
        res.sendStatus(500);
      }
    }
}
