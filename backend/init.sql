-- 能力诊断与学习资源生成系统 - 数据库初始化脚本

CREATE DATABASE IF NOT EXISTS capability_diagnosis DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE capability_diagnosis;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    target_job VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email)
);

-- 职业表
CREATE TABLE IF NOT EXISTS jobs (
    id VARCHAR(36) PRIMARY KEY,
    job_title VARCHAR(100) NOT NULL,
    description TEXT,
    required_skills JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 能力评估表
CREATE TABLE IF NOT EXISTS assessments (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    job_id VARCHAR(36) NOT NULL,
    user_input TEXT,
    overall_mastery DECIMAL(5,4),
    ability_vector JSON,
    knowledge_gaps JSON,
    confidence DECIMAL(5,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (job_id) REFERENCES jobs(id),
    INDEX idx_user_id (user_id)
);

-- 学习会话表
CREATE TABLE IF NOT EXISTS sessions (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    job_id VARCHAR(36) NOT NULL,
    status ENUM('active', 'paused', 'completed') DEFAULT 'active',
    current_step INT DEFAULT 1,
    progress DECIMAL(5,4) DEFAULT 0,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (job_id) REFERENCES jobs(id),
    INDEX idx_user_id (user_id)
);

-- 学习路径表
CREATE TABLE IF NOT EXISTS learning_paths (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    job_id VARCHAR(36) NOT NULL,
    steps JSON,
    current_step INT DEFAULT 1,
    status ENUM('active', 'completed', 'abandoned') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (job_id) REFERENCES jobs(id),
    INDEX idx_user_id (user_id)
);

-- 学习资源表
CREATE TABLE IF NOT EXISTS resources (
    id VARCHAR(36) PRIMARY KEY,
    knowledge_point VARCHAR(100) NOT NULL,
    content_type ENUM('讲义', '练习', '案例', '视频脚本') NOT NULL,
    title VARCHAR(200) NOT NULL,
    body TEXT NOT NULL,
    difficulty INT CHECK (difficulty BETWEEN 1 AND 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_knowledge_point (knowledge_point)
);

-- 学习记录表
CREATE TABLE IF NOT EXISTS learning_records (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    session_id VARCHAR(36) NOT NULL,
    resource_id VARCHAR(36) NOT NULL,
    status ENUM('not_started', 'in_progress', 'completed') DEFAULT 'not_started',
    score DECIMAL(5,4),
    time_spent INT DEFAULT 0,
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (session_id) REFERENCES sessions(id),
    FOREIGN KEY (resource_id) REFERENCES resources(id),
    INDEX idx_user_id (user_id),
    INDEX idx_session_id (session_id)
);
