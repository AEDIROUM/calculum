// Initialize syntax highlighting
document.addEventListener('DOMContentLoaded', function() {
	if (typeof hljs !== 'undefined') {
		hljs.highlightAll();
	}
	
	// Highlight active navigation link
	const currentPath = window.location.pathname;
	const navLinks = document.querySelectorAll('nav a');
	
	navLinks.forEach(link => {
		const href = link.getAttribute('href');
		
		// Check if current path matches the nav link
		if (href === '/' && (currentPath === '/' || currentPath.startsWith('/noob'))) {
			link.classList.add('active');
		} 
		else if (href !== '/' && currentPath.startsWith(href)) {
			link.classList.add('active');
		}
	});
});