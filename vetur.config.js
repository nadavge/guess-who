// vetur.config.js
/** @type {import('vls').VeturConfig} */
module.exports = {

    projects: [
        'guess-who-client', // shorthand for only root.
        {
            root: './client/guess-who',

            globalComponents: [
                './src/components/**/*.vue'
            ]
        }
    ]
}