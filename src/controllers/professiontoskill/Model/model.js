const mongoose = require('mongoose');

const dataSchema = new mongoose.Schema({
    profession: {
        required: true,
        type: String
    },
    necessary_skills: {
        required: true,
        type: Array
    },
    helpful_skills: {
        required: true,
        type: Array
    },
    counter: {
        required: false,
        type: Object
    }
});

// dataSchema.index({'profession': "text"}, {default_language: 'english'});

const ProfessionToSkill = mongoose.model('professiontoskill', dataSchema,"professiontoskill")
module.exports = ProfessionToSkill;
