const path = require('path')
module.exports = {
  // 关键：禁用 ESLint 校验，防止构建时报错
  lintOnSave: false,
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
