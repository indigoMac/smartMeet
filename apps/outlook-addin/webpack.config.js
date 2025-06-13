const path = require("path");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const CopyWebpackPlugin = require("copy-webpack-plugin");
const fs = require("fs");
const os = require("os");

module.exports = (env, argv) => {
  const isProduction = argv.mode === "production";

  // Path to the trusted Office dev certificates
  const certPath = path.join(os.homedir(), ".office-addin-dev-certs");
  const httpsOptions = {
    key: fs.readFileSync(path.join(certPath, "localhost.key")),
    cert: fs.readFileSync(path.join(certPath, "localhost.crt")),
  };

  return {
    entry: {
      taskpane: "./src/taskpane/index.tsx",
      commands: "./src/commands/commands.ts",
    },
    output: {
      path: path.resolve(__dirname, "dist"),
      filename: "[name].js",
      clean: true,
    },
    resolve: {
      extensions: [".ts", ".tsx", ".js", ".jsx"],
    },
    module: {
      rules: [
        {
          test: /\.tsx?$/,
          use: "ts-loader",
          exclude: /node_modules/,
        },
        {
          test: /\.css$/,
          use: ["style-loader", "css-loader"],
        },
        {
          test: /\.(png|jpg|jpeg|gif|svg)$/,
          type: "asset/resource",
        },
      ],
    },
    plugins: [
      new HtmlWebpackPlugin({
        template: "./src/taskpane/taskpane.html",
        filename: "taskpane.html",
        chunks: ["taskpane"],
      }),
      new HtmlWebpackPlugin({
        template: "./src/commands/commands.html",
        filename: "commands.html",
        chunks: ["commands"],
      }),
      new CopyWebpackPlugin({
        patterns: [
          {
            from: "manifest.xml",
            to: "manifest.xml",
          },
          {
            from: "manifest.dev.xml",
            to: "manifest.dev.xml",
          },
          {
            from: "src/assets",
            to: "assets",
          },
        ],
      }),
    ],
    devServer: {
      static: {
        directory: path.join(__dirname, "dist"),
      },
      port: 3000,
      hot: true,
      https: httpsOptions,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods":
          "GET, POST, PUT, DELETE, PATCH, OPTIONS",
        "Access-Control-Allow-Headers":
          "X-Requested-With, content-type, Authorization",
      },
    },
    mode: isProduction ? "production" : "development",
    devtool: isProduction ? "source-map" : "eval-source-map",
  };
};
