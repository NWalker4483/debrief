# Debrief - AI-Powered Project Management for Obsidian

Debrief is an intelligent project management assistant that integrates with your Obsidian vault, helping you maintain project documentation and track progress through natural speech updates.

## 🌟 Features

- **Automated Project Tracking**
  - Scans your Obsidian vault for files with project tags
  - Automatically identifies working files through direct links to project files
  - Maintains project relationship graphs and dependencies

- **Speech-to-Text Updates**
  - Provide end-of-day updates using voice input
  - Natural and friction-free project documentation
  - Perfect for quick debriefs and progress logging

- **AI-Powered Analysis**
  - Suggests task completion status updates
  - Identifies new tasks from verbal updates
  - Generates concise project summaries
  - Recommends creation of new working files
  - Maintains project context and relationships

## 📋 Prerequisites

- Obsidian vault with reading/writing permissions
- Project files must include a project tag (default: `#project`)
- Working files must be directly linked to project files

## 🚀 Getting Started

1. Install the plugin in your Obsidian vault
2. Configure your project tag preferences
3. Tag your main project files
4. Link relevant working files to your project files
5. Start providing end-of-day updates using the speech-to-text feature

## 💡 Usage

### Project Structure
```markdown
YourVault/
├── ProjectA.md (#project)
│   ├── WorkingFile1.md
│   └── WorkingFile2.md
└── ProjectB.md (#project)
    ├── WorkingFile3.md
    └── SubTask1.md
```

### Daily Debrief
1. Click the Debrief button in your Obsidian ribbon
2. Speak your daily update
3. Review AI-suggested changes:
   - Task status updates
   - New tasks identified
   - Project summaries
   - Suggested new working files
4. Accept or modify suggestions
5. Changes are automatically applied to your vault

## ⚙️ Configuration

- **Project Tag**: Customize the tag used to identify project files
- **Speech Recognition**: Configure input device and language
- **AI Settings**: Adjust suggestion sensitivity and update frequency
- **File Templates**: Customize new working file templates

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Share your use cases and improvements
