# AI FAQ Chatbot - User Guide

Welcome to the AI FAQ Chatbot! This guide explains how to use the web interface.

## 1. Authentication
- You must create an account and log in.
- Sessions are securely stored via JWT tokens.

## 2. Using the Knowledge Base (Dashboard)
- On the dashboard, you can view, create, edit, and delete standard FAQs.
- You can upload `.txt`, `.csv`, or `.pdf` files. The system will automatically chunk and embed the files.

## 3. Chat Interface
Access the Chat Interface by clicking the **"Open Chat"** button on your dashboard.

### Starting a Chat
Click **"+ New Chat"** in the sidebar. Simply type a question (e.g. "How do I reset my password?") into the input area. The system will automatically construct a persistent conversation.

### Sources
Every time the AI Assistant answers, it consults your FAQ documents. A small "Sources" block will appear under its message showing which document and chunk it retrieved, along with the percentage of semantic similarity.

### Managing Conversations
- **History**: Use the left sidebar to switch between older conversations. They are intelligently grouped by date.
- **Rename**: Click the three dots next to a conversation name to open a modal and rename it.
- **Delete**: Click the three dots to permanently delete a thread. This clears your messages but does NOT delete the FAQ documents.

## 4. Expected AI Latency
Because the AI model runs locally on your machine, it may take 2-10 seconds to respond depending on hardware limitations. A subtle "Thinking" animation will display until the response arrives.
