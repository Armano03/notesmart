// DOM Elements
const tasksList = document.getElementById('tasks-list');
const addTaskBtn = document.getElementById('add-task-btn');
const taskModal = document.getElementById('task-modal');
const modalClose = document.querySelector('.modal-close');
const cancelBtn = document.getElementById('cancel-btn');
const taskForm = document.getElementById('task-form');
const modalTitle = document.getElementById('modal-title');
const taskIdInput = document.getElementById('task-id');
const taskTitleInput = document.getElementById('task-title');
const taskDescriptionInput = document.getElementById('task-description');
const taskDueDateInput = document.getElementById('task-due-date');
const taskImportanceInput = document.getElementById('task-importance');
const taskColorInput = document.getElementById('task-color');
const filterStatus = document.getElementById('filter-status');
const filterImportance = document.getElementById('filter-importance');

// Global variables
let tasks = [];
let currentFilters = {
    status: 'all',
    importance: 'all'
};

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    loadTasks();
    
    // Task modal event listeners
    addTaskBtn.addEventListener('click', openAddTaskModal);
    modalClose.addEventListener('click', closeTaskModal);
    cancelBtn.addEventListener('click', closeTaskModal);
    taskForm.addEventListener('submit', handleTaskSubmit);
    
    // Filter event listeners
    filterStatus.addEventListener('change', handleFilterChange);
    filterImportance.addEventListener('change', handleFilterChange);
    
    // Close modal when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target === taskModal) {
            closeTaskModal();
        }
    });
});

// API Functions
async function loadTasks() {
    showLoading();
    try {
        const response = await fetch('/api/tasks');
        if (!response.ok) {
            throw new Error('Failed to load tasks');
        }
        tasks = await response.json();
        renderTasks();
    } catch (error) {
        showError('Error loading tasks. Please try again later.');
        console.error(error);
    }
}

async function createTask(taskData) {
    try {
        const response = await fetch('/api/tasks', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(taskData)
        });
        
        if (!response.ok) {
            throw new Error('Failed to create task');
        }
        
        const newTask = await response.json();
        tasks.push(newTask);
        renderTasks();
        return true;
    } catch (error) {
        showError('Error creating task. Please try again.');
        console.error(error);
        return false;
    }
}

async function updateTask(taskId, taskData) {
    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(taskData)
        });
        
        if (!response.ok) {
            throw new Error('Failed to update task');
        }
        
        const updatedTask = await response.json();
        const index = tasks.findIndex(task => task.id === updatedTask.id);
        if (index !== -1) {
            tasks[index] = updatedTask;
        }
        renderTasks();
        return true;
    } catch (error) {
        showError('Error updating task. Please try again.');
        console.error(error);
        return false;
    }
}

async function deleteTask(taskId) {
    if (!confirm('Are you sure you want to delete this task?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error('Failed to delete task');
        }
        
        tasks = tasks.filter(task => task.id !== taskId);
        renderTasks();
    } catch (error) {
        showError('Error deleting task. Please try again.');
        console.error(error);
    }
}

async function toggleTaskCompletion(taskId, completed) {
    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ completed })
        });
        
        if (!response.ok) {
            throw new Error('Failed to update task');
        }
        
        const updatedTask = await response.json();
        const index = tasks.findIndex(task => task.id === updatedTask.id);
        if (index !== -1) {
            tasks[index] = updatedTask;
        }
        renderTasks();
    } catch (error) {
        showError('Error updating task. Please try again.');
        console.error(error);
    }
}

// UI Functions
function renderTasks() {
    if (!tasksList) return;
    
    // Apply filters
    const filteredTasks = tasks.filter(task => {
        // Filter by status
        if (currentFilters.status === 'pending' && task.completed) {
            return false;
        }
        if (currentFilters.status === 'completed' && !task.completed) {
            return false;
        }
        // Filter by importance
        if (currentFilters.importance !== 'all' && task.importance !== currentFilters.importance) {
            return false;
        }
        return true;
    });
    
    if (filteredTasks.length === 0) {
        tasksList.innerHTML = '<div class="no-tasks">No tasks found. Add a new task to get started!</div>';
        return;
    }
    
    tasksList.innerHTML = '';
    
    filteredTasks.forEach(task => {
        const taskElement = document.createElement('div');
        taskElement.className = `task-item ${task.completed ? 'completed' : ''}`;
        taskElement.dataset.id = task.id;
        taskElement.dataset.importance = task.importance;
        taskElement.style.borderLeft = `4px solid var(--task-${task.color})`;
        
        const dueDate = task.due_date ? new Date(task.due_date).toLocaleDateString() : 'No due date';
        
        taskElement.innerHTML = `
            <div class="task-checkbox">
                <input type="checkbox" ${task.completed ? 'checked' : ''}>
            </div>
            <div class="task-content">
                <h3 class="task-title">${task.title}</h3>
                <p class="task-description">${task.description || 'No description'}</p>
                <div class="task-meta">
                    <span class="task-due-date">Due: ${dueDate}</span>
                    <span class="task-importance ${task.importance}">${task.importance}</span>
                </div>
            </div>
            <div class="task-actions">
                <button class="edit-task" title="Edit Task">✏️</button>
                <button class="delete-task" title="Delete Task">🗑️</button>
            </div>
        `;
        
        // Add event listeners
        const checkbox = taskElement.querySelector('input[type="checkbox"]');
        checkbox.addEventListener('change', () => {
            toggleTaskCompletion(task.id, checkbox.checked);
        });
        
        const editBtn = taskElement.querySelector('.edit-task');
        editBtn.addEventListener('click', () => {
            openEditTaskModal(task);
        });
        
        const deleteBtn = taskElement.querySelector('.delete-task');
        deleteBtn.addEventListener('click', () => {
            deleteTask(task.id);
        });
        
        tasksList.appendChild(taskElement);
    });
}

function openAddTaskModal() {
    modalTitle.textContent = 'Add New Task';
    taskForm.reset();
    taskIdInput.value = '';
    taskModal.style.display = 'block';
}

function openEditTaskModal(task) {
    modalTitle.textContent = 'Edit Task';
    taskIdInput.value = task.id;
    taskTitleInput.value = task.title;
    taskDescriptionInput.value = task.description || '';
    
    if (task.due_date) {
        // Format date to YYYY-MM-DD for input
        const date = new Date(task.due_date);
        const formattedDate = date.toISOString().split('T')[0];
        taskDueDateInput.value = formattedDate;
    } else {
        taskDueDateInput.value = '';
    }
    
    taskImportanceInput.value = task.importance;
    taskColorInput.value = task.color;
    
    taskModal.style.display = 'block';
}

function closeTaskModal() {
    taskModal.style.display = 'none';
}

async function handleTaskSubmit(e) {
    e.preventDefault();
    
    const taskData = {
        title: taskTitleInput.value,
        description: taskDescriptionInput.value,
        importance: taskImportanceInput.value,
        color: taskColorInput.value
    };
    
    if (taskDueDateInput.value) {
        taskData.due_date = taskDueDateInput.value;
    }
    
    let success = false;
    
    if (taskIdInput.value) {
        // Update existing task
        success = await updateTask(taskIdInput.value, taskData);
    } else {
        // Create new task
        success = await createTask(taskData);
    }
    
    if (success) {
        closeTaskModal();
    }
}

function handleFilterChange() {
    currentFilters.status = filterStatus.value;
    currentFilters.importance = filterImportance.value;
    renderTasks();
}

function showLoading() {
    tasksList.innerHTML = '<div class="loading-spinner">Loading tasks...</div>';
}

function showError(message) {
    const errorElement = document.createElement('div');
    errorElement.className = 'alert alert-danger';
    errorElement.textContent = message;
    
    // Insert at the top of the main container
    const container = document.querySelector('main .container');
    container.insertBefore(errorElement, container.firstChild);
    
    // Remove after 5 seconds
    setTimeout(() => {
        errorElement.remove();
    }, 5000);
}