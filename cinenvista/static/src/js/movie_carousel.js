// Movie Carousel - Drag and Arrow Navigation
document.addEventListener('DOMContentLoaded', function() {
    const scrollContainers = document.querySelectorAll('.movies-scroll-container');
    
    scrollContainers.forEach(container => {
        const wrapper = container.closest('.movies-carousel-wrapper');
        if (!wrapper) return;

        let isDown = false;
        let startX;
        let scrollLeft;

        // Drag to scroll functionality
        container.addEventListener('mousedown', (e) => {
            isDown = true;
            startX = e.pageX - container.offsetLeft;
            scrollLeft = container.scrollLeft;
            container.style.cursor = 'grabbing';
        });

        container.addEventListener('mouseleave', () => {
            isDown = false;
            container.style.cursor = 'grab';
        });

        container.addEventListener('mouseup', () => {
            isDown = false;
            container.style.cursor = 'grab';
        });

        container.addEventListener('mousemove', (e) => {
            if (!isDown) return;
            e.preventDefault();
            const x = e.pageX - container.offsetLeft;
            const walk = (x - startX) * 1; // scroll-fast
            container.scrollLeft = scrollLeft - walk;
        });

        // Arrow buttons functionality
        const arrows = wrapper.querySelectorAll('.carousel-arrow');
        arrows.forEach(arrow => {
            arrow.addEventListener('click', () => {
                const scrollDirection = parseInt(arrow.dataset.scroll);
                const scrollAmount = 300; // pixels to scroll
                
                container.scrollBy({
                    left: scrollDirection * scrollAmount,
                    behavior: 'smooth'
                });
            });
        });

        // Set initial cursor
        container.style.cursor = 'grab';
    });
});
