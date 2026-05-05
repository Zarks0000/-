import fs from 'node:fs'
import path from 'node:path'

const projectRoot = process.cwd()

function readEnvValue(filePath, key) {
  if (!fs.existsSync(filePath)) return ''
  const lines = fs.readFileSync(filePath, 'utf8').split(/\r?\n/)
  for (const line of lines) {
    const trimmed = line.trim()
    if (!trimmed || trimmed.startsWith('#')) continue
    const index = trimmed.indexOf('=')
    if (index < 0) continue
    if (trimmed.slice(0, index).trim() !== key) continue
    return trimmed.slice(index + 1).trim().replace(/^['"]|['"]$/g, '')
  }
  return ''
}

const wechatAppId =
  process.env.WECHAT_APPID ||
  readEnvValue(path.join(projectRoot, 'api', '.env'), 'WECHAT_APPID') ||
  'touristappid'

const baseConfig = {
  description: '项目配置文件。',
  packOptions: {
    ignore: [],
    include: [],
  },
  setting: {
    urlCheck: false,
    es6: true,
    postcss: false,
    minified: false,
    compileWorklet: false,
    uglifyFileName: false,
    uploadWithSourceMap: false,
    enhance: false,
    packNpmManually: false,
    packNpmRelationList: [],
    minifyWXSS: true,
    minifyWXML: true,
    localPlugins: false,
    disableUseStrict: false,
    useCompilerPlugins: false,
    condition: false,
    swc: false,
    disableSWC: true,
    babelSetting: {
      ignore: [],
      disablePlugins: [],
      outputPath: '',
    },
  },
  compileType: 'miniprogram',
  libVersion: '3.15.2',
  appid: wechatAppId,
  projectname: '摩旅客',
  condition: {},
  editorSetting: {
    tabIndent: 'insertSpaces',
    tabSize: 2,
  },
}

const privateConfig = {
  projectname: 'mp-weixin',
  setting: {
    urlCheck: false,
    coverView: false,
    lazyloadPlaceholderEnable: false,
    skylineRenderEnable: false,
    preloadBackgroundData: false,
    autoAudits: false,
    useApiHook: true,
    showShadowRootInWxmlPanel: false,
    useStaticServer: false,
    useLanDebug: false,
    showES6CompileOption: false,
    compileHotReLoad: true,
    checkInvalidKey: true,
    ignoreDevUnusedFiles: true,
    bigPackageSizeSupport: false,
  },
  libVersion: '3.15.2',
  condition: {},
}

function writeJson(filePath, value) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true })
  try {
    fs.writeFileSync(filePath, `${JSON.stringify(value, null, 2)}\n`, 'utf8')
  } catch (error) {
    if (error && error.code === 'EPERM') {
      console.warn(`Skipped locked file: ${filePath}`)
      return
    }
    throw error
  }
}

function syncTarget(dir, miniprogramRoot) {
  if (!fs.existsSync(dir)) return

  writeJson(
    path.join(dir, 'project.config.json'),
    {
      ...baseConfig,
      miniprogramRoot,
    },
  )

  writeJson(path.join(dir, 'project.private.config.json'), privateConfig)
}

writeJson(
  path.join(projectRoot, 'project.config.json'),
  {
    ...baseConfig,
    miniprogramRoot: 'dist/build/mp-weixin/',
  },
)

writeJson(path.join(projectRoot, 'project.private.config.json'), privateConfig)

syncTarget(path.join(projectRoot, 'dist', 'dev', 'mp-weixin'), './')
syncTarget(path.join(projectRoot, 'dist', 'build', 'mp-weixin'), './')

console.log('Synced WeChat project configs.')
