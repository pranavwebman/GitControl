#!/usr/bin/env python3
"""
GitControl - A comprehensive GitHub CLI tool for Termux
Author: Pranav Krishna H
Version: 1.0.0
"""

import os
import sys
import time
import json
import requests
import subprocess
from datetime import datetime
from typing import Dict, List, Optional
import getpass

# ASCII Art for GitControl
GITCONTROL_ASCII = """
   ____ _ _   ____            _             
  / ___(_) |_/ ___|___  _ __ | |_ ___  _ __ 
 | |  _| | __| |   / _ \\| '_ \\| __/ _ \\| '__|
 | |_| | | |_| |__| (_) | | | | || (_) | |   
  \\____|_|\\__|\\____\\___/|_| |_|\\__\\___/|_|   
                                             
  GitHub Control Tool for Termux
  Version 1.0.0
"""

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Animation:
    """Handle text animations and effects"""
    
    @staticmethod
    def typing_effect(text: str, delay: float = 0.03):
        """Display text with typing effect"""
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)
        print()
    
    @staticmethod
    def loading_animation(message: str, duration: int = 2):
        """Display loading animation"""
        chars = ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷']
        end_time = time.time() + duration
        i = 0
        while time.time() < end_time:
            sys.stdout.write(f'\r{message} {chars[i % len(chars)]}')
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1
        print('\r' + ' ' * len(message) + '    \r', end='')
    
    @staticmethod
    def progress_bar(iteration: int, total: int, prefix: str = '', suffix: str = '', length: int = 30):
        """Display progress bar"""
        percent = (iteration / total) * 100
        filled_length = int(length * iteration // total)
        bar = '█' * filled_length + '░' * (length - filled_length)
        sys.stdout.write(f'\r{prefix} |{bar}| {percent:.1f}% {suffix}')
        sys.stdout.flush()
        if iteration == total:
            print()

class GitControl:
    """Main GitControl class for GitHub API interactions"""
    
    def __init__(self):
        self.token = None
        self.username = None
        self.base_url = "https://api.github.com"
        self.headers = {}
        self.session = requests.Session()
        self.load_config()
        
    def load_config(self):
        """Load configuration from file"""
        config_path = os.path.expanduser("~/.gitcontrol_config")
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    self.token = config.get('token')
                    self.username = config.get('username')
                    if self.token:
                        self.headers = {
                            "Authorization": f"token {self.token}",
                            "Accept": "application/vnd.github.v3+json"
                        }
                        self.session.headers.update(self.headers)
            except Exception as e:
                print(f"{Colors.FAIL}Error loading config: {e}{Colors.END}")
    
    def save_config(self):
        """Save configuration to file"""
        config_path = os.path.expanduser("~/.gitcontrol_config")
        config = {
            'token': self.token,
            'username': self.username
        }
        try:
            with open(config_path, 'w') as f:
                json.dump(config, f)
            os.chmod(config_path, 0o600)  # Secure the file
        except Exception as e:
            print(f"{Colors.FAIL}Error saving config: {e}{Colors.END}")
    
    def authenticate(self):
        """Authenticate with GitHub using token"""
        print(f"{Colors.CYAN}GitHub Authentication{Colors.END}")
        print("=" * 40)
        
        if self.token:
            use_existing = input("Use existing token? (y/n): ").lower()
            if use_existing == 'y':
                return True
        
        print(f"{Colors.WARNING}Generate a token at: https://github.com/settings/tokens{Colors.END}")
        print("Required scopes: repo, user, delete_repo")
        
        self.token = getpass.getpass("Enter your GitHub Personal Access Token: ")
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.session.headers.update(self.headers)
        
        # Verify token
        try:
            response = self.session.get(f"{self.base_url}/user")
            if response.status_code == 200:
                data = response.json()
                self.username = data['login']
                self.save_config()
                print(f"{Colors.GREEN}✓ Authentication successful as: {self.username}{Colors.END}")
                return True
            else:
                print(f"{Colors.FAIL}✗ Authentication failed: {response.status_code}{Colors.END}")
                return False
        except Exception as e:
            print(f"{Colors.FAIL}✗ Error: {e}{Colors.END}")
            return False
    
    def display_menu(self):
        """Display main menu"""
        os.system('clear')
        print(Colors.CYAN + GITCONTROL_ASCII + Colors.END)
        print(f"{Colors.GREEN}Welcome, {self.username}!{Colors.END}\n")
        
        menu_options = {
            "1": "📋 List Repositories",
            "2": "📁 Create Repository",
            "3": "🗑️ Delete Repository",
            "4": "📊 Repository Statistics",
            "5": "🔍 Search Repositories",
            "6": "📝 View User Profile",
            "7": "⭐ Star a Repository",
            "8": "🔀 Fork a Repository",
            "9": "📦 List Issues",
            "10": "🔄 Create Issue",
            "11": "📈 Repository Activity",
            "12": "🔑 Manage Collaborators",
            "13": "📤 Upload File to Repo",
            "14": "📥 Download File from Repo",
            "15": "🔄 Refresh Token",
            "16": "🚪 Exit"
        }
        
        for key, value in menu_options.items():
            print(f"{Colors.BLUE}{key}{Colors.END}. {value}")
        
        print("\n" + "=" * 40)
        choice = input(f"{Colors.CYAN}Enter your choice: {Colors.END}")
        return choice
    
    def list_repos(self):
        """List all repositories for the authenticated user"""
        print(f"\n{Colors.CYAN}📋 Fetching repositories...{Colors.END}")
        Animation.loading_animation("Loading repositories", 1)
        
        try:
            response = self.session.get(f"{self.base_url}/user/repos?per_page=100")
            if response.status_code == 200:
                repos = response.json()
                if not repos:
                    print(f"{Colors.WARNING}No repositories found.{Colors.END}")
                    return
                
                print(f"\n{Colors.GREEN}Your Repositories ({len(repos)}):{Colors.END}")
                print("=" * 60)
                for i, repo in enumerate(repos, 1):
                    print(f"{Colors.BOLD}{i}. {Colors.END}{repo['name']}")
                    print(f"   📝 {repo['description'] or 'No description'}")
                    print(f"   ⭐ {repo['stargazers_count']} stars | 🍴 {repo['forks_count']} forks")
                    print(f"   🔗 {repo['html_url']}")
                    if repo['private']:
                        print(f"   🔒 Private")
                    else:
                        print(f"   🌐 Public")
                    print("-" * 60)
                
                input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
            else:
                print(f"{Colors.FAIL}Error: {response.status_code} - {response.text}{Colors.END}")
        except Exception as e:
            print(f"{Colors.FAIL}Error: {e}{Colors.END}")
    
    def create_repo(self):
        """Create a new repository"""
        print(f"\n{Colors.CYAN}📁 Create New Repository{Colors.END}")
        print("=" * 40)
        
        name = input("Repository name: ")
        description = input("Description (optional): ")
        private = input("Private? (y/n): ").lower() == 'y'
        
        data = {
            "name": name,
            "description": description,
            "private": private,
            "auto_init": True  # Initialize with README
        }
        
        Animation.loading_animation("Creating repository", 2)
        
        try:
            response = self.session.post(f"{self.base_url}/user/repos", json=data)
            if response.status_code == 201:
                repo = response.json()
                print(f"{Colors.GREEN}✓ Repository created successfully!{Colors.END}")
                print(f"📌 Name: {repo['name']}")
                print(f"🔗 URL: {repo['html_url']}")
                
                # Clone command suggestion
                print(f"\n{Colors.CYAN}To clone this repository:{Colors.END}")
                print(f"git clone {repo['clone_url']}")
                
                input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
            else:
                print(f"{Colors.FAIL}Error: {response.status_code} - {response.text}{Colors.END}")
        except Exception as e:
            print(f"{Colors.FAIL}Error: {e}{Colors.END}")
    
    def delete_repo(self):
        """Delete a repository"""
        print(f"\n{Colors.CYAN}🗑️ Delete Repository{Colors.END}")
        print(f"{Colors.WARNING}⚠️  WARNING: This action cannot be undone!{Colors.END}")
        
        repo_name = input("Enter repository name to delete: ")
        confirm = input(f"Are you sure you want to delete '{repo_name}'? (yes/no): ")
        
        if confirm.lower() != 'yes':
            print("Deletion cancelled.")
            return
        
        # Get repository ID first
        try:
            response = self.session.get(f"{self.base_url}/repos/{self.username}/{repo_name}")
            if response.status_code == 200:
                repo = response.json()
                delete_response = self.session.delete(f"{self.base_url}/repos/{self.username}/{repo_name}")
                
                if delete_response.status_code == 204:
                    print(f"{Colors.GREEN}✓ Repository '{repo_name}' deleted successfully.{Colors.END}")
                else:
                    print(f"{Colors.FAIL}Error: {delete_response.status_code}{Colors.END}")
            else:
                print(f"{Colors.FAIL}Repository not found.{Colors.END}")
        except Exception as e:
            print(f"{Colors.FAIL}Error: {e}{Colors.END}")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
    
    def repo_stats(self):
        """Display repository statistics"""
        print(f"\n{Colors.CYAN}📊 Repository Statistics{Colors.END}")
        repo_name = input("Enter repository name: ")
        
        try:
            response = self.session.get(f"{self.base_url}/repos/{self.username}/{repo_name}")
            if response.status_code == 200:
                repo = response.json()
                
                print(f"\n{Colors.GREEN}Statistics for: {repo['name']}{Colors.END}")
                print("=" * 50)
                print(f"📝 Description: {repo['description'] or 'N/A'}")
                print(f"⭐ Stars: {repo['stargazers_count']}")
                print(f"🍴 Forks: {repo['forks_count']}")
                print(f"👀 Watchers: {repo['watchers_count']}")
                print(f"📂 Size: {repo['size']} KB")
                print(f"📅 Created: {repo['created_at'][:10]}")
                print(f"🔄 Updated: {repo['updated_at'][:10]}")
                print(f"🔒 Private: {'Yes' if repo['private'] else 'No'}")
                print(f"🌐 Language: {repo['language'] or 'N/A'}")
                print(f"🐛 Open Issues: {repo['open_issues_count']}")
                
                input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
            else:
                print(f"{Colors.FAIL}Repository not found.{Colors.END}")
        except Exception as e:
            print(f"{Colors.FAIL}Error: {e}{Colors.END}")
    
    def search_repos(self):
        """Search for repositories"""
        print(f"\n{Colors.CYAN}🔍 Search Repositories{Colors.END}")
        query = input("Enter search query: ")
        
        Animation.loading_animation("Searching", 1)
        
        try:
            response = self.session.get(f"{self.base_url}/search/repositories?q={query}")
            if response.status_code == 200:
                data = response.json()
                repos = data['items'][:10]  # Show top 10 results
                
                if not repos:
                    print(f"{Colors.WARNING}No repositories found.{Colors.END}")
                    return
                
                print(f"\n{Colors.GREEN}Search Results ({data['total_count']} found):{Colors.END}")
                print("=" * 60)
                for repo in repos:
                    print(f"{Colors.BOLD}{repo['full_name']}{Colors.END}")
                    print(f"   📝 {repo['description'] or 'No description'}")
                    print(f"   ⭐ {repo['stargazers_count']} stars | 🍴 {repo['forks_count']} forks")
                    print(f"   🔗 {repo['html_url']}")
                    print("-" * 60)
                
                input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
            else:
                print(f"{Colors.FAIL}Error: {response.status_code}{Colors.END}")
        except Exception as e:
            print(f"{Colors.FAIL}Error: {e}{Colors.END}")
    
    def view_profile(self):
        """View user profile"""
        print(f"\n{Colors.CYAN}📝 User Profile{Colors.END}")
        Animation.loading_animation("Loading profile", 1)
        
        try:
            response = self.session.get(f"{self.base_url}/user")
            if response.status_code == 200:
                user = response.json()
                
                print(f"\n{Colors.GREEN}Profile Information{Colors.END}")
                print("=" * 50)
                print(f"👤 Username: {user['login']}")
                print(f"📧 Email: {user.get('email', 'N/A')}")
                print(f"📛 Name: {user.get('name', 'N/A')}")
                print(f"🏢 Company: {user.get('company', 'N/A')}")
                print(f"📍 Location: {user.get('location', 'N/A')}")
                print(f"📅 Joined: {user['created_at'][:10]}")
                print(f"📝 Bio: {user.get('bio', 'N/A')}")
                print(f"📊 Repositories: {user['public_repos']}")
                print(f"👥 Followers: {user['followers']}")
                print(f"👤 Following: {user['following']}")
                print(f"🔗 Profile: {user['html_url']}")
                
                input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
            else:
                print(f"{Colors.FAIL}Error: {response.status_code}{Colors.END}")
        except Exception as e:
            print(f"{Colors.FAIL}Error: {e}{Colors.END}")
    
    def star_repo(self):
        """Star a repository"""
        print(f"\n{Colors.CYAN}⭐ Star a Repository{Colors.END}")
        repo_name = input("Enter repository name (owner/repo): ")
        
        try:
            response = self.session.put(f"{self.base_url}/user/starred/{repo_name}")
            if response.status_code == 204:
                print(f"{Colors.GREEN}✓ Repository starred successfully!{Colors.END}")
            else:
                print(f"{Colors.FAIL}Error: {response.status_code}{Colors.END}")
        except Exception as e:
            print(f"{Colors.FAIL}Error: {e}{Colors.END}")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
    
    def fork_repo(self):
        """Fork a repository"""
        print(f"\n{Colors.CYAN}🔀 Fork a Repository{Colors.END}")
        repo_name = input("Enter repository name (owner/repo): ")
        
        Animation.loading_animation("Forking repository", 2)
        
        try:
            response = self.session.post(f"{self.base_url}/repos/{repo_name}/forks")
            if response.status_code == 202:
                print(f"{Colors.GREEN}✓ Repository forked successfully!{Colors.END}")
                print(f"📌 Forked to: {self.username}/{repo_name.split('/')[1]}")
            else:
                print(f"{Colors.FAIL}Error: {response.status_code}{Colors.END}")
        except Exception as e:
            print(f"{Colors.FAIL}Error: {e}{Colors.END}")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
    
    def list_issues(self):
        """List issues for a repository"""
        print(f"\n{Colors.CYAN}📦 List Issues{Colors.END}")
        repo_name = input("Enter repository name: ")
        
        try:
            response = self.session.get(f"{self.base_url}/repos/{self.username}/{repo_name}/issues")
            if response.status_code == 200:
                issues = response.json()
                if not issues:
                    print(f"{Colors.WARNING}No issues found.{Colors.END}")
                    return
                
                print(f"\n{Colors.GREEN}Issues for {repo_name}:{Colors.END}")
                print("=" * 60)
                for issue in issues:
                    print(f"{Colors.BOLD}#{issue['number']}{Colors.END}: {issue['title']}")
                    print(f"   Status: {'Open' if issue['state'] == 'open' else 'Closed'}")
                    print(f"   Created: {issue['created_at'][:10]}")
                    print(f"   🔗 {issue['html_url']}")
                    print("-" * 60)
                
                input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
            else:
                print(f"{Colors.FAIL}Error: {response.status_code}{Colors.END}")
        except Exception as e:
            print(f"{Colors.FAIL}Error: {e}{Colors.END}")
    
    def create_issue(self):
        """Create a new issue"""
        print(f"\n{Colors.CYAN}🔄 Create Issue{Colors.END}")
        repo_name = input("Enter repository name: ")
        title = input("Issue title: ")
        body = input("Issue description: ")
        
        data = {
            "title": title,
            "body": body
        }
        
        try:
            response = self.session.post(f"{self.base_url}/repos/{self.username}/{repo_name}/issues", json=data)
            if response.status_code == 201:
                issue = response.json()
                print(f"{Colors.GREEN}✓ Issue created successfully!{Colors.END}")
                print(f"📌 Issue #{issue['number']}: {issue['title']}")
                print(f"🔗 {issue['html_url']}")
            else:
                print(f"{Colors.FAIL}Error: {response.status_code}{Colors.END}")
        except Exception as e:
            print(f"{Colors.FAIL}Error: {e}{Colors.END}")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
    
    def repo_activity(self):
        """Show repository activity"""
        print(f"\n{Colors.CYAN}📈 Repository Activity{Colors.END}")
        repo_name = input("Enter repository name: ")
        
        try:
            # Get commits
            response = self.session.get(f"{self.base_url}/repos/{self.username}/{repo_name}/commits?per_page=10")
            if response.status_code == 200:
                commits = response.json()
                print(f"\n{Colors.GREEN}Recent Activity for {repo_name}:{Colors.END}")
                print("=" * 60)
                for commit in commits:
                    date = commit['commit']['author']['date'][:10]
                    message = commit['commit']['message'][:50]
                    author = commit['commit']['author']['name']
                    print(f"📝 [{date}] {author}: {message}...")
                    print(f"   🔗 {commit['html_url']}")
                    print("-" * 60)
                
                input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
            else:
                print(f"{Colors.FAIL}Error: {response.status_code}{Colors.END}")
        except Exception as e:
            print(f"{Colors.FAIL}Error: {e}{Colors.END}")
    
    def manage_collaborators(self):
        """Manage collaborators for a repository"""
        print(f"\n{Colors.CYAN}🔑 Manage Collaborators{Colors.END}")
        repo_name = input("Enter repository name: ")
        action = input("Add or remove collaborator? (add/remove): ").lower()
        username = input("GitHub username: ")
        
        if action == 'add':
            response = self.session.put(f"{self.base_url}/repos/{self.username}/{repo_name}/collaborators/{username}")
            if response.status_code == 201:
                print(f"{Colors.GREEN}✓ Collaborator added successfully!{Colors.END}")
            elif response.status_code == 204:
                print(f"{Colors.GREEN}✓ Collaborator already exists.{Colors.END}")
            else:
                print(f"{Colors.FAIL}Error: {response.status_code}{Colors.END}")
        elif action == 'remove':
            response = self.session.delete(f"{self.base_url}/repos/{self.username}/{repo_name}/collaborators/{username}")
            if response.status_code == 204:
                print(f"{Colors.GREEN}✓ Collaborator removed successfully!{Colors.END}")
            else:
                print(f"{Colors.FAIL}Error: {response.status_code}{Colors.END}")
        else:
            print(f"{Colors.WARNING}Invalid action.{Colors.END}")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
    
    def upload_file(self):
        """Upload a file to a repository"""
        print(f"\n{Colors.CYAN}📤 Upload File to Repository{Colors.END}")
        repo_name = input("Enter repository name: ")
        file_path = input("Enter local file path: ")
        remote_path = input("Enter remote path (e.g., path/to/file.txt): ")
        commit_message = input("Commit message: ")
        
        if not os.path.exists(file_path):
            print(f"{Colors.FAIL}File not found.{Colors.END}")
            input("Press Enter to continue...")
            return
        
        try:
            with open(file_path, 'rb') as file:
                content = file.read()
            
            # Get file SHA if exists
            sha = None
            try:
                response = self.session.get(f"{self.base_url}/repos/{self.username}/{repo_name}/contents/{remote_path}")
                if response.status_code == 200:
                    sha = response.json()['sha']
            except:
                pass
            
            import base64
            encoded = base64.b64encode(content).decode('utf-8')
            
            data = {
                "message": commit_message,
                "content": encoded,
                "branch": "main"
            }
            if sha:
                data["sha"] = sha
            
            response = self.session.put(f"{self.base_url}/repos/{self.username}/{repo_name}/contents/{remote_path}", json=data)
            if response.status_code in [200, 201]:
                print(f"{Colors.GREEN}✓ File uploaded successfully!{Colors.END}")
                print(f"🔗 {response.json()['content']['html_url']}")
            else:
                print(f"{Colors.FAIL}Error: {response.status_code}{Colors.END}")
        except Exception as e:
            print(f"{Colors.FAIL}Error: {e}{Colors.END}")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
    
    def download_file(self):
        """Download a file from a repository"""
        print(f"\n{Colors.CYAN}📥 Download File from Repository{Colors.END}")
        repo_name = input("Enter repository name: ")
        remote_path = input("Enter remote file path (e.g., path/to/file.txt): ")
        local_path = input("Enter local save path: ")
        
        try:
            response = self.session.get(f"{self.base_url}/repos/{self.username}/{repo_name}/contents/{remote_path}")
            if response.status_code == 200:
                import base64
                content = response.json()['content']
                decoded = base64.b64decode(content)
                
                with open(local_path, 'wb') as f:
                    f.write(decoded)
                
                print(f"{Colors.GREEN}✓ File downloaded successfully to: {local_path}{Colors.END}")
            else:
                print(f"{Colors.FAIL}Error: {response.status_code}{Colors.END}")
        except Exception as e:
            print(f"{Colors.FAIL}Error: {e}{Colors.END}")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
    
    def refresh_token(self):
        """Refresh GitHub token"""
        print(f"\n{Colors.CYAN}🔄 Refresh Token{Colors.END}")
        if self.token:
            print(f"Current token: {self.token[:10]}...")
        
        new_token = getpass.getpass("Enter new GitHub Personal Access Token: ")
        if new_token:
            self.token = new_token
            self.headers = {
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json"
            }
            self.session.headers.update(self.headers)
            self.save_config()
            
            # Verify new token
            try:
                response = self.session.get(f"{self.base_url}/user")
                if response.status_code == 200:
                    data = response.json()
                    self.username = data['login']
                    self.save_config()
                    print(f"{Colors.GREEN}✓ Token refreshed successfully!{Colors.END}")
                else:
                    print(f"{Colors.FAIL}✗ Invalid token.{Colors.END}")
            except Exception as e:
                print(f"{Colors.FAIL}Error: {e}{Colors.END}")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
    
    def check_github_cli(self):
        """Check if GitHub CLI is installed and provide setup instructions"""
        try:
            subprocess.run(['gh', '--version'], capture_output=True, check=True)
            return True
        except:
            return False
    
    def run(self):
        """Main application loop"""
        # Check for GH CLI
        if not self.check_github_cli():
            print(f"{Colors.WARNING}GitHub CLI (gh) not found. Recommended for additional features.{Colors.END}")
            print("Install with: pkg install gh")
            time.sleep(2)
        
        # Display startup animation
        Animation.typing_effect(f"{Colors.CYAN}Starting GitControl...{Colors.END}", 0.05)
        
        # Authentication
        if not self.authenticate():
            print(f"{Colors.FAIL}Authentication failed. Exiting...{Colors.END}")
            sys.exit(1)
        
        # Main loop
        while True:
            choice = self.display_menu()
            
            if choice == '1':
                self.list_repos()
            elif choice == '2':
                self.create_repo()
            elif choice == '3':
                self.delete_repo()
            elif choice == '4':
                self.repo_stats()
            elif choice == '5':
                self.search_repos()
            elif choice == '6':
                self.view_profile()
            elif choice == '7':
                self.star_repo()
            elif choice == '8':
                self.fork_repo()
            elif choice == '9':
                self.list_issues()
            elif choice == '10':
                self.create_issue()
            elif choice == '11':
                self.repo_activity()
            elif choice == '12':
                self.manage_collaborators()
            elif choice == '13':
                self.upload_file()
            elif choice == '14':
                self.download_file()
            elif choice == '15':
                self.refresh_token()
            elif choice == '16':
                print(f"\n{Colors.GREEN}Thank you for using GitControl! Goodbye! 👋{Colors.END}")
                Animation.typing_effect("Exiting...", 0.05)
                sys.exit(0)
            else:
                print(f"{Colors.WARNING}Invalid choice. Please try again.{Colors.END}")
                time.sleep(1)

if __name__ == "__main__":
    try:
        app = GitControl()
        app.run()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Interrupted by user. Exiting...{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print(f"{Colors.FAIL}Fatal error: {e}{Colors.END}")
        sys.exit(1)
