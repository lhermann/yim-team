var webpack = require("webpack");
var path = require("path");
var PROD = process.env.NODE_ENV === "production";

module.exports = {
    entry: "./static/_webpack/main.js",
    output: {
        filename: "bundle.js",
        path: path.resolve(__dirname, "static/js/")
    },
    devtool: "source-map",
    target: "node",
    plugins: [
        new webpack.DefinePlugin({
            "process.env": {
                NODE_ENV: '"production"'
            }
        })
    ]
};
