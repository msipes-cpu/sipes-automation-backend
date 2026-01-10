import { createProject, getProjects } from '../src/lib/projects';
import { createTestimonial, getTestimonials } from '../src/lib/testimonials';

async function main() {
    console.log("🔍 Verifying Projects & Linked Testimonials...");

    // 1. Add Project
    const newProject = await createProject({
        title: "Automated Email Outreach System",
        slug: "automated-email-outreach-system",
        description: "Built a cold email system sending 1000 daily emails with 99% deliverability.",
        technologies: ["Python", "AWS", "SendGrid"],
        featured: true,
        live_url: "https://example.com",
        upwork_job_url: "https://upwork.com/job/123"
    });
    console.log("✅ Added Project:", newProject.title, `(${newProject.id})`);

    // 2. Add Testimonial linked to Project
    const newTestimonial = await createTestimonial({
        client_name: "Sarah Connors",
        client_company: "Skynet Systems",
        content: "The email automation changed our business completely.",
        rating: 5,
        is_featured: true,
        is_verified: true,
        project_id: newProject.id,
        project_title: newProject.title
    });
    console.log("✅ Added Testimonial linked to Project:", newTestimonial.client_name);

    // 3. Verify Linkage
    const projects = await getProjects();
    const testimonials = await getTestimonials();

    const foundP = projects.find(p => p.id === newProject.id);
    const foundT = testimonials.find(t => t.id === newTestimonial.id);

    if (foundP && foundT && foundT.project_id === foundP.id) {
        console.log("✅ Verified: Project and Testimonial correctly linked.");
    } else {
        console.error("❌ Error: Verification failed.");
        process.exit(1);
    }

    console.log("🎉 Verification Successful!");
}

main().catch(err => {
    console.error(err);
    process.exit(1);
});
