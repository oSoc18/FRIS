const path = require('path');

const config = {
    mode: 'development',
    entry: {
        app: './app.js'
    },
    output: {
        filename: 'bundle.js',
        path: path.resolve(__dirname, 'dist')
    },
    context: path.resolve(__dirname, 'src')
};

module.exports = config;