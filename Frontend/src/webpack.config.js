const path = require('path');
const webpack = require('webpack');
const HtmlWebpackPlugin = require('html-webpack-plugin');

const config = {
    mode: 'development',
    entry: {
        app: './app.js'
    },
    output: {
        filename: 'bundle.js',
        path: path.resolve(__dirname, 'dist'),
        publicPath: '/static/'
    },
    context: path.resolve(__dirname, 'src'),
    devServer: {
        port: 3000,

    },
    devtool: 'inline-source-map',
    plugins: [
        new HtmlWebpackPlugin()
    ]
};

module.exports = config;