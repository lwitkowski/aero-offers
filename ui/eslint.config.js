import eslint from '@eslint/js'
import pluginVue from 'eslint-plugin-vue'
import eslintPluginPrettierRecommended from 'eslint-plugin-prettier/recommended'

export default [
  {
    files: ['**/*.vue', '**/*..js', '**/*..jsx', '**/*..cjs', '**/*..mjs']
  },
  {
    ignores: ['dist/*']
  },
  eslint.configs.recommended,
  ...pluginVue.configs['flat/recommended'],
  eslintPluginPrettierRecommended
]
