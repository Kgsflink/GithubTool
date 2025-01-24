# This script is created by Kgsflink
# GitHub Profile: https://github.com/Kgsflink
# Instagram: @gopalsahani666
import os
import requests
import base64
import json
import argparse

def show_banner():
    banner = """
    ===========================================
               GITHUB UPLOAD TOOL
          Professional Automation Script
    ===========================================
    """
    print(banner)

def save_token(token):
    with open('config.json', 'w') as config_file:
        json.dump({'github_token': token}, config_file)

def load_token():
    try:
        if os.path.exists('config.json'):
            with open('config.json', 'r') as config_file:
                config = json.load(config_file)
                return config.get('github_token', None)
    except (json.JSONDecodeError, KeyError):
        print("Error reading token from config.json. Resetting the file.")
        save_token("")
    return None

def get_github_username(api_key):
    try:
        url = 'https://api.github.com/user'
        headers = {'Authorization': f'token {api_key}'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get('login', None)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching GitHub username: {e}")
        return None

def check_repo_exists(repo_name, api_key):
    try:
        username = get_github_username(api_key)
        url = f'https://api.github.com/repos/{username}/{repo_name}'
        headers = {'Authorization': f'token {api_key}'}
        response = requests.get(url, headers=headers)
        return response.status_code != 404
    except requests.exceptions.RequestException as e:
        print(f"Error checking repository existence: {e}")
        return False

def create_github_repo(repo_name, api_key, private):
    try:
        url = 'https://api.github.com/user/repos'
        headers = {'Authorization': f'token {api_key}'}
        data = {'name': repo_name, 'private': private}
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 201:
            print(f"Repository '{repo_name}' created successfully.")
            return response.json().get('full_name')
        else:
            print(f"Failed to create repository: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"Error creating repository: {e}")
    return None

def delete_github_repo(repo_full_name, api_key):
    try:
        url = f'https://api.github.com/repos/{repo_full_name}'
        headers = {'Authorization': f'token {api_key}'}
        response = requests.delete(url, headers=headers)
        if response.status_code == 204:
            print(f"Repository '{repo_full_name}' deleted successfully.")
            return True
        else:
            print(f"Failed to delete repository: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"Error deleting repository: {e}")
    return False

def get_file_sha(repo_full_name, file_path, api_key):
    try:
        url = f'https://api.github.com/repos/{repo_full_name}/contents/{file_path}'
        headers = {'Authorization': f'token {api_key}'}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get('sha'), base64.b64decode(response.json().get('content'))
    except requests.exceptions.RequestException as e:
        print(f"Error fetching file SHA: {e}")
    return None, None

def upload_files_to_repo(repo_full_name, local_directory, api_key, ignore_list):
    url_template = f'https://api.github.com/repos/{repo_full_name}/contents/{{path}}'
    headers = {'Authorization': f'token {api_key}'}

    for root, dirs, files in os.walk(local_directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            relative_path = os.path.relpath(file_path, local_directory).replace('\\', '/')

            if any(ignored in relative_path for ignored in ignore_list):
                print(f"Skipping ignored file: {relative_path}")
                continue

            try:
                print(f"Processing file: {relative_path}")
                sha, remote_content = get_file_sha(repo_full_name, relative_path, api_key)

                with open(file_path, 'rb') as file:
                    content = base64.b64encode(file.read()).decode('utf-8')

                if remote_content and remote_content == base64.b64decode(content):
                    print(f"No changes in {relative_path}. Skipping.")
                    continue

                url = url_template.format(path=relative_path)
                data = {'message': f"Upload {relative_path}", 'content': content, 'branch': 'main'}
                if sha:
                    data['sha'] = sha

                response = requests.put(url, json=data, headers=headers)
                if response.status_code in [200, 201]:
                    print(f"Successfully uploaded {relative_path}")
                else:
                    print(f"Failed to upload {relative_path}: {response.json()}")

            except Exception as e:
                print(f"Error processing {file_path}: {e}")

def main():
    show_banner()
    parser = argparse.ArgumentParser(description="GitHub repo automation script.")
    parser.add_argument('-p', '--path', type=str, help="Path to the local directory to upload.")
    parser.add_argument('-A', '--api', type=str, help="GitHub API token to save.")
    parser.add_argument('-I', '--ignore', type=str, nargs='*', help="Files or folders to ignore.")
    parser.add_argument('--private', action='store_true', help="Create the repository as private.")
    parser.add_argument('--delete', action='store_true', help="Delete the specified repository.")
    args = parser.parse_args()

    if args.api:
        save_token(args.api)
        print("GitHub API token has been saved successfully!")

    api_key = load_token()
    if not api_key:
        print("GitHub API token is required. Please set it using -A flag.")
        return

    if args.delete:
        repo_name = input("Enter the name of the repository to delete: ").strip()
        if not repo_name:
            print("Repository name is required.")
            return
        username = get_github_username(api_key)
        if username and delete_github_repo(f"{username}/{repo_name}", api_key):
            print(f"Repository '{repo_name}' deleted successfully.")
        return

    if not args.path:
        print("Path to the local directory is required. Use -p to specify the path.")
        return

    repo_name = input("Enter the name of the repository to create or upload to: ").strip()
    if not repo_name:
        print("Repository name is required.")
        return

    visibility = input("Do you want the repository to be private? (yes/no): ").strip().lower()
    if visibility not in ["yes", "no"]:
        print("Invalid input. Please enter 'yes' or 'no'.")
        return

    private = visibility == "yes"
    local_directory = args.path
    if not os.path.exists(local_directory):
        print("Invalid path provided.")
        return

    ignore_list = args.ignore if args.ignore else []

    if check_repo_exists(repo_name, api_key):
        username = get_github_username(api_key)
        repo_full_name = f"{username}/{repo_name}"
        print(f"Repository '{repo_name}' already exists.")
    else:
        repo_full_name = create_github_repo(repo_name, api_key, private)
        if not repo_full_name:
            print("Failed to create the repository. Exiting script.")
            return

    action = input("Do you want to upload files to the repository or delete it? (upload/delete): ").strip().lower()
    if action == "upload":
        upload_files_to_repo(repo_full_name, local_directory, api_key, ignore_list)
    elif action == "delete":
        confirm = input(f"Are you sure you want to delete the repository '{repo_name}'? This action is irreversible! (yes/no): ").strip().lower()
        if confirm == "yes":
            if delete_github_repo(repo_full_name, api_key):
                print(f"Repository '{repo_name}' deleted successfully.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScript interrupted by user. Exiting...")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
