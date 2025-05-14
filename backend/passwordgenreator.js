const bcrypt = require('bcrypt');

const plainPassword = 'password';
const saltRounds = 10;

bcrypt.hash(plainPassword, saltRounds, (err, hash) => {
    if (err) {
        console.error(err);
        return;
    }
    console.log('Generated Hash:', hash);
});