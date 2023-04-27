#!/usr/bin/node
const esbuild = require('esbuild');
const copyStaticFiles = require('esbuild-copy-static-files');

const args = process.argv.slice(2);
const mode = args.includes('--watch') ? 'watch' : 'build';

const projectDirectory = process.env.PACKAGE_NAME;

const plugins = [
    copyStaticFiles({
        src: './static',
        dest: `../${projectDirectory}/statics/`,
        dereference: true,
        errorOnExist: false,
        preserveTimestamps: true,
        recursive: true,
    }),
    copyStaticFiles({
        src: './static/logo.svg',
        dest: `../${projectDirectory}/templates/mail/logo.svg`,
        dereference: true,
        errorOnExist: false,
        preserveTimestamps: true,
        recursive: true,
    }),
];

async function main() {
    const context = await esbuild.context({
        entryPoints: ['./js/main.ts'],
        outdir: `../${projectDirectory}/statics`,
        target: 'esnext',
        format: 'esm',
        bundle: true,
        sourcemap: mode == 'build' ? true : 'inline',
        define: {},
        treeShaking: true,
        loader: {},
        plugins: plugins,
        minify: mode == 'build',
        external: ['/fonts/*', '/images/*'],
        logLevel: 'debug',
    });
    if (mode == 'watch') {
        await context.watch();
    } else {
        await context.rebuild();
    }
}

main().catch(console.error);
