document.addEventListener('DOMContentLoaded', function() {
	const printBtn = document.getElementById('print-btn');
	
	if (printBtn) {
		printBtn.addEventListener('click', function() {
			window.print();
		});
	}
});