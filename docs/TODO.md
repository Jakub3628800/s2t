# S2T Project TODO List

This document outlines future development plans and improvements for the S2T project.

## High Priority

- **Upload library to PyPI**
  - Create proper package structure for PyPI distribution
  - Ensure all dependencies are correctly specified
  - Add proper versioning and release process
  - Create comprehensive README and documentation for PyPI page

- **Further improve test coverage**
  - Expand unit tests for core functionality
  - Add integration tests for end-to-end workflows
  - Implement UI/GTK4 test framework
  - Create mock backends for testing without API keys

## Feature Enhancements

- **Enhanced speech-to-text capabilities**
  - Add support for additional transcription backends (local models)
  - Implement language detection and multi-language support
  - Add specialized modes for technical terms and code dictation
  - Include speech command capabilities (e.g., "new paragraph")

- **UI Improvements**
  - Add keyboard shortcuts for common operations
  - Implement a settings dialog for real-time configuration
  - Create a system tray icon for quick access
  - Add theming support (light/dark mode)

## Technical Improvements

- **Performance optimizations**
  - Reduce startup time for faster response
  - Optimize audio processing for lower latency
  - Implement caching for frequently used configurations
  - Add batch processing capabilities for offline transcription

- **Code quality and maintainability**
  - Move to fully typed codebase with more MyPy enforcement
  - Restructure modules for better organization
  - Improve error handling and user feedback
  - Add configurable logging levels

## Completed Items

- **~~Migrate to GTK 4~~** ✅
  - Updated all imports to use GTK 4.0
  - Fixed compatibility issues with GTK 4 API
  - Updated documentation to reflect GTK 4 requirements

- **~~Centralize command-line interface~~** ✅
  - Created unified main module entry point
  - Standardized command-line arguments
  - Implemented flexible mode selection

- **~~Improve security~~** ✅
  - Fixed potential security issues in subprocess calls
  - Implemented better temporary file handling
  - Added test coverage for cleanup behavior

## Long-term Goals

- **Expand platform support**
  - Add native Windows support
  - Improve macOS integration
  - Create mobile companion apps
  - Support for embedded/IoT devices

- **Integration capabilities**
  - Create plugins for popular applications
  - Develop API for third-party integration
  - Add webhooks for event-driven workflows
  - Support for cloud synchronization of transcriptions
