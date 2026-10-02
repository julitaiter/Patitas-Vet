(function () {
    "use strict";

    const hero = document.querySelector(".home-hero-carousel");
    if (hero) {
        const updateHeroHeight = () => {
            const navbar = document.querySelector("body > .navbar");
            const navbarHeight = navbar ? navbar.getBoundingClientRect().height : 0;
            hero.style.setProperty(
                "--home-hero-height",
                `${Math.max(0, window.innerHeight - navbarHeight)}px`
            );
        };

        updateHeroHeight();
        window.addEventListener("resize", updateHeroHeight);
        if (window.visualViewport) {
            window.visualViewport.addEventListener("resize", updateHeroHeight);
        }
        const toggle = hero.querySelector(".js-home-carousel-toggle");
        if (toggle && window.bootstrap?.Carousel) {
            const carousel = window.bootstrap.Carousel.getOrCreateInstance(hero);
            let paused = false;
            const setPaused = (value) => {
                paused = value;
                if (paused) {
                    carousel.pause();
                } else {
                    carousel.cycle();
                }
                toggle.setAttribute("aria-pressed", String(paused));
                toggle.setAttribute("aria-label", paused ? "Reanudar carrusel" : "Pausar carrusel");
                toggle.querySelector("span").textContent = paused ? "Reanudar" : "Pausar";
                toggle.querySelector("i").className = paused ? "bi bi-play-fill" : "bi bi-pause-fill";
            };
            toggle.addEventListener("click", () => setPaused(!paused));
            if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
                setPaused(true);
            }
        }
    }

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
            timeline.fromTo(heading, {
                autoAlpha: 0,
                y: 36,
            }, {
                autoAlpha: 1,
                y: 0,
                duration: 0.45,
                ease: "power2.out"
            });
        }

        if (items.length) {
            timeline.fromTo(items, {
                autoAlpha: 0,
                y: 52,
                scale: 0.97,
            }, {
                autoAlpha: 1,
                y: 0,
                scale: 1,
                duration: 0.7,
                stagger: 0.12,
                ease: "power2.out"
            }, heading.length ? "-=0.15" : 0);
        }
    });
})();
