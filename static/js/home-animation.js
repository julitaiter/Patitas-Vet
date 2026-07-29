(function () {
    "use strict";

    if (
        typeof window.gsap === "undefined"
        || typeof window.ScrollTrigger === "undefined"
        || window.matchMedia("(prefers-reduced-motion: reduce)").matches
    ) {
        return;
    }

    gsap.registerPlugin(ScrollTrigger);

    document.querySelectorAll(".js-scroll-section").forEach((section) => {
        const heading = section.querySelectorAll(".js-scroll-heading");
        const items = section.querySelectorAll(".js-scroll-items > *");
        const timeline = gsap.timeline({
            scrollTrigger: {
                trigger: section,
                start: "top 90%",
                end: "top 45%",
                scrub: 0.6,
                invalidateOnRefresh: true
            }
        });

        if (heading.length) {
            timeline.from(heading, {
                autoAlpha: 0,
                y: 36,
                duration: 0.45,
                ease: "power2.out"
            });
        }

        if (items.length) {
            timeline.from(items, {
                autoAlpha: 0,
                y: 52,
                scale: 0.97,
                duration: 0.7,
                stagger: 0.12,
                ease: "power2.out"
            }, heading.length ? "-=0.15" : 0);
        }
    });
})();
