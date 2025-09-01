#!/usr/bin/env python3
"""
Production Deployment Script for Sound to Text Web Application
Handles production deployment with Gunicorn, environment setup, and monitoring.
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path

class WebAppDeployer:
    def __init__(self):
        self.app_dir = Path(__file__).parent
        self.venv_dir = self.app_dir / 'venv'
        self.log_dir = self.app_dir / 'logs'
        self.pid_file = self.app_dir / 'app.pid'
        
    def setup_environment(self):
        """Set up Python virtual environment and install dependencies"""
        print("🔧 Setting up environment...")
        
        # Create logs directory
        self.log_dir.mkdir(exist_ok=True)
        
        # Create virtual environment if it doesn't exist
        if not self.venv_dir.exists():
            print("Creating virtual environment...")
            subprocess.run([sys.executable, '-m', 'venv', str(self.venv_dir)], check=True)
        
        # Get pip path
        if os.name == 'nt':  # Windows
            pip_path = self.venv_dir / 'Scripts' / 'pip.exe'
            python_path = self.venv_dir / 'Scripts' / 'python.exe'
        else:  # Unix/Linux/macOS
            pip_path = self.venv_dir / 'bin' / 'pip'
            python_path = self.venv_dir / 'bin' / 'python'
        
        # Install dependencies
        print("Installing dependencies...")
        subprocess.run([
            str(pip_path), 'install', '-r', 'web_requirements.txt'
        ], check=True)
        
        print("✅ Environment setup complete")
        return python_path
    
    def check_system_dependencies(self):
        """Check for required system dependencies"""
        print("🔍 Checking system dependencies...")
        
        dependencies = {
            'ffmpeg': 'FFmpeg is required for audio format conversion',
            'portaudio19-dev': 'PortAudio is required for microphone input (Linux)',
        }
        
        missing = []
        
        # Check FFmpeg
        try:
            subprocess.run(['ffmpeg', '-version'], 
                         capture_output=True, check=True)
            print("✅ FFmpeg found")
        except (subprocess.CalledProcessError, FileNotFoundError):
            missing.append('ffmpeg')
            print("❌ FFmpeg not found")
        
        if missing:
            print("\n⚠️ Missing system dependencies:")
            for dep in missing:
                print(f"  - {dep}: {dependencies.get(dep, 'Required for audio processing')}")
            
            print("\nInstallation commands:")
            print("Ubuntu/Debian: sudo apt install ffmpeg portaudio19-dev")
            print("macOS: brew install ffmpeg portaudio")
            print("Windows: Download FFmpeg from https://ffmpeg.org/download.html")
            
            return False
        
        print("✅ All system dependencies found")
        return True
    
    def create_config(self):
        """Create production configuration"""
        config = {
            'SECRET_KEY': os.urandom(24).hex(),
            'MAX_CONTENT_LENGTH': 100 * 1024 * 1024,  # 100MB
            'UPLOAD_FOLDER': 'uploads',
            'RESULTS_FOLDER': 'results',
            'DEBUG': False,
            'TESTING': False
        }
        
        config_file = self.app_dir / 'config.json'
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Configuration saved to {config_file}")
        return config_file
    
    def start_production_server(self, python_path, port=5000, workers=4):
        """Start production server with Gunicorn"""
        print(f"🚀 Starting production server on port {port}...")
        
        # Create Gunicorn command
        if os.name == 'nt':  # Windows
            gunicorn_path = self.venv_dir / 'Scripts' / 'gunicorn.exe'
        else:  # Unix/Linux/macOS
            gunicorn_path = self.venv_dir / 'bin' / 'gunicorn'
        
        cmd = [
            str(gunicorn_path),
            '--bind', f'0.0.0.0:{port}',
            '--workers', str(workers),
            '--worker-class', 'sync',
            '--timeout', '300',
            '--keep-alive', '2',
            '--max-requests', '1000',
            '--max-requests-jitter', '100',
            '--access-logfile', str(self.log_dir / 'access.log'),
            '--error-logfile', str(self.log_dir / 'error.log'),
            '--log-level', 'info',
            '--pid', str(self.pid_file),
            '--daemon',
            'app:app'
        ]
        
        try:
            subprocess.run(cmd, check=True, cwd=self.app_dir)
            
            # Wait a moment and check if server started
            time.sleep(2)
            if self.is_server_running():
                print(f"✅ Production server started successfully")
                print(f"🌐 Access the application at: http://localhost:{port}")
                print(f"📊 Health check: http://localhost:{port}/health")
                print(f"📝 Logs: {self.log_dir}")
                return True
            else:
                print("❌ Server failed to start")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to start server: {e}")
            return False
    
    def stop_server(self):
        """Stop the production server"""
        if not self.pid_file.exists():
            print("❌ No PID file found. Server may not be running.")
            return
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            print(f"🛑 Stopping server (PID: {pid})...")
            
            if os.name == 'nt':  # Windows
                subprocess.run(['taskkill', '/F', '/PID', str(pid)], check=True)
            else:  # Unix/Linux/macOS
                subprocess.run(['kill', str(pid)], check=True)
            
            # Remove PID file
            self.pid_file.unlink()
            print("✅ Server stopped successfully")
            
        except Exception as e:
            print(f"❌ Error stopping server: {e}")
    
    def is_server_running(self):
        """Check if server is running"""
        if not self.pid_file.exists():
            return False
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            if os.name == 'nt':  # Windows
                result = subprocess.run(['tasklist', '/FI', f'PID eq {pid}'], 
                                      capture_output=True, text=True)
                return str(pid) in result.stdout
            else:  # Unix/Linux/macOS
                try:
                    os.kill(pid, 0)  # Signal 0 checks if process exists
                    return True
                except OSError:
                    return False
                    
        except Exception:
            return False
    
    def show_status(self):
        """Show server status and logs"""
        print("📊 Server Status")
        print("=" * 40)
        
        if self.is_server_running():
            print("Status: ✅ Running")
            
            if self.pid_file.exists():
                with open(self.pid_file, 'r') as f:
                    pid = f.read().strip()
                print(f"PID: {pid}")
        else:
            print("Status: ❌ Not running")
        
        # Show recent logs
        access_log = self.log_dir / 'access.log'
        error_log = self.log_dir / 'error.log'
        
        if access_log.exists():
            print(f"\n📈 Recent access logs ({access_log}):")
            try:
                with open(access_log, 'r') as f:
                    lines = f.readlines()
                    for line in lines[-5:]:  # Last 5 lines
                        print(f"  {line.strip()}")
            except Exception as e:
                print(f"  Error reading access log: {e}")
        
        if error_log.exists():
            print(f"\n🚨 Recent error logs ({error_log}):")
            try:
                with open(error_log, 'r') as f:
                    lines = f.readlines()
                    for line in lines[-5:]:  # Last 5 lines
                        print(f"  {line.strip()}")
            except Exception as e:
                print(f"  Error reading error log: {e}")
    
    def deploy(self, port=5000, workers=4):
        """Full deployment process"""
        print("🎵 Sound to Text Web App - Production Deployment")
        print("=" * 60)
        
        # Check system dependencies
        if not self.check_system_dependencies():
            print("\n❌ Please install missing system dependencies first")
            return False
        
        # Setup environment
        python_path = self.setup_environment()
        
        # Create configuration
        self.create_config()
        
        # Start server
        if self.start_production_server(python_path, port, workers):
            print("\n🎉 Deployment successful!")
            print(f"Your Sound to Text web app is now running at http://localhost:{port}")
            return True
        else:
            print("\n❌ Deployment failed")
            return False

def main():
    deployer = WebAppDeployer()
    
    if len(sys.argv) < 2:
        print("Usage: python deploy.py [start|stop|restart|status|deploy]")
        print("\nCommands:")
        print("  deploy  - Full deployment (setup + start)")
        print("  start   - Start the server")
        print("  stop    - Stop the server")
        print("  restart - Restart the server")
        print("  status  - Show server status")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'deploy':
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
        workers = int(sys.argv[3]) if len(sys.argv) > 3 else 4
        deployer.deploy(port, workers)
        
    elif command == 'start':
        if deployer.is_server_running():
            print("❌ Server is already running")
        else:
            python_path = deployer.setup_environment()
            port = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
            workers = int(sys.argv[3]) if len(sys.argv) > 3 else 4
            deployer.start_production_server(python_path, port, workers)
    
    elif command == 'stop':
        deployer.stop_server()
    
    elif command == 'restart':
        print("🔄 Restarting server...")
        deployer.stop_server()
        time.sleep(2)
        python_path = deployer.setup_environment()
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
        workers = int(sys.argv[3]) if len(sys.argv) > 3 else 4
        deployer.start_production_server(python_path, port, workers)
    
    elif command == 'status':
        deployer.show_status()
    
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()