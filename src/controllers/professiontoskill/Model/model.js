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
})

module.exports = mongoose.model('professiontoskill', dataSchema,"professiontoskill")