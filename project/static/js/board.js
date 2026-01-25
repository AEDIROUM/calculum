// Change session via dropdown
function changeSession(sessionId) {
	if (sessionId) {
		window.location.href = '/?session=' + sessionId;
	}
}

document.addEventListener('DOMContentLoaded', function() {
	// Handle algo toggle buttons
	const toggleButtons = document.querySelectorAll('.algo-toggle');
	
	toggleButtons.forEach(button => {
		button.addEventListener('click', function() {
			this.classList.toggle('active');
			const meetId = this.getAttribute('data-meet-id');
			const content = document.getElementById('algo-' + meetId);
			const toggleText = this.querySelector('.toggle-text');
			
			content.classList.toggle('active');
			
			if (content.classList.contains('active')) {
				toggleText.textContent = 'Masquer l\'algorithme';
				// Re-highlight the code when shown
				const codeBlock = content.querySelector('code');
				if (codeBlock && typeof hljs !== 'undefined') {
					hljs.highlightElement(codeBlock);
				}
			} else {
				toggleText.textContent = 'Afficher l\'algorithme';
			}
		});
	});
});