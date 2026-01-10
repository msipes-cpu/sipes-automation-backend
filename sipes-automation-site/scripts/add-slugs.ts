
import fs from 'fs';
import path from 'path';
import slugify from 'slugify';

const projectsPath = path.join(process.cwd(), 'src/data/projects.json');
const rawData = fs.readFileSync(projectsPath, 'utf-8');
const projects = JSON.parse(rawData);

const updatedProjects = projects.map((p: any) => {
    // Generate slug if it doesn't exist
    if (!p.slug) {
        p.slug = slugify(p.title, { lower: true, strict: true });
    }
    return p;
});

fs.writeFileSync(projectsPath, JSON.stringify(updatedProjects, null, 2));
console.log(`Updated ${updatedProjects.length} projects with slugs.`);
