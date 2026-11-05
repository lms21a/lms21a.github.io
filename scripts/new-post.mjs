import { mkdir, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const title = process.argv.slice(2).join(' ').trim();
if (!title) {
  console.error('Usage: npm run new:post -- "Your research note title"');
  process.exit(1);
}

const slug = title.normalize('NFKD').replace(/[\u0300-\u036f]/g, '')
  .toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
if (!slug) {
  console.error('Please include at least one Latin letter or number in the title.');
  process.exit(1);
}

const today = new Intl.DateTimeFormat('en-CA', {
  year: 'numeric', month: '2-digit', day: '2-digit',
}).format(new Date());
const directory = fileURLToPath(new URL('../src/content/posts/', import.meta.url));
const filename = path.join(directory, `${slug}.md`);
const content = `---\ntitle: ${JSON.stringify(title)}\ndescription: "Add a short summary of the question and finding."\ndate: ${today}\ndraft: true\ntags: [Research]\n---\n\n## Question\n\nWhat are you trying to understand?\n\n## Setup\n\nDescribe the experiment and how to reproduce it.\n\n## Results\n\nAdd your figures, evidence, and interpretation.\n\n## Limitations and next steps\n\nWhat remains uncertain?\n\n## References\n\nLink to papers, code, and data.\n`;

try {
  await mkdir(directory, { recursive: true });
  await writeFile(filename, content, { flag: 'wx' });
  console.log(`Created draft: ${filename}\nPreview with npm run dev:drafts.\nSet draft: false when ready for publication.`);
} catch (error) {
  if (error.code === 'EEXIST') {
    console.error(`A post already exists at ${filename}. Choose another title.`);
    process.exit(1);
  }
  throw error;
}
