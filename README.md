# Work Hours Tracker

A simple, easy-to-use application to track your working hours. Available in both **Command-Line** and **Web Interface** versions!

## Choose Your Interface

### 🌐 Web Interface (Recommended for Beginners)
The easiest way to use the tracker - just open it in your web browser!

```bash
python3 work_tracker_web.py
```

Then open your browser and go to: **http://localhost:8000**

### 💻 Command-Line Interface
For those who prefer typing commands in the terminal.

```bash
python3 work_tracker.py in
```

Both versions use the same data file, so you can switch between them anytime!

## Features

- **Clock In/Out**: Track when you start and stop working
- **Session Notes**: Add notes to your work sessions
- **View Sessions**: See all your recorded work sessions
- **Summary Reports**: Get summaries for today, this week, this month, or all time
- **Data Persistence**: All data stored locally in JSON format
- **Status Check**: See if you're currently clocked in or out
- **Session Management**: Delete sessions if needed

## Requirements

- Python 3.6 or higher (no external dependencies required!)

## Installation

1. Clone this repository or download the files
2. Make sure you have Python 3.6 or higher installed

That's it! No external dependencies required.

## Quick Start Guide (For Beginners)

### Using the Web Interface (Easiest!)

1. Open your terminal/command prompt
2. Navigate to this folder:
   ```bash
   cd /path/to/medical-councel
   ```
3. Start the web server:
   ```bash
   python3 work_tracker_web.py
   ```
4. Open your web browser and go to: **http://localhost:8000**
5. Click the buttons to track your time!
6. Press Ctrl+C in the terminal to stop the server when done

### Using the Command Line

See the detailed commands below in the "Command-Line Usage" section.

---

## Web Interface Usage

The web interface is self-explanatory with big, clickable buttons:

- **Clock In** button - Start tracking your work time
- **Clock Out** button - Stop tracking your work time
- **Add a note** - Optional text field for notes
- **View All Sessions** - See all your work sessions
- **Today/Week/Month** - View summaries for different time periods

The timer updates automatically every second when you're clocked in!

---

## Command-Line Usage

### Basic Commands

**Clock In** - Start tracking your work time:
```bash
python3 work_tracker.py in
```

**Clock In with Note**:
```bash
python3 work_tracker.py in --note "Working on project X"
```

**Clock Out** - Stop tracking your work time:
```bash
python3 work_tracker.py out
```

**Clock Out with Note**:
```bash
python3 work_tracker.py out --note "Completed task Y"
```

**Check Status** - See if you're currently clocked in:
```bash
python3 work_tracker.py status
```

### Viewing Your Work Sessions

**View All Sessions**:
```bash
python3 work_tracker.py view
```

**View Last 5 Sessions**:
```bash
python3 work_tracker.py view --limit 5
```

**View Sessions for a Specific Date**:
```bash
python3 work_tracker.py view --date 2025-11-18
```

### Summary Reports

**All Time Summary**:
```bash
python3 work_tracker.py summary
```

**Today's Summary**:
```bash
python3 work_tracker.py summary --period today
```

**This Week's Summary**:
```bash
python3 work_tracker.py summary --period week
```

**This Month's Summary**:
```bash
python3 work_tracker.py summary --period month
```

### Managing Sessions

**Delete a Session** (use session number from view command):
```bash
python3 work_tracker.py delete 5
```

### Advanced Options

**Use a Different Data File**:
```bash
python3 work_tracker.py in --file my_work_hours.json
```

## Example Workflow

```bash
# Start your work day
$ python3 work_tracker.py in --note "Morning shift"
✓ Clocked in at 2025-11-18 09:00:00
  Note: Morning shift

# Check your status
$ python3 work_tracker.py status
✓ Currently clocked in
  Started: 2025-11-18 09:00:00
  Duration: 02:30:15
  Note: Morning shift

# Take a lunch break
$ python3 work_tracker.py out
✓ Clocked out at 2025-11-18 12:00:00
  Duration: 03:00:00

# Return from lunch
$ python3 work_tracker.py in --note "Afternoon shift"
✓ Clocked in at 2025-11-18 13:00:00
  Note: Afternoon shift

# End your work day
$ python3 work_tracker.py out
✓ Clocked out at 2025-11-18 17:30:00
  Duration: 04:30:00

# View today's summary
$ python3 work_tracker.py summary --period today
================================================================================
SUMMARY - TODAY
================================================================================
Total sessions: 2
Completed sessions: 2
Total hours worked: 07:30:00
Average per session: 03:45:00
================================================================================
```

## Data Storage

Work sessions are stored in `work_hours.json` in the same directory as the script. The file uses JSON format and can be backed up or transferred to other devices.

Example data structure:
```json
[
  {
    "clock_in": "2025-11-18T09:00:00",
    "clock_out": "2025-11-18T17:30:00",
    "note": "Working on project"
  }
]
```

## Tips

1. **Always clock out**: Remember to clock out before leaving work to keep accurate records
2. **Use notes**: Add notes to help remember what you worked on
3. **Regular reviews**: Use `summary --period week` to review your weekly hours
4. **Backup your data**: Periodically backup the `work_hours.json` file
5. **Multiple projects**: Use different data files (`--file`) to track different projects

## Troubleshooting

**Already clocked in error**: If you try to clock in while already clocked in, use `status` to check your current session, then clock out first.

**No sessions found**: Make sure you're in the correct directory or specify the right data file with `--file`.

**Wrong time recorded**: You can delete incorrect sessions using the `delete` command.

## License

Free to use and modify as needed.

## Contributing

Feel free to suggest improvements or report issues!
