# Skileez - Peer-to-Peer Learning Platform

## Overview
Skileez is a full-stack web platform for global peer-to-peer learning and coaching, connecting students with expert coaches for personalized instruction. Inspired by Upwork, it aims to be a premium marketplace focusing on quality interactions. Key capabilities include comprehensive onboarding, role-based dashboards, a messaging system, and a job marketplace.

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture

### UI/UX Decisions
- **Color Schemes/Templates**: Jinja2 templates with inheritance.
- **Design Approach**: Mobile-first responsive design using Tailwind CSS with custom configurations.
- **Iconography**: Feather Icons for consistent UI elements.
- **Typography**: Inter Font via Google Fonts.

### Technical Implementations
- **Backend Framework**: Flask with Python.
- **Database ORM**: SQLAlchemy with a declarative base model.
- **Session Management**: Flask sessions utilizing configurable secret keys.
- **Middleware**: ProxyFix for robust handling of reverse proxy headers.
- **Environment Configuration**: Utilizes environment variables with sensible fallback defaults.
- **JavaScript**: Vanilla JS structured modularly under a `Skileez` global object.
- **Authentication**: Password hashing secured with Werkzeug.
- **Role-Based Access Control**: Decorators are used to protect routes based on user type.
- **Form Validation**: WTForms provides comprehensive validation rules for all forms.
- **Real-time Messaging**: AJAX-powered messaging enables instant message sending and receiving.
- **Portfolio System**: Redesigned to use external links (YouTube, Google Drive, etc.) instead of direct file uploads to reduce storage costs. Supports multiple links and optional thumbnails.
- **Dual Role System**: Comprehensive support for users to switch between student and coach roles seamlessly, with role-specific profile editing.
- **Messaging Permissions**: Students can message any coach; coaches can only message students who have contacted them or accepted proposals.

### Feature Specifications
- **User Management**: Supports dual roles (student, coach, or both) with separate profile models.
- **Onboarding Flows**:
    - **Coach Onboarding**: A 9-step guided process covering essential details, skills, and experience.
    - **Student Onboarding**: A simplified flow for profile creation.
    - **Progress Tracking**: Step-by-step navigation with indicators.
- **Dashboard System**: Dedicated dashboards for coaches (job recommendations, earnings, proposals) and students (learning requests, coach discovery).
- **Job Marketplace**: Students post learning requests; coaches search, filter, and submit proposals. Includes a job bookmarking system.
- **Messaging System**: 1:1 communication with conversation history and threading.
- **Profile Management**: Public coach profiles with a portfolio system showcasing projects via external links and a future-ready rating system.
- **Student Profile Privacy**: Coaches can only view student profiles with accepted proposals.
- **Student Language Management**: Students can manage multiple languages with predefined proficiency levels.

### System Design Choices
- **Data Storage**: SQLite for development, configurable via `DATABASE_URL`.
- **Connection Pooling**: SQLAlchemy engine options include pool recycling and pre-ping for efficient database connections.
- **Schema Management**: Automatic table creation on application startup.
- **Scalability**: Designed with a role-based architecture, modular templates, and a structure that supports future API development.

## External Dependencies

### Frontend
- **Tailwind CSS**: Utility-first CSS framework (CDN).
- **Feather Icons**: Icon library.
- **Google Fonts**: Inter font.

### Backend
- **Flask**: Web framework.
- **SQLAlchemy**: ORM.
- **WTForms**: Form handling.
- **Werkzeug**: Security utilities.