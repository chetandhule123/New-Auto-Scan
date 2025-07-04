# Enhanced NSE Stock Screener

## Overview

This is a real-time stock screening application built with Streamlit that continuously monitors NSE (National Stock Exchange) stocks. The application provides server-side background scanning every 15 minutes with live data updates and filtering capabilities.

## System Architecture

The application follows a modular architecture with three main components:

1. **Frontend Layer** (`app.py`): Streamlit-based web interface
2. **Data Management Layer** (`data_manager.py`): Thread-safe data storage and retrieval
3. **Scanning Engine** (`stock_scanner.py`): Background data collection and processing

The system uses a thread-based approach for background processing while maintaining a responsive web interface.

## Key Components

### Frontend (app.py)
- **Technology**: Streamlit web framework
- **Purpose**: Provides the user interface for displaying stock data and controls
- **Features**: 
  - Real-time status indicators
  - Multi-column layout for data presentation
  - Session state management for persistent scanner operation
  - Wide layout configuration for optimal data viewing

### Data Manager (data_manager.py)
- **Technology**: Pandas for data manipulation, threading for concurrency
- **Purpose**: Centralized data storage and retrieval with thread safety
- **Features**:
  - Thread-safe data operations using locks
  - Scan history management (limited to 100 records)
  - Filtering capabilities for market cap and sector
  - Timestamp tracking for scan scheduling

### Stock Scanner (stock_scanner.py)
- **Technology**: Threading, schedule library, requests for HTTP calls
- **Purpose**: Background data collection and processing
- **Features**:
  - Continuous background scanning every 15 minutes
  - Daemon thread implementation for clean shutdown
  - HTTP-based data fetching (presumably from NSE APIs)
  - Automatic retry and error handling

## Data Flow

1. **Initialization**: App starts and initializes DataManager and StockScanner
2. **Background Scanning**: Scanner runs on a separate daemon thread
3. **Data Collection**: Every 15 minutes, scanner fetches fresh stock data
4. **Data Storage**: Collected data is stored in DataManager with thread safety
5. **UI Updates**: Frontend queries DataManager for latest data to display
6. **User Interaction**: Users can filter and view data through the Streamlit interface

## External Dependencies

- **Streamlit**: Web framework for the frontend
- **Pandas**: Data manipulation and analysis
- **Requests**: HTTP client for external API calls
- **Schedule**: Task scheduling for periodic scans
- **Threading**: Built-in Python threading for background operations

## Deployment Strategy

The application is designed for single-instance deployment with:
- **Background Processing**: Daemon threads for continuous operation
- **Memory Management**: Limited scan history to prevent memory leaks
- **Session Persistence**: Streamlit session state for maintaining scanner state
- **Error Handling**: Graceful degradation when data fetching fails

## Changelog

- July 04, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.