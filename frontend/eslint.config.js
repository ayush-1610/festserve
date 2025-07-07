const js = require('@eslint/js');
const react = require('eslint-plugin-react');
const reactHooks = require('eslint-plugin-react-hooks');
const babelParser = require('@babel/eslint-parser');
const globals = require('globals');

const browserGlobals = Object.fromEntries(
  Object.entries(globals.browser).map(([k, v]) => [k.trim(), v])
);

module.exports = [
  {
    files: ['**/*.{js,jsx}'],
    languageOptions: {
      parser: babelParser,
      parserOptions: {
        requireConfigFile: false,
        ecmaFeatures: { jsx: true },
        babelOptions: {
          presets: ['@babel/preset-react']
        }
      },
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: browserGlobals
    },
    plugins: {
      react,
      'react-hooks': reactHooks
    },
    settings: {
      react: {
        version: 'detect'
      }
    },
    rules: {
      ...js.configs.recommended.rules,
      ...react.configs.recommended.rules,
      ...reactHooks.configs.recommended.rules
    }
  }
];
