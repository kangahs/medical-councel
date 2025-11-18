#!/usr/bin/env python3
"""
Work Hours Tracker - A simple CLI application to track your working hours
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import argparse


class WorkTracker:
    """Main class for tracking work hours"""

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
                print(f"Warning: Could not read {self.data_file}, starting fresh")
                return []
        return []

    def save_sessions(self):
        """Save work sessions to JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.sessions, f, indent=2)

    def clock_in(self, note: Optional[str] = None):
        """Start a new work session"""
        # Check if there's an active session
        if self.sessions and not self.sessions[-1].get('clock_out'):
            print("Error: You already have an active session. Please clock out first.")
            print(f"Active session started at: {self.sessions[-1]['clock_in']}")
            return

        session = {
            'clock_in': datetime.now().isoformat(),
            'clock_out': None,
            'note': note
        }
        self.sessions.append(session)
        self.save_sessions()
        print(f"✓ Clocked in at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        if note:
            print(f"  Note: {note}")

    def clock_out(self, note: Optional[str] = None):
        """End the current work session"""
        if not self.sessions:
            print("Error: No sessions found. Please clock in first.")
            return

        if self.sessions[-1].get('clock_out'):
            print("Error: No active session. Please clock in first.")
            return

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
        print(f"✓ Clocked out at {clock_out_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Duration: {self.format_duration(duration)}")

    def status(self):
        """Show current status"""
        if not self.sessions:
            print("No sessions recorded yet.")
            return

        last_session = self.sessions[-1]
        if not last_session.get('clock_out'):
            clock_in_time = datetime.fromisoformat(last_session['clock_in'])
            duration = datetime.now() - clock_in_time
            print(f"✓ Currently clocked in")
            print(f"  Started: {clock_in_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  Duration: {self.format_duration(duration)}")
            if last_session.get('note'):
                print(f"  Note: {last_session['note']}")
        else:
            print("✓ Currently clocked out")
            clock_out_time = datetime.fromisoformat(last_session['clock_out'])
            print(f"  Last session ended: {clock_out_time.strftime('%Y-%m-%d %H:%M:%S')}")

    def view_sessions(self, limit: Optional[int] = None, date: Optional[str] = None):
        """View recorded work sessions"""
        if not self.sessions:
            print("No sessions recorded yet.")
            return

        sessions_to_show = self.sessions.copy()

        # Filter by date if specified
        if date:
            try:
                filter_date = datetime.strptime(date, '%Y-%m-%d').date()
                sessions_to_show = [
                    s for s in sessions_to_show
                    if datetime.fromisoformat(s['clock_in']).date() == filter_date
                ]
                if not sessions_to_show:
                    print(f"No sessions found for {date}")
                    return
            except ValueError:
                print("Error: Invalid date format. Use YYYY-MM-DD")
                return

        # Limit number of sessions if specified
        if limit:
            sessions_to_show = sessions_to_show[-limit:]

        print("\n" + "="*80)
        print("WORK SESSIONS")
        print("="*80)

        total_duration = timedelta()

        for i, session in enumerate(sessions_to_show, 1):
            clock_in = datetime.fromisoformat(session['clock_in'])
            clock_out = datetime.fromisoformat(session['clock_out']) if session.get('clock_out') else None

            print(f"\nSession {i}:")
            print(f"  In:  {clock_in.strftime('%Y-%m-%d %H:%M:%S')}")

            if clock_out:
                duration = clock_out - clock_in
                total_duration += duration
                print(f"  Out: {clock_out.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"  Duration: {self.format_duration(duration)}")
            else:
                duration = datetime.now() - clock_in
                total_duration += duration
                print(f"  Out: ACTIVE (running {self.format_duration(duration)})")

            if session.get('note'):
                print(f"  Note: {session['note']}")

        print("\n" + "-"*80)
        print(f"Total time: {self.format_duration(total_duration)}")
        print("="*80 + "\n")

    def summary(self, period: str = 'all'):
        """Show summary of work hours"""
        if not self.sessions:
            print("No sessions recorded yet.")
            return

        now = datetime.now()

        # Filter sessions based on period
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

        if not filtered_sessions:
            print(f"No sessions found for period: {period}")
            return

        # Calculate totals
        total_duration = timedelta()
        completed_sessions = 0

        for session in filtered_sessions:
            if session.get('clock_out'):
                clock_in = datetime.fromisoformat(session['clock_in'])
                clock_out = datetime.fromisoformat(session['clock_out'])
                total_duration += (clock_out - clock_in)
                completed_sessions += 1

        print("\n" + "="*80)
        print(f"SUMMARY - {period.upper()}")
        print("="*80)
        print(f"Total sessions: {len(filtered_sessions)}")
        print(f"Completed sessions: {completed_sessions}")
        if len(filtered_sessions) > completed_sessions:
            print(f"Active sessions: {len(filtered_sessions) - completed_sessions}")
        print(f"Total hours worked: {self.format_duration(total_duration)}")

        # Calculate average per day
        if completed_sessions > 0:
            avg_duration = total_duration / completed_sessions
            print(f"Average per session: {self.format_duration(avg_duration)}")

        print("="*80 + "\n")

    def delete_session(self, index: int):
        """Delete a specific session by index"""
        if not self.sessions:
            print("No sessions to delete.")
            return

        if index < 1 or index > len(self.sessions):
            print(f"Error: Invalid session index. Must be between 1 and {len(self.sessions)}")
            return

        session = self.sessions[index - 1]
        clock_in = datetime.fromisoformat(session['clock_in'])
        print(f"Deleting session from {clock_in.strftime('%Y-%m-%d %H:%M:%S')}")

        del self.sessions[index - 1]
        self.save_sessions()
        print("✓ Session deleted")

    @staticmethod
    def format_duration(duration: timedelta) -> str:
        """Format a timedelta as HH:MM:SS"""
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Work Hours Tracker - Track your working hours',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s in                    # Clock in
  %(prog)s in --note "Morning shift"  # Clock in with note
  %(prog)s out                   # Clock out
  %(prog)s status                # Check current status
  %(prog)s view                  # View all sessions
  %(prog)s view --limit 5        # View last 5 sessions
  %(prog)s view --date 2025-11-18  # View sessions for specific date
  %(prog)s summary               # Summary of all time
  %(prog)s summary --period today  # Today's summary
  %(prog)s delete 5              # Delete session #5
        """
    )

    parser.add_argument('command',
                       choices=['in', 'out', 'status', 'view', 'summary', 'delete'],
                       help='Command to execute')
    parser.add_argument('--note', type=str, help='Add a note to the session')
    parser.add_argument('--limit', type=int, help='Limit number of sessions to view')
    parser.add_argument('--date', type=str, help='Filter by date (YYYY-MM-DD)')
    parser.add_argument('--period', type=str,
                       choices=['today', 'week', 'month', 'all'],
                       default='all',
                       help='Period for summary')
    parser.add_argument('--file', type=str, default='work_hours.json',
                       help='Data file to use (default: work_hours.json)')
    parser.add_argument('index', type=int, nargs='?', help='Session index (for delete command)')

    args = parser.parse_args()

    tracker = WorkTracker(data_file=args.file)

    if args.command == 'in':
        tracker.clock_in(note=args.note)
    elif args.command == 'out':
        tracker.clock_out(note=args.note)
    elif args.command == 'status':
        tracker.status()
    elif args.command == 'view':
        tracker.view_sessions(limit=args.limit, date=args.date)
    elif args.command == 'summary':
        tracker.summary(period=args.period)
    elif args.command == 'delete':
        if args.index is None:
            print("Error: Please specify session index to delete")
            print("Usage: work_tracker.py delete <index>")
        else:
            tracker.delete_session(args.index)


if __name__ == '__main__':
    main()
