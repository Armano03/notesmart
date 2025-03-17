-- Drop tables if they exist
DROP TABLE IF EXISTS note;
DROP TABLE IF EXISTS category;
DROP TABLE IF EXISTS user;

-- Create user table
CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(64) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create category table
CREATE TABLE category (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(64) NOT NULL,
    user_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    UNIQUE KEY user_category (user_id, name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create note table
CREATE TABLE note (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    content TEXT,
    created_date DATETIME NOT NULL,
    updated_date DATETIME NOT NULL,
    is_todo TINYINT(1) NOT NULL DEFAULT 0,
    completed TINYINT(1) NOT NULL DEFAULT 0,
    importance VARCHAR(20) DEFAULT 'normal',
    color VARCHAR(20) DEFAULT 'blue',
    category_id INT,
    user_id INT NOT NULL,
    FOREIGN KEY (category_id) REFERENCES category(id) ON DELETE SET NULL,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create indexes for performance
CREATE INDEX idx_note_user_id ON note(user_id);
CREATE INDEX idx_note_category_id ON note(category_id);
CREATE INDEX idx_note_is_todo ON note(is_todo);
CREATE INDEX idx_note_completed ON note(completed);
CREATE INDEX idx_note_importance ON note(importance);