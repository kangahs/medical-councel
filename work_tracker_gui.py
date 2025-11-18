#!/usr/bin/env python3
"""
Work Hours Tracker GUI - A graphical interface for tracking your working hours
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class WorkTracker:
    """Backend class for tracking work hours"""

    def __init__(self, data_file: str = "work_hours.json"):
        self.data_file = data_file
        self.sessions = self.load_sessions()

    def load_sessions(self) -> List[Dict]:
        """Load work sessions from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []

    def save_sessions(self):
        """Save work sessions to JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.sessions, f, indent=2)

    def clock_in(self, note: Optional[str] = None) -> tuple[bool, str]:
        """Start a new work session"""
        if self.sessions and not self.sessions[-1].get('clock_out'):
            return False, "You already have an active session. Please clock out first."

        session = {
            'clock_in': datetime.now().isoformat(),
            'clock_out': None,
            'note': note if note else None
        }
        self.sessions.append(session)
        self.save_sessions()
        return True, f"Clocked in at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    def clock_out(self, note: Optional[str] = None) -> tuple[bool, str, timedelta]:
        """End the current work session"""
        if not self.sessions:
            return False, "No sessions found. Please clock in first.", timedelta()

        if self.sessions[-1].get('clock_out'):
            return False, "No active session. Please clock in first.", timedelta()

        self.sessions[-1]['clock_out'] = datetime.now().isoformat()
        if note:
            current_note = self.sessions[-1].get('note', '')
            if current_note:
                self.sessions[-1]['note'] = f"{current_note} | {note}"
            else:
                self.sessions[-1]['note'] = note

        clock_in_time = datetime.fromisoformat(self.sessions[-1]['clock_in'])
        clock_out_time = datetime.now()
        duration = clock_out_time - clock_in_time

        self.save_sessions()
        return True, f"Clocked out at {clock_out_time.strftime('%Y-%m-%d %H:%M:%S')}", duration

    def get_active_session(self) -> Optional[Dict]:
        """Get the currently active session if any"""
        if self.sessions and not self.sessions[-1].get('clock_out'):
            return self.sessions[-1]
        return None

    def get_sessions_for_period(self, period: str = 'all') -> List[Dict]:
        """Get sessions for a specific period"""
        if not self.sessions:
            return []

        now = datetime.now()
        filtered_sessions = []

        for session in self.sessions:
            clock_in = datetime.fromisoformat(session['clock_in'])

            if period == 'today':
                if clock_in.date() == now.date():
                    filtered_sessions.append(session)
            elif period == 'week':
                week_start = now - timedelta(days=now.weekday())
                if clock_in.date() >= week_start.date():
                    filtered_sessions.append(session)
            elif period == 'month':
                if clock_in.month == now.month and clock_in.year == now.year:
                    filtered_sessions.append(session)
            else:  # all
                filtered_sessions.append(session)

        return filtered_sessions

    def calculate_total_duration(self, sessions: List[Dict]) -> timedelta:
        """Calculate total duration for a list of sessions"""
        total = timedelta()
        for session in sessions:
            if session.get('clock_out'):
                clock_in = datetime.fromisoformat(session['clock_in'])
                clock_out = datetime.fromisoformat(session['clock_out'])
                total += (clock_out - clock_in)
        return total

    @staticmethod
    def format_duration(duration: timedelta) -> str:
        """Format a timedelta as HH:MM:SS"""
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


class WorkTrackerGUI:
    """GUI class for the work tracker"""

    def __init__(self, root):
        self.root = root
        self.root.title("Work Hours Tracker")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # Set color scheme
        self.bg_color = "#f0f0f0"
        self.primary_color = "#4CAF50"
        self.secondary_color = "#2196F3"
        self.danger_color = "#f44336"

        self.tracker = WorkTracker()

        # Configure style
        style = ttk.Style()
        style.theme_use('clam')

        self.setup_ui()
        self.update_status()

        # Auto-update status every second
        self.root.after(1000, self.auto_update_status)

    def setup_ui(self):
        """Set up the user interface"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)

        # Title
        title_label = tk.Label(main_frame, text="Work Hours Tracker",
                              font=('Arial', 20, 'bold'), fg=self.primary_color)
        title_label.grid(row=0, column=0, pady=10)

        # Status Frame
        status_frame = ttk.LabelFrame(main_frame, text="Current Status", padding="10")
        status_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)
        status_frame.columnconfigure(0, weight=1)

        self.status_label = tk.Label(status_frame, text="Not clocked in",
                                     font=('Arial', 14), fg=self.danger_color)
        self.status_label.grid(row=0, column=0, pady=5)

        self.duration_label = tk.Label(status_frame, text="", font=('Arial', 12))
        self.duration_label.grid(row=1, column=0, pady=5)

        # Control Frame
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=10)

        # Note entry
        tk.Label(control_frame, text="Note (optional):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.note_entry = ttk.Entry(control_frame, width=50)
        self.note_entry.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=5)

        # Buttons frame
        buttons_frame = ttk.Frame(control_frame)
        buttons_frame.grid(row=1, column=0, columnspan=3, pady=10)

        # Clock In/Out buttons
        self.clock_in_btn = tk.Button(buttons_frame, text="Clock In",
                                      command=self.clock_in, bg=self.primary_color,
                                      fg='white', font=('Arial', 12, 'bold'),
                                      width=12, height=2)
        self.clock_in_btn.grid(row=0, column=0, padx=5)

        self.clock_out_btn = tk.Button(buttons_frame, text="Clock Out",
                                       command=self.clock_out, bg=self.danger_color,
                                       fg='white', font=('Arial', 12, 'bold'),
                                       width=12, height=2, state=tk.DISABLED)
        self.clock_out_btn.grid(row=0, column=1, padx=5)

        # View buttons
        view_frame = ttk.Frame(control_frame)
        view_frame.grid(row=2, column=0, columnspan=3, pady=10)

        tk.Button(view_frame, text="View All Sessions", command=self.view_all_sessions,
                 bg=self.secondary_color, fg='white', font=('Arial', 10),
                 width=15).grid(row=0, column=0, padx=5)

        tk.Button(view_frame, text="Today's Summary", command=lambda: self.show_summary('today'),
                 bg=self.secondary_color, fg='white', font=('Arial', 10),
                 width=15).grid(row=0, column=1, padx=5)

        tk.Button(view_frame, text="Week Summary", command=lambda: self.show_summary('week'),
                 bg=self.secondary_color, fg='white', font=('Arial', 10),
                 width=15).grid(row=0, column=2, padx=5)

        tk.Button(view_frame, text="Month Summary", command=lambda: self.show_summary('month'),
                 bg=self.secondary_color, fg='white', font=('Arial', 10),
                 width=15).grid(row=0, column=3, padx=5)

        # Display area
        display_frame = ttk.LabelFrame(main_frame, text="Information", padding="10")
        display_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        display_frame.columnconfigure(0, weight=1)
        display_frame.rowconfigure(0, weight=1)

        self.display_text = scrolledtext.ScrolledText(display_frame, wrap=tk.WORD,
                                                      font=('Courier', 10), height=15)
        self.display_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Initial message
        self.display_text.insert(tk.END, "Welcome to Work Hours Tracker!\n\n")
        self.display_text.insert(tk.END, "Click 'Clock In' to start tracking your work time.\n")
        self.display_text.insert(tk.END, "You can add optional notes before clocking in or out.\n\n")
        self.display_text.insert(tk.END, "Use the buttons above to view your sessions and summaries.\n")

    def update_status(self):
        """Update the status display"""
        active_session = self.tracker.get_active_session()

        if active_session:
            clock_in_time = datetime.fromisoformat(active_session['clock_in'])
            duration = datetime.now() - clock_in_time

            self.status_label.config(text="✓ Currently Clocked In", fg=self.primary_color)
            self.duration_label.config(
                text=f"Started: {clock_in_time.strftime('%Y-%m-%d %H:%M:%S')} | "
                     f"Duration: {self.tracker.format_duration(duration)}"
            )

            self.clock_in_btn.config(state=tk.DISABLED)
            self.clock_out_btn.config(state=tk.NORMAL)
        else:
            self.status_label.config(text="Currently Clocked Out", fg=self.danger_color)
            self.duration_label.config(text="")

            self.clock_in_btn.config(state=tk.NORMAL)
            self.clock_out_btn.config(state=tk.DISABLED)

    def auto_update_status(self):
        """Auto-update status every second"""
        self.update_status()
        self.root.after(1000, self.auto_update_status)

    def clock_in(self):
        """Handle clock in button click"""
        note = self.note_entry.get().strip()
        success, message = self.tracker.clock_in(note if note else None)

        if success:
            self.display_text.insert(tk.END, f"\n✓ {message}\n")
            if note:
                self.display_text.insert(tk.END, f"  Note: {note}\n")
            self.note_entry.delete(0, tk.END)
            self.update_status()
        else:
            messagebox.showerror("Error", message)

        self.display_text.see(tk.END)

    def clock_out(self):
        """Handle clock out button click"""
        note = self.note_entry.get().strip()
        success, message, duration = self.tracker.clock_out(note if note else None)

        if success:
            self.display_text.insert(tk.END, f"\n✓ {message}\n")
            self.display_text.insert(tk.END, f"  Duration: {self.tracker.format_duration(duration)}\n")
            if note:
                self.display_text.insert(tk.END, f"  Note: {note}\n")
            self.note_entry.delete(0, tk.END)
            self.update_status()
        else:
            messagebox.showerror("Error", message)

        self.display_text.see(tk.END)

    def view_all_sessions(self):
        """Display all work sessions"""
        sessions = self.tracker.sessions

        if not sessions:
            self.display_text.delete(1.0, tk.END)
            self.display_text.insert(tk.END, "No sessions recorded yet.\n")
            return

        self.display_text.delete(1.0, tk.END)
        self.display_text.insert(tk.END, "="*80 + "\n")
        self.display_text.insert(tk.END, "ALL WORK SESSIONS\n")
        self.display_text.insert(tk.END, "="*80 + "\n\n")

        total_duration = timedelta()

        for i, session in enumerate(sessions, 1):
            clock_in = datetime.fromisoformat(session['clock_in'])
            clock_out = datetime.fromisoformat(session['clock_out']) if session.get('clock_out') else None

            self.display_text.insert(tk.END, f"Session {i}:\n")
            self.display_text.insert(tk.END, f"  In:  {clock_in.strftime('%Y-%m-%d %H:%M:%S')}\n")

            if clock_out:
                duration = clock_out - clock_in
                total_duration += duration
                self.display_text.insert(tk.END, f"  Out: {clock_out.strftime('%Y-%m-%d %H:%M:%S')}\n")
                self.display_text.insert(tk.END, f"  Duration: {self.tracker.format_duration(duration)}\n")
            else:
                duration = datetime.now() - clock_in
                total_duration += duration
                self.display_text.insert(tk.END, f"  Out: ACTIVE (running {self.tracker.format_duration(duration)})\n")

            if session.get('note'):
                self.display_text.insert(tk.END, f"  Note: {session['note']}\n")

            self.display_text.insert(tk.END, "\n")

        self.display_text.insert(tk.END, "-"*80 + "\n")
        self.display_text.insert(tk.END, f"Total time: {self.tracker.format_duration(total_duration)}\n")
        self.display_text.insert(tk.END, "="*80 + "\n")

        self.display_text.see(tk.END)

    def show_summary(self, period: str):
        """Show summary for a specific period"""
        sessions = self.tracker.get_sessions_for_period(period)

        if not sessions:
            self.display_text.delete(1.0, tk.END)
            self.display_text.insert(tk.END, f"No sessions found for period: {period}\n")
            return

        total_duration = self.tracker.calculate_total_duration(sessions)
        completed_sessions = sum(1 for s in sessions if s.get('clock_out'))

        self.display_text.delete(1.0, tk.END)
        self.display_text.insert(tk.END, "="*80 + "\n")
        self.display_text.insert(tk.END, f"SUMMARY - {period.upper()}\n")
        self.display_text.insert(tk.END, "="*80 + "\n\n")
        self.display_text.insert(tk.END, f"Total sessions: {len(sessions)}\n")
        self.display_text.insert(tk.END, f"Completed sessions: {completed_sessions}\n")

        if len(sessions) > completed_sessions:
            self.display_text.insert(tk.END, f"Active sessions: {len(sessions) - completed_sessions}\n")

        self.display_text.insert(tk.END, f"Total hours worked: {self.tracker.format_duration(total_duration)}\n")

        if completed_sessions > 0:
            avg_duration = total_duration / completed_sessions
            self.display_text.insert(tk.END, f"Average per session: {self.tracker.format_duration(avg_duration)}\n")

        self.display_text.insert(tk.END, "\n" + "="*80 + "\n")

        self.display_text.see(tk.END)


def main():
    """Main entry point"""
    root = tk.Tk()
    app = WorkTrackerGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
