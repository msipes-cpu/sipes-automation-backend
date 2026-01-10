import fs from 'fs';
import path from 'path';

export type Testimonial = {
    id: string;
    created_at: string;
    client_name: string;
    client_role?: string;
    client_company?: string;
    client_avatar_url?: string;
    content: string;
    rating?: number;
    source?: string;
    project_title?: string;
    project_id?: string;
    is_featured: boolean;
    is_verified: boolean;
};

// Helper to get path to data file
function getDataFilePath() {
    return path.join(process.cwd(), 'src', 'data', 'testimonials.json');
}

// Helper to read data
function readData(): Testimonial[] {
    const filePath = getDataFilePath();
    try {
        const fileContent = fs.readFileSync(filePath, 'utf-8');
        return JSON.parse(fileContent);
    } catch (error) {
        console.error('Error reading testimonials data:', error);
        return [];
    }
}

// Helper to write data
function writeData(data: Testimonial[]) {
    const filePath = getDataFilePath();
    try {
        fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf-8');
    } catch (error) {
        console.error('Error writing dummy data', error);
    }
}


export async function getTestimonials() {
    // Simulate async to keep API consistent with DB version
    return new Promise<Testimonial[]>((resolve) => {
        const data = readData();
        // Sort by created_at desc
        data.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
        resolve(data);
    });
}

export async function getFeaturedTestimonials() {
    return new Promise<Testimonial[]>((resolve) => {
        const data = readData();
        const featured = data.filter(t => t.is_featured);
        // Sort by created_at desc
        featured.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
        resolve(featured);
    });
}

export async function createTestimonial(testimonialData: Omit<Testimonial, 'id' | 'created_at'>) {
    return new Promise<Testimonial>((resolve) => {
        const data = readData();

        const newTestimonial: Testimonial = {
            id: crypto.randomUUID(), // Use Web Crypto API or import uuid package if available
            created_at: new Date().toISOString(),
            ...testimonialData
        };

        data.push(newTestimonial);
        writeData(data);

        resolve(newTestimonial);
    });
}
