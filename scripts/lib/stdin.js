'use strict';
/**
 * Safe stdin reader with timeout protection.
 * Prevents hooks from hanging when stdin pipe is not properly closed.
 */
const TIMEOUT_MS = 2000;

function readStdin(timeout) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    const timer = setTimeout(() => {
      process.stdin.destroy();
      resolve(chunks.join(''));
    }, timeout || TIMEOUT_MS);

    process.stdin.on('data', (chunk) => {
      chunks.push(chunk.toString());
    });

    process.stdin.on('end', () => {
      clearTimeout(timer);
      resolve(chunks.join(''));
    });

    process.stdin.on('error', (err) => {
      clearTimeout(timer);
      reject(err);
    });

    // If stdin is already ended, resolve immediately
    if (process.stdin.readableEnded) {
      clearTimeout(timer);
      resolve(chunks.join(''));
    }
  });
}

function readStdinSync() {
  try {
    return fs.readFileSync(0, 'utf-8');
  } catch (_) {
    return '';
  }
}

const fs = require('fs');

module.exports = { readStdin, readStdinSync, TIMEOUT_MS };
