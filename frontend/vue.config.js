const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  devServer: {
      port: 8082,
  },
  lintOnSave: false
})
