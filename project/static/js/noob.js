// Noob guide page functionality
document.addEventListener('DOMContentLoaded', function() {
	// Animate guide sections on scroll
	const observer = new IntersectionObserver(function(entries) {
		entries.forEach(entry => {
			if (entry.isIntersecting) {
				entry.target.style.animation = 'slideIn 0.5s ease forwards';
			}
		});
	}, { threshold: 0.1 });

	const guideSections = document.querySelectorAll('.guide-section');
	guideSections.forEach((section, index) => {
		section.style.animation = 'none';
		section.style.opacity = '0';
		observer.observe(section);
	});

	// Add smooth transitions to CTA buttons
	const buttons = document.querySelectorAll('.action-button');
	buttons.forEach(button => {
		button.addEventListener('mouseenter', function() {
			this.style.boxShadow = '0 8px 25px rgba(52, 152, 219, 0.5)';
		});
		button.addEventListener('mouseleave', function() {
			this.style.boxShadow = '0 6px 20px rgba(52, 152, 219, 0.4)';
		});
	});
});

// Add CSS animation dynamically
const style = document.createElement('style');
style.textContent = `
	@keyframes slideIn {
		from {
			opacity: 0;
			transform: translateX(-20px);
		}
		to {
			opacity: 1;
			transform: translateX(0);
		}
	}
`;
document.head.appendChild(style);
