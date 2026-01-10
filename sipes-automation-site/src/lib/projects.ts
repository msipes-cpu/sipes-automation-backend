import fs from 'fs';
import path from 'path';
import projectsData from '@/data/projects.json';

export type Project = {
    id: string;
    slug: string;
    title: string;
    description: string;
    technologies: string[];
    industry?: string;
    location?: string;
    image_url?: string;
    live_url?: string;
    upwork_job_url?: string;
    featured: boolean;
};

// Helper to get path to data file
function getDataFilePath() {
    return path.join(process.cwd(), 'src', 'data', 'projects.json');
}

// Helper to read data - kept for write operations
function readData(): Project[] {
    const filePath = getDataFilePath();
    try {
        const fileContent = fs.readFileSync(filePath, 'utf-8');
        return JSON.parse(fileContent);
    } catch (error) {
        console.error('Error reading projects data:', error);
        return [];
    }
}

// Helper to write data
function writeData(data: Project[]) {
    const filePath = getDataFilePath();
    try {
        fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf-8');
    } catch (error) {
        console.error('Error writing projects data', error);
    }
}

export async function getProjects() {
    // Return statically imported data for production reliability
    return new Promise<Project[]>((resolve) => {
        resolve(projectsData as Project[]);
    });
}

export async function getFeaturedProjects() {
    return new Promise<Project[]>((resolve) => {
        const featured = (projectsData as Project[]).filter(p => p.featured);
        resolve(featured);
    });
}

export async function createProject(projectData: Omit<Project, 'id'>) {
    return new Promise<Project>((resolve) => {
        const data = readData();

        const newProject: Project = {
            id: crypto.randomUUID(),
            ...projectData
        };

        data.push(newProject);
        writeData(data);

        resolve(newProject);
    });
}
