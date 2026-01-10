import { MetadataRoute } from 'next';

export default function robots(): MetadataRoute.Robots {
    const baseUrl = 'https://www.sipesautomation.com';

    return {
        rules: {
            userAgent: '*',
            allow: '/',
            disallow: ['/private/', '/api/'], // Disallow API routes or private areas if any
        },
        sitemap: `${baseUrl}/sitemap.xml`,
    };
}
