#!/usr/bin/env python3
"""
Work Hours Tracker Web Interface - A web-based GUI for tracking your working hours
Uses Python's built-in http.server - no external dependencies needed!
"""

import http.server
import socketserver
import json
import os
import urllib.parse
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

    def clock_in(self, note: Optional[str] = None) -> tuple:
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

    def clock_out(self, note: Optional[str] = None) -> tuple:
        """End the current work session"""
        if not self.sessions:
            return False, "No sessions found. Please clock in first.", "00:00:00"

        if self.sessions[-1].get('clock_out'):
            return False, "No active session. Please clock in first.", "00:00:00"

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
        return True, f"Clocked out at {clock_out_time.strftime('%Y-%m-%d %H:%M:%S')}", self.format_duration(duration)

    def get_status(self) -> Dict:
        """Get current status"""
        if not self.sessions:
            return {
                'active': False,
                'message': 'Not clocked in',
                'duration': '00:00:00'
            }

        last_session = self.sessions[-1]
        if not last_session.get('clock_out'):
            clock_in_time = datetime.fromisoformat(last_session['clock_in'])
            duration = datetime.now() - clock_in_time
            return {
                'active': True,
                'message': f"Clocked in since {clock_in_time.strftime('%Y-%m-%d %H:%M:%S')}",
                'duration': self.format_duration(duration),
                'note': last_session.get('note', '')
            }
        else:
            return {
                'active': False,
                'message': 'Not clocked in',
                'duration': '00:00:00'
            }

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

    def get_summary(self, period: str = 'all') -> Dict:
        """Get summary for a period"""
        sessions = self.get_sessions_for_period(period)

        if not sessions:
            return {
                'total_sessions': 0,
                'completed_sessions': 0,
                'active_sessions': 0,
                'total_hours': '00:00:00',
                'average_per_session': '00:00:00'
            }

        total_duration = self.calculate_total_duration(sessions)
        completed_sessions = sum(1 for s in sessions if s.get('clock_out'))

        avg_duration = total_duration / completed_sessions if completed_sessions > 0 else timedelta()

        return {
            'total_sessions': len(sessions),
            'completed_sessions': completed_sessions,
            'active_sessions': len(sessions) - completed_sessions,
            'total_hours': self.format_duration(total_duration),
            'average_per_session': self.format_duration(avg_duration)
        }

    def format_sessions(self, sessions: List[Dict]) -> List[Dict]:
        """Format sessions for display"""
        formatted = []
        for i, session in enumerate(sessions, 1):
            clock_in = datetime.fromisoformat(session['clock_in'])
            clock_out = datetime.fromisoformat(session['clock_out']) if session.get('clock_out') else None

            formatted_session = {
                'id': i,
                'clock_in': clock_in.strftime('%Y-%m-%d %H:%M:%S'),
                'note': session.get('note', '')
            }

            if clock_out:
                duration = clock_out - clock_in
                formatted_session['clock_out'] = clock_out.strftime('%Y-%m-%d %H:%M:%S')
                formatted_session['duration'] = self.format_duration(duration)
                formatted_session['active'] = False
            else:
                duration = datetime.now() - clock_in
                formatted_session['clock_out'] = 'ACTIVE'
                formatted_session['duration'] = self.format_duration(duration)
                formatted_session['active'] = True

            formatted.append(formatted_session)

        return formatted

    @staticmethod
    def format_duration(duration: timedelta) -> str:
        """Format a timedelta as HH:MM:SS"""
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


# Global tracker instance
tracker = WorkTracker()


class WorkTrackerRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom request handler for the work tracker"""

    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/' or self.path == '/index.html':
            self.send_html_page()
        elif self.path == '/api/status':
            self.send_json_response(tracker.get_status())
        elif self.path.startswith('/api/sessions/'):
            period = self.path.split('/')[-1]
            sessions = tracker.get_sessions_for_period(period)
            formatted_sessions = tracker.format_sessions(sessions)
            self.send_json_response(formatted_sessions)
        elif self.path.startswith('/api/summary/'):
            period = self.path.split('/')[-1]
            summary = tracker.get_summary(period)
            self.send_json_response(summary)
        else:
            self.send_error(404, "File not found")

    def do_POST(self):
        """Handle POST requests"""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')

        try:
            data = json.loads(post_data) if post_data else {}
        except json.JSONDecodeError:
            data = {}

        note = data.get('note', '').strip() if data else None

        if self.path == '/api/clock_in':
            success, message = tracker.clock_in(note if note else None)
            self.send_json_response({'success': success, 'message': message})
        elif self.path == '/api/clock_out':
            success, message, duration = tracker.clock_out(note if note else None)
            self.send_json_response({'success': success, 'message': message, 'duration': duration})
        else:
            self.send_error(404, "Endpoint not found")

    def send_json_response(self, data):
        """Send a JSON response"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def send_html_page(self):
        """Send the HTML page"""
        html_content = self.get_html_content()
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Content-length', len(html_content))
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))

    def get_html_content(self):
        """Get the HTML content"""
        # Check if template file exists
        template_path = os.path.join('templates', 'index.html')
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()

        # Fallback to embedded HTML if template doesn't exist
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Work Hours Tracker</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f0f0f0; }
        .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #667eea; text-align: center; }
        .status { text-align: center; padding: 20px; background: #f8f9fa; border-radius: 10px; margin: 20px 0; }
        .btn { padding: 15px 30px; margin: 5px; font-size: 16px; border: none; border-radius: 5px; cursor: pointer; color: white; }
        .btn-primary { background: #4CAF50; }
        .btn-danger { background: #f44336; }
        .btn-secondary { background: #2196F3; }
        .btn:disabled { opacity: 0.5; cursor: not-allowed; }
        input { width: 100%; padding: 10px; margin: 10px 0; box-sizing: border-box; }
    </style>
</head>
<body>
    <div class="container">
        <h1>⏰ Work Hours Tracker</h1>
        <div class="status">
            <h2 id="statusText">Loading...</h2>
            <p id="duration">00:00:00</p>
        </div>
        <input type="text" id="note" placeholder="Add a note (optional)...">
        <div style="text-align: center;">
            <button id="clockIn" class="btn btn-primary" onclick="clockIn()">Clock In</button>
            <button id="clockOut" class="btn btn-danger" onclick="clockOut()">Clock Out</button>
        </div>
        <hr>
        <div style="text-align: center; margin: 20px 0;">
            <button class="btn btn-secondary" onclick="viewSessions('all')">View All</button>
            <button class="btn btn-secondary" onclick="showSummary('today')">Today</button>
            <button class="btn btn-secondary" onclick="showSummary('week')">Week</button>
            <button class="btn btn-secondary" onclick="showSummary('month')">Month</button>
        </div>
        <div id="display" style="margin-top: 20px; padding: 20px; background: #f8f9fa; border-radius: 5px;"></div>
    </div>
    <script>
        setInterval(updateStatus, 1000);
        updateStatus();

        async function updateStatus() {
            const res = await fetch('/api/status');
            const data = await res.json();
            document.getElementById('statusText').textContent = data.active ? '✓ Clocked In' : 'Clocked Out';
            document.getElementById('duration').textContent = data.duration;
            document.getElementById('clockIn').disabled = data.active;
            document.getElementById('clockOut').disabled = !data.active;
        }

        async function clockIn() {
            const note = document.getElementById('note').value;
            await fetch('/api/clock_in', {
                method: 'POST',
                body: JSON.stringify({note: note})
            });
            document.getElementById('note').value = '';
            updateStatus();
        }

        async function clockOut() {
            const note = document.getElementById('note').value;
            await fetch('/api/clock_out', {
                method: 'POST',
                body: JSON.stringify({note: note})
            });
            document.getElementById('note').value = '';
            updateStatus();
        }

        async function viewSessions(period) {
            const res = await fetch('/api/sessions/' + period);
            const sessions = await res.json();
            let html = '<h3>Sessions</h3>';
            sessions.forEach(s => {
                html += `<p><strong>#${s.id}</strong> ${s.clock_in} - ${s.clock_out} (${s.duration})<br>${s.note}</p>`;
            });
            document.getElementById('display').innerHTML = html;
        }

        async function showSummary(period) {
            const res = await fetch('/api/summary/' + period);
            const data = await res.json();
            document.getElementById('display').innerHTML = `
                <h3>Summary - ${period}</h3>
                <p>Total Sessions: ${data.total_sessions}</p>
                <p>Completed: ${data.completed_sessions}</p>
                <p>Total Hours: ${data.total_hours}</p>
                <p>Average: ${data.average_per_session}</p>
            `;
        }
    </script>
</body>
</html>
        """

    def log_message(self, format, *args):
        """Override to reduce logging noise"""
        return


def main():
    """Main entry point"""
    PORT = 8000
    Handler = WorkTrackerRequestHandler

    print("=" * 60)
    print("Work Hours Tracker - Web Interface")
    print("=" * 60)
    print("\nNo external dependencies required - using Python's built-in server!")
    print(f"\nServer starting on port {PORT}...")
    print(f"\n🌐 Open your web browser and go to:")
    print(f"   http://localhost:{PORT}")
    print(f"\nPress Ctrl+C to stop the server")
    print("=" * 60)

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\nServer stopped. Goodbye!")


if __name__ == '__main__':
    main()
