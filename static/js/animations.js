/**
 * Additional animations for NoteSmart app
 * This script adds interactive animations that require JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize animations
    initializeAnimations();
    
    // Add event listeners for dynamic content
    addEventListeners();
});

/**
 * Initialize animations for existing elements
 */
function initializeAnimations() {
    // Animate note cards when they come into view
    if ('IntersectionObserver' in window) {
        const noteCards = document.querySelectorAll('.note-card, .todo-item');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });
        
        noteCards.forEach(card => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            observer.observe(card);
        });
    }
    
    // Add ripple effect to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', createRipple);
    });
    
    // Animate checkboxes
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', animateCheckbox);
    });
}

/**
 * Add event listeners for dynamic content
 */
function addEventListeners() {
    // Category hover effect
    const categoryItems = document.querySelectorAll('.category-item');
    categoryItems.forEach(item => {
        item.addEventListener('mouseenter', () => {
            item.style.transform = 'translateX(5px)';
        });
        
        item.addEventListener('mouseleave', () => {
            item.style.transform = 'translateX(0)';
        });
    });
    
    // Flash notification when it appears
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.addedNodes.length) {
                mutation.addedNodes.forEach((node) => {
                    if (node.classList && node.classList.contains('alert')) {
                        flashElement(node);
                    }
                });
            }
        });
    });
    
    const container = document.querySelector('main .container');
    if (container) {
        observer.observe(container, { childList: true });
    }
}

/**
 * Create ripple effect on button click
 * @param {Event} e - Click event
 */
function createRipple(e) {
    const button = e.currentTarget;
    
    const circle = document.createElement('span');
    const diameter = Math.max(button.clientWidth, button.clientHeight);
    const radius = diameter / 2;
    
    circle.style.width = circle.style.height = `${diameter}px`;
    circle.style.left = `${e.clientX - button.getBoundingClientRect().left - radius}px`;
    circle.style.top = `${e.clientY - button.getBoundingClientRect().top - radius}px`;
    circle.classList.add('ripple');
    
    const ripple = button.getElementsByClassName('ripple')[0];
    
    if (ripple) {
        ripple.remove();
    }
    
    button.appendChild(circle);
}

/**
 * Animate checkbox on change
 * @param {Event} e - Change event
 */
function animateCheckbox(e) {
    const checkbox = e.currentTarget;
    
    if (checkbox.checked) {
        const todoItem = checkbox.closest('.todo-item');
        if (todoItem) {
            todoItem.classList.add('completed');
            todoItem.style.transition = 'background-color 0.5s ease';
        }
    } else {
        const todoItem = checkbox.closest('.todo-item');
        if (todoItem) {
            todoItem.classList.remove('completed');
        }
    }
}

/**
 * Flash element with attention animation
 * @param {HTMLElement} element - Element to animate
 */
function flashElement(element) {
    element.style.animation = 'none';
    setTimeout(() => {
        if (element.classList.contains('alert-danger')) {
            element.style.animation = 'shake 0.6s cubic-bezier(0.36, 0.07, 0.19, 0.97) both';
        } else {
            element.style.animation = 'slideInFromTop 0.5s ease-out';
        }
    }, 10);
}