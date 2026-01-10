import { createTestimonial, getTestimonials } from '../src/lib/testimonials';

async function main() {
    console.log("🔍 Verifying Local Testimonials Implementation...");

    // 1. Initial Count
    const initial = await getTestimonials();
    console.log(`Initial count: ${initial.length}`);

    // 2. Add Testimonial
    const newT = await createTestimonial({
        client_name: "Test User",
        content: "This is a test testimonial.",
        is_featured: false,
        is_verified: true,
        client_company: "Test Corp",
        client_role: "Tester",
        source: "Manual",
        rating: 5
    });
    console.log("✅ Added testimonial:", newT.id);

    // 3. Verify Persistence
    const updated = await getTestimonials();
    console.log(`Updated count: ${updated.length}`);

    const found = updated.find(t => t.id === newT.id);
    if (found) {
        console.log("✅ Verified: Testimonial found in database.");
    } else {
        console.error("❌ Error: Testimonial not found!");
        process.exit(1);
    }

    console.log("🎉 Verification Successful!");
}

main().catch(err => {
    console.error(err);
    process.exit(1);
});
