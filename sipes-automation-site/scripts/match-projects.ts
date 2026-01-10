
import fs from 'fs';
import path from 'path';

// Load data directly
const projectsPath = path.join(process.cwd(), 'src/data/projects.json');
const projects = JSON.parse(fs.readFileSync(projectsPath, 'utf-8'));

function calculateScore(project: any, tokens: string[]): number {
    let score = 0;
    const text = `${project.title} ${project.description} ${project.industry} ${project.technologies.join(' ')}`.toLowerCase();

    tokens.forEach(token => {
        if (text.includes(token)) {
            // Heuristic scoring
            if (project.title.toLowerCase().includes(token)) score += 10;
            else if (project.industry && project.industry.toLowerCase().includes(token)) score += 5;
            else if (project.technologies.some((t: string) => t.toLowerCase() === token)) score += 3;
            else score += 1;
        }
    });

    return score;
}

export function findRelevantProjects(query: string, limit = 3) {
    const tokens = query.toLowerCase().split(/\s+/).filter(t => t.length > 2); // basic tokenization

    const scored = projects.map((p: any) => ({
        ...p,
        score: calculateScore(p, tokens)
    }));

    // Sort by score desc
    scored.sort((a: any, b: any) => b.score - a.score);

    return scored.slice(0, limit);
}

// CLI Execution if run directly
if (process.argv[1] === import.meta.filename) {
    const query = process.argv.slice(2).join(' ');
    if (!query) {
        console.log("Usage: npx tsx scripts/match-projects.ts <job description>");
        process.exit(1);
    }

    console.log(`\n🔍 Finding matches for: "${query.substring(0, 50)}..."\n`);
    const matches = findRelevantProjects(query);

    matches.forEach((p: any, i: number) => {
        console.log(`${i + 1}. ${p.title} (Score: ${p.score})`);
        console.log(`   Technologies: ${p.technologies.join(', ')}`);
        console.log(`   Slug: ${p.slug}`);
        console.log(`   Link: https://sipesautomation.com/work/${p.slug}\n`);
    });
}
