import { mkdirSync, writeFileSync } from 'fs';
import { join } from 'path';

const directories = ['./dist', './dist/assets'];

directories.forEach(dir => {
  const filePath = join(dir, '__init__.py');
  mkdirSync(dir, { recursive: true }); // Ensure the directory exists
  writeFileSync(filePath, '', { flag: 'w' }); // Create an empty __init__.py file
});

console.log('__init__.py files created in dist/ and dist/assets/');