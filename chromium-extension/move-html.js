#!/usr/bin/env node

import { promises as fs } from 'fs';
import path from 'path';

async function moveFile(src, dest) {
    try {
        await fs.rename(src, dest);
    } catch (err) {
        if (err.code === 'EXDEV') {
            await fs.copyFile(src, dest);
            await fs.unlink(src);
        } else {
            throw err;
        }
    }
}

async function rmIfEmpty(dir) {
    try {
        const entries = await fs.readdir(dir);
        if (entries.length === 0) {
            await fs.rmdir(dir);
        }
    } catch { }
}

async function main() {
    const srcHtml = path.join('dist', 'src', 'popup', 'index.html');
    const destDir = path.join('dist', 'popup');
    const destHtml = path.join(destDir, 'index.html');

    try {
        await fs.mkdir(destDir, { recursive: true });
        await moveFile(srcHtml, destHtml);
        await rmIfEmpty(path.join('dist', 'src', 'popup'));
        await rmIfEmpty(path.join('dist', 'src'));
        console.log('✔ popup/index.html moved successfully');
    } catch (err) {
        console.error('✘ Failed to move file:', err);
        process.exit(1);
    }
}

main();
