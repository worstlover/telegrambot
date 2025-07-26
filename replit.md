# Telegram Anonymous Channel Management Bot

## Overview

This is a comprehensive Telegram bot designed to manage anonymous message posting to a Telegram channel with full Persian language support and interactive menu system. The bot allows users to submit messages and media anonymously, with features including profanity filtering, rate limiting, admin approval workflows, configurable activity hours, and intuitive keyboard-based navigation. The system uses SQLite for data persistence and includes comprehensive admin controls for managing the channel.

## Recent Changes

### July 26, 2025 - Major Menu System Implementation
- ✅ Complete Persian language interface with keyboard navigation
- ✅ Interactive menu system for both users and admins
- ✅ Context-sensitive menus with back/restart functionality
- ✅ Multi-step input handling for admin operations
- ✅ Comprehensive keyboard layouts for all operations
- ✅ User state management for guided workflows
- ✅ Enhanced admin panel with hierarchical navigation

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The bot follows a modular Python architecture with clear separation of concerns:

- **Main Application Layer**: Entry point (`main.py`) that initializes the bot and registers handlers
- **Handler Layer**: Separate modules for user handlers (`handlers.py`) and admin handlers (`admin_handlers.py`)
- **Data Layer**: SQLite database operations (`database.py`) with connection pooling
- **Business Logic Layer**: Utilities (`utils.py`) and content filtering (`filters.py`)
- **Configuration Layer**: Centralized settings and messages (`config.py`)

The architecture supports both synchronous database operations and asynchronous Telegram API interactions using the python-telegram-bot library.

## Key Components

### 1. Interactive Menu System
- **User Interface**: Persian keyboard-based navigation with intuitive button layouts
- **State Management**: Multi-step workflows for admin operations with context preservation
- **Menu Hierarchy**: Context-sensitive menus (user/admin) with proper back navigation
- **Input Handling**: Guided input collection for complex operations like admin management

### 2. Message Processing Pipeline
- **Input Validation**: Checks for profanity, rate limits, and activity hours
- **Content Filtering**: Normalizes text and applies profanity detection with character substitution handling
- **Approval Workflow**: Routes media content through admin approval process when required
- **Publishing**: Posts approved content to the target Telegram channel

### 2. User Management System
- **User Registration**: Automatic user creation on first interaction
- **Display Names**: One-time settable anonymous display names with uniqueness validation
- **Rate Limiting**: Configurable time-based message throttling per user
- **Activity Tracking**: Logs user interactions and message timestamps

### 3. Admin Control Panel
- **Multi-Admin Support**: Hierarchical admin system with add/remove capabilities
- **Content Moderation**: Approve/reject pending media submissions
- **System Configuration**: Runtime adjustment of rate limits, activity hours, and approval requirements
- **Profanity Management**: Dynamic addition/removal of filtered words

### 4. Database Schema
- **Users Table**: Stores user data, display names, and activity timestamps
- **Admins Table**: Manages admin privileges with audit trail
- **Profanity Words Table**: Configurable content filtering dictionary
- **Settings Table**: Runtime configuration storage
- **Pending Media Table**: Queue for media awaiting approval
- **Message Logs Table**: Audit trail for all processed messages

## Data Flow

### User Message Flow
1. User sends message/media to bot
2. System validates user permissions and rate limits
3. Content passes through profanity filter
4. Text messages: Direct posting to channel (if clean)
5. Media messages: Queue for admin approval (if required)
6. Approved content gets posted with anonymous attribution

### Admin Workflow
1. Admin receives notification of pending media
2. Admin reviews content through inline keyboard controls
3. Approval/rejection decision updates database and notifies user
4. Approved media posts to channel with admin attribution

### Configuration Management
1. Admins modify settings through bot commands
2. Changes persist to SQLite settings table
3. System immediately applies new configuration
4. Settings affect rate limiting, activity hours, and approval requirements

## External Dependencies

### Core Dependencies
- **python-telegram-bot**: Telegram Bot API wrapper for async operations
- **sqlite3**: Built-in Python SQLite database interface
- **logging**: Python standard logging for debugging and monitoring

### Environment Variables
- **TELEGRAM_BOT_TOKEN**: Bot authentication token from BotFather
- **TELEGRAM_CHANNEL_ID**: Target channel ID for message posting
- **TELEGRAM_CHANNEL_USERNAME**: Channel username for user references

### Database Storage
- **SQLite Database**: Local file-based storage (`bot_database.db`)
- **No external database server required**
- **Self-contained data persistence**

## Deployment Strategy

### Local Development
- Direct Python execution with environment variables
- SQLite database auto-initialization on first run
- Hot-reload capabilities for development

### Production Considerations
- **Database**: SQLite suitable for moderate traffic; may require PostgreSQL for high volume
- **Scaling**: Single-instance design; horizontal scaling would require external database
- **Monitoring**: Built-in logging to stdout/files
- **Error Handling**: Comprehensive exception handling with user-friendly error messages

### Configuration Management
- Environment variable based configuration
- Runtime settings stored in database
- Default values provide fallback for missing configuration
- Admin panel allows real-time configuration changes without restart

The system is designed to be self-contained and easy to deploy while providing comprehensive channel management capabilities with strong admin controls and user privacy protection.