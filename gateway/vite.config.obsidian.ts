import { defineConfig, type Plugin } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import path from 'path';
import { builtinModules } from 'module';
import fs from 'fs';

// All Node.js built-in modules (available in Electron runtime)
const nodeBuiltins = builtinModules.flatMap((m) => [m, `node:${m}`]);

// Copy manifest.json to dist after build
function copyManifest(): Plugin {
  return {
    name: 'copy-manifest',
    closeBundle() {
      fs.copyFileSync(
        path.resolve(__dirname, 'manifest.json'),
        path.resolve(__dirname, 'dist-obsidian/manifest.json'),
      );
    },
  };
}

// Fix Vite's broken __dirname polyfill for Electron/CJS.
// Vite converts ESM `import.meta.url` to a browser-aware polyfill that uses document.baseURI,
// which produces `app://obsidian.md/main.js` in Electron — not a file:// URL.
// fileURLToPath() then throws "The URL must be of scheme file".
// Since this is a CJS bundle, __dirname and __filename are already available natively.
function fixDirnamePolyfill(): Plugin {
  return {
    name: 'fix-dirname-polyfill',
    writeBundle() {
      const mainPath = path.resolve(__dirname, 'dist-obsidian/main.js');
      let code = fs.readFileSync(mainPath, 'utf-8');
      let fixes = 0;

      // Fix `const __dirname$1 = path.dirname(url.fileURLToPath(<polyfill>));`
      // → `const __dirname$1 = __dirname;`
      code = code.replace(
        /const __dirname\$1=[^;]*fileURLToPath[^;]*;/g,
        () => { fixes++; return 'const __dirname$1=__dirname;'; },
      );

      // Fix all remaining Vite import.meta.url polyfills → `__filename`
      // Use exact string replacement (not regex) to avoid backtracking on 10MB file.
      const polyfill = 'url.fileURLToPath(typeof document>"u"?require("url").pathToFileURL(__filename).href:_documentCurrentScript&&_documentCurrentScript.tagName.toUpperCase()==="SCRIPT"&&_documentCurrentScript.src||new URL("main.js",document.baseURI).href)';
      while (code.includes(polyfill)) {
        code = code.replace(polyfill, '__filename');
        fixes++;
      }

      if (fixes > 0) {
        fs.writeFileSync(mainPath, code);
        console.log(`  fix-dirname-polyfill: replaced ${fixes} Vite polyfill(s)`);
      }
    },
  };
}

// Wrap require() calls for optional packages that may not exist at runtime
// so they don't crash the plugin on load
function safeRequires(): Plugin {
  const optionalPackages = [
    '@emotion/is-prop-valid',
    'ajv-formats/dist/formats',
    'ajv/dist/runtime/equal',
    'ajv/dist/runtime/ucs2length',
    'ajv/dist/runtime/uri',
    'ajv/dist/runtime/validation_error',
  ];
  return {
    name: 'safe-requires',
    renderChunk(code) {
      let result = code;
      for (const pkg of optionalPackages) {
        // Replace require("pkg") with a try/catch that returns empty object on failure
        const escaped = pkg.replace(/[.*+?^${}()|[\]\\\/]/g, '\\$&');
        const pattern = new RegExp(`require\\("${escaped}"\\)`, 'g');
        result = result.replace(
          pattern,
          `(function(){try{return require("${pkg}")}catch(e){return{}}})()`,
        );
      }
      return { code: result, map: null };
    },
  };
}

// Electron compatibility: patch Node.js APIs that reject browser AbortSignal.
// In Electron's renderer, `new AbortController().signal` is a Chromium Web API AbortSignal,
// not a Node.js EventTarget. Node.js APIs like child_process.spawn() and
// events.setMaxListeners() reject it with "must be EventEmitter or EventTarget".
// This preamble monkey-patches both APIs to handle browser AbortSignals gracefully.
function patchElectronCompat(): Plugin {
  return {
    name: 'patch-electron-compat',
    writeBundle() {
      const mainPath = path.resolve(__dirname, 'dist-obsidian/main.js');
      let code = fs.readFileSync(mainPath, 'utf-8');

      const preamble = `
(function(){
  var cp=require("child_process"),origSpawn=cp.spawn;
  cp.spawn=function(cmd,args,opts){
    if(opts&&opts.signal){
      var sig=opts.signal;
      opts=Object.assign({},opts);
      delete opts.signal;
      var proc=origSpawn.call(this,cmd,args,opts);
      if(sig.aborted){proc.kill("SIGTERM");}
      else{sig.addEventListener("abort",function(){if(!proc.killed)proc.kill("SIGTERM");});}
      return proc;
    }
    return origSpawn.call(this,cmd,args,opts);
  };
  var ev=require("events"),origSML=ev.setMaxListeners;
  ev.setMaxListeners=function(){
    try{return origSML.apply(this,arguments);}
    catch(e){if(e&&e.code==="ERR_INVALID_ARG_TYPE")return;throw e;}
  };
})();
`;

      // Prepend after "use strict"; if present, otherwise at the top
      if (code.startsWith('"use strict";')) {
        code = '"use strict";' + preamble + code.slice('"use strict";'.length);
      } else {
        code = preamble + code;
      }

      fs.writeFileSync(mainPath, code);
      console.log('  patch-electron-compat: patched spawn() and setMaxListeners() for Electron');
    },
  };
}

export default defineConfig({
  plugins: [react(), tailwindcss(), copyManifest(), safeRequires(), fixDirnamePolyfill(), patchElectronCompat()],
  build: {
    lib: {
      entry: path.resolve(__dirname, 'src/plugin/main.ts'),
      formats: ['cjs'],
      fileName: () => 'main.js',
    },
    rollupOptions: {
      external: [
        'obsidian', 'electron',
        '@codemirror/autocomplete', '@codemirror/collab', '@codemirror/commands',
        '@codemirror/language', '@codemirror/lint', '@codemirror/search',
        '@codemirror/state', '@codemirror/view',
        '@lezer/common', '@lezer/highlight', '@lezer/lr',
        // Node.js built-ins available in Electron runtime
        ...nodeBuiltins,
      ],
      output: {
        // Obsidian requires a single main.js file - no code splitting
        inlineDynamicImports: true,
        // Ensure `export default` maps to `module.exports`
        exports: 'default',
        // Obsidian expects styles.css (not the default lib name)
        assetFileNames: 'styles.[ext]',
      },
    },
    outDir: 'dist-obsidian',
    emptyOutDir: true,
    sourcemap: 'inline',
    cssCodeSplit: false,
    // Target node for Electron compatibility (prevents browser externalization)
    target: 'node18',
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src/client'),
      '@shared': path.resolve(__dirname, 'src/shared'),
    },
  },
});
