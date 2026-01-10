import { MetadataRoute } from 'next';
import { getProjects } from '@/lib/projects';
import { industries, integrations } from '@/lib/seo-content';

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
    const baseUrl = 'https://www.sipesautomation.com';

    // 1. Static Routes
    const staticRoutes: MetadataRoute.Sitemap = [
        {
            url: baseUrl,
            lastModified: new Date(),
            changeFrequency: 'weekly',
            priority: 1,
        },
        {
            url: `${baseUrl}/resources/50-ways`,
            lastModified: new Date(),
            changeFrequency: 'monthly',
            priority: 0.8,
        },
    ];

    // 2. Dynamic Work (Case Studies) Routes
    const projects = await getProjects();
    const workRoutes: MetadataRoute.Sitemap = projects.map((project) => ({
        url: `${baseUrl}/work/${project.slug}`,
        lastModified: new Date(), // Ideally track actual modified date if available
        changeFrequency: 'monthly',
        priority: 0.9,
    }));

    // 3. Dynamic Industry Routes
    const industryRoutes: MetadataRoute.Sitemap = Object.keys(industries).map((slug) => ({
        url: `${baseUrl}/industry/${slug}`,
        lastModified: new Date(),
        changeFrequency: 'weekly',
        priority: 0.8,
    }));

    // 4. Dynamic Software/Integration Routes
    const integrationRoutes: MetadataRoute.Sitemap = Object.keys(integrations).map((slug) => ({
        url: `${baseUrl}/software/${slug}`,
        lastModified: new Date(),
        changeFrequency: 'weekly',
        priority: 0.8,
    }));

    return [
        ...staticRoutes,
        ...workRoutes,
        ...industryRoutes,
        ...integrationRoutes,
    ];
}
