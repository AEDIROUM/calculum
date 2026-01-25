// Presentation page functionality
document.addEventListener('DOMContentLoaded', function() {
	// Smooth scrolling for anchor links
	const anchorLinks = document.querySelectorAll('a[href^="#"]');
	
	anchorLinks.forEach(link => {
		link.addEventListener('click', function(e) {
			e.preventDefault();
			const target = document.querySelector(this.getAttribute('href'));
			if (target) {
				target.scrollIntoView({ behavior: 'smooth' });
			}
		});
	});

	// Add animation class to elements on scroll
	const observer = new IntersectionObserver(function(entries) {
		entries.forEach(entry => {
			if (entry.isIntersecting) {
				entry.target.classList.add('fade-in');
			}
		});
	});

	const elements = document.querySelectorAll('.info-card, .presentation-section');
	elements.forEach(el => observer.observe(el));
});
