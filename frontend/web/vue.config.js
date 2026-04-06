const path = require('path')
module.exports = {
  // 让 Webpack 4 用 Babel 转译 element-plus 及其依赖的 ES2021+ 语法
  transpileDependencies: ['element-plus', '@ctrl/tinycolor'],
  publicPath: '/',
  outputDir: 'dist',
  assetsDir: 'static',
  productionSourceMap: false,
  devServer: {
    hot: true,
    port: 8010,
    open: true,
    proxy: {
      '/': {
        target: 'http://127.0.0.1:8000/',
        changeOrigin: true,
        pathRewrite: { '^/': '' },
      },
    },
  },
  configureWebpack: {
    name: 'system',
    resolve: {
      alias: {
        "~@": __dirname,
        "@": path.resolve(__dirname, "./src")
      }
    }
  },
}
