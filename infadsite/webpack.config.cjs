const path = require('path');

module.exports = {
  entry: './mythgarden/static/mythgarden/js/script.ts',
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env', '@babel/preset-react', '@babel/preset-typescript'],
          }
        },
        exclude: /node_modules/,
      },
    ],
  },
  mode: 'development',
  watch: true,
  resolve: {
    extensions: ['.tsx', '.ts', '.js'],
  },
  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, './mythgarden/static/mythgarden/dist'),
  },
};