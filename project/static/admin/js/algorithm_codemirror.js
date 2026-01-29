(function() {
    'use strict';
    
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initCodeMirror);
    } else {
        initCodeMirror();
    }
    
    function initCodeMirror() {
        // Find the code textarea
        const codeTextarea = document.querySelector('textarea.code-editor');
        if (!codeTextarea) return;
        
        // Find the language select field
        const languageSelect = document.querySelector('#id_language');
        if (!languageSelect) return;
        
        // Language mode mapping
        const languageModes = {
            'python': 'python',
            'cpp': 'text/x-c++src',
            'c': 'text/x-csrc',
            'java': 'text/x-java',
            'javascript': 'javascript'
        };
        
        // Get initial mode
        function getMode() {
            const lang = languageSelect.value;
            return languageModes[lang] || 'python';
        }
        
        // Initialize CodeMirror
        const editor = CodeMirror.fromTextArea(codeTextarea, {
            lineNumbers: true,
            mode: getMode(),
            theme: 'monokai',
            indentUnit: 4,
            tabSize: 4,
            indentWithTabs: false,
            lineWrapping: true,
            matchBrackets: true,
            autoCloseBrackets: true,
            styleActiveLine: true,
            viewportMargin: Infinity
        });
        
        // Set height
        editor.setSize(null, 400);
        
        // Update mode when language changes
        languageSelect.addEventListener('change', function() {
            editor.setOption('mode', getMode());
        });
        
        // Ensure content is saved before form submission
        const form = codeTextarea.closest('form');
        if (form) {
            form.addEventListener('submit', function() {
                editor.save();
            });
        }
    }
})();