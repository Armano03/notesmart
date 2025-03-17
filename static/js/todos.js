// JavaScript to handle to-do completion with the proper PUT method
document.addEventListener('DOMContentLoaded', function() {
    // Find all checkbox forms
    const checkboxForms = document.querySelectorAll('.checkbox-form');
    
    checkboxForms.forEach(form => {
        const checkbox = form.querySelector('input[type="checkbox"]');
        
        checkbox.addEventListener('change', function(e) {
            // Prevent default form submission
            e.preventDefault();
            
            // Get the note ID from the form's action URL
            const noteId = form.getAttribute('data-note-id');
            
            // Get the completed state from the checkbox
            const completed = checkbox.checked;
            
            // Send a PUT request to update the note
            fetch(`/api/notes/${noteId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    completed: completed
                })
            })
            .then(response => {
                if (response.ok) {
                    // Reload the page to show updated state
                    window.location.reload();
                } else {
                    console.error('Failed to update to-do');
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    });
});