document.addEventListener("DOMContentLoaded", function() {
    const collage = document.getElementById('animatedCollage');
    collage.addEventListener('mouseenter', function() {
        Array.from(collage.children).forEach(img => {
            img.style.animationPlayState = 'paused';
        });
    });
    collage.addEventListener('mouseleave', function() {
        Array.from(collage.children).forEach(img => {
            img.style.animationPlayState = 'running';
        });
    });
});
