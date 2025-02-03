#!/usr/bin/env python3
import os
import secrets
import sys
import subprocess
import argparse
import re


def get_random_secret_key():
    """
    Return a 50 character random string usable as a SECRET_KEY setting value.
    """
    chars = "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"
    return "".join(secrets.choice(chars) for i in range(50))


def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created directory: {path}")
    else:
        print(f"Directory {path} already exists.")


def create_virtualenv(project_dir):
    venv_path = os.path.join(project_dir, "venv")
    subprocess.check_call([sys.executable, "-m", "venv", venv_path])
    print("Virtual environment created at", venv_path)


def get_venv_python(project_dir):
    # Adjust the path based on OS (Windows vs Unix)
    if os.name == "nt":
        # Windows
        return os.path.join(project_dir, "venv", "Scripts", "python.exe")
    else:
        return os.path.join(project_dir, "venv", "bin", "python")


def install_packages(venv_python, type_project):
    if type_project == 1:
        subprocess.check_call(
            [venv_python, "-m", "pip", "install", "django", "python-dotenv"]
        )
        print("Installed Django and python-dotenv in the virtual environment.")

    elif type_project == 2:
        subprocess.check_call(
            [
                venv_python,
                "-m",
                "pip",
                "install",
                "django",
                "python-dotenv",
                "djangorestframework",
                "djangorestframework-simplejwt",
            ]
        )
        print(
            "Installed Django, python-dotenv , Django Rest Framework and Simple JWT in the virtual environment."
        )


def create_env_file(project_dir):
    env_file = os.path.join(project_dir, ".env")
    if not os.path.exists(env_file):
        with open(env_file, "w") as f:
            SECRET_KEY = get_random_secret_key()
            # set the SECRET_KEY, ALLOWED_HOSTS, and DEBUG environment variables
            f.write(f"SECRET_KEY={SECRET_KEY}\n")
            f.write("ALLOWED_HOSTS=localhost,127.0.0.1\n")
            f.write("DEBUG=True\n")

        print("Created .env file for environment variables.")
    else:
        print(".env file already exists.")


def create_gitignore(project_dir):
    gitignore_file = os.path.join(project_dir, ".gitignore")
    if not os.path.exists(gitignore_file):
        with open(gitignore_file, "w") as f:
            # Typical files/folders to ignore for a Django project.
            f.write("venv/\n")
            f.write("__pycache__/\n")
            f.write("*.pyc\n")
            f.write(".env\n")
            f.write("db.sqlite3\n")
        print("Created .gitignore file.")
    else:
        print(".gitignore file already exists.")


def start_django_project(project_dir, project_name, venv_python):
    # Use the virtual environment's Python to run Django's startproject.
    # Using '.' as destination creates the project files in the project_dir.
    subprocess.check_call(
        [venv_python, "-m", "django", "startproject", "config", "."],
        cwd=project_dir,
    )
    print(f"Django project '{project_name}' created in {project_dir}")


def update_settings_file(project_dir, project_name, type_project , account_use):
    """
    Updates the settings.py file so that the SECRET_KEY is read from the .env file.
    Inserts the necessary python-dotenv imports and calls at the top.
    """
    settings_path = os.path.join(project_dir, "config", "settings.py")
    try:
        with open(settings_path, "r") as f:
            content = f.read()
    except FileNotFoundError:
        print("Could not find settings.py at", settings_path)
        return

    # Prepend dotenv import and load_dotenv() if not already present.
    if "load_dotenv()" not in content:
        # Find the first line that isn't a shebang or encoding declaration.
        lines = content.splitlines()
        insert_at = 0
        for i, line in enumerate(lines):
            if line.startswith("#!") or line.startswith("# -*-"):
                continue
            else:
                insert_at = i
                break
        dotenv_lines = [
            "import os",
            "from dotenv import load_dotenv",
            "load_dotenv()",
            "",
        ]
        lines = lines[:insert_at] + dotenv_lines + lines[insert_at:]
        content = "\n".join(lines)

    # Replace SECRET_KEY, ALLOWED_HOSTS, and DEBUG assignments in settings.py.
    content, secret_count = re.subn(
        r"SECRET_KEY = .*\n",
        'SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key")\n',
        content,
        flags=re.MULTILINE,
    )
    content, hosts_count = re.subn(
        r"ALLOWED_HOSTS = .*\n",
        'ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")\n',
        content,
        flags=re.MULTILINE,
    )
    content, debug_count = re.subn(
        r"DEBUG = .*\n",
        "DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'\n",
        content,
        flags=re.MULTILINE,
    )

    if secret_count and hosts_count and debug_count:
        print("Updated SECRET_KEY, ALLOWED_HOSTS, and DEBUG in settings.py.")
    else:
        print(
            "One or more of SECRET_KEY, ALLOWED_HOSTS, or DEBUG not found in settings.py. No changes made."
        )

    # Add the DRF settings if the project is a DRF project
    if type_project == 2:
        if account_use :
            content, drf_count = re.subn(
            r"INSTALLED_APPS = \[",
            "INSTALLED_APPS = [\n  #3rd party apps \n  'rest_framework',\n    'rest_framework_simplejwt',\n\t#local apps\n\t'account.apps.AccountConfig'\n    # main apps \n    ",
            content,
            flags=re.MULTILINE,
            )
        else :    
            content, drf_count = re.subn(
                r"INSTALLED_APPS = \[",
                "INSTALLED_APPS = [\n  #3rd party apps \n  'rest_framework',\n    'rest_framework_simplejwt',\n    # main apps \n    ",
                content,
                flags=re.MULTILINE,
            )
        # set the jwt as the main authentication class in the settings.py
        if "REST_FRAMEWORK" not in content:
            content += "\n\n #add the jwt as the default authentication class \nREST_FRAMEWORK = {\n    'DEFAULT_AUTHENTICATION_CLASSES': [\n        'rest_framework_simplejwt.authentication.JWTAuthentication',\n    ],\n}\n"
            jwt_count = 1
        else:
            content, jwt_count = re.subn(
                r"REST_FRAMEWORK = {",
                "REST_FRAMEWORK = {\n    'DEFAULT_AUTHENTICATION_CLASSES': [\n        'rest_framework_simplejwt.authentication.JWTAuthentication',\n],",
                content,
                flags=re.MULTILINE,
            )
        
        if account_use:
            content += "\n\n# set default auth\nAUTH_USER_MODEL = 'account.User'"

        if drf_count and jwt_count:
            print("Added DRF settings to settings.py.")
            print("Added JWT as the main authentication class in settings.py.")
        else:
            print("Could not add DRF or JWT settings to settings.py. No changes made.")

    with open(settings_path, "w") as f:
        f.write(content)
    print("settings.py has been updated.")

def make_user_app(project_dir,venv_python,type_project):
    # make the project
    subprocess.check_call([venv_python,"-m","django","startapp","account"],cwd=project_dir)
    print("Created 'account' app in the project.")
    # add the model
    model_file = os.path.join(project_dir,"account","models.py")
    with open(model_file,mode="w") as f:
        f.write("from django.db import models\n")
        f.write("from django.contrib.auth.models import AbstractUser\n")
        f.write("class User(AbstractUser): \n\tpass \n")
    print("set the simple 'User' in models of 'account' app.")
    # add the urls for the jwt or empty for not jwt
    urls_file = os.path.join(project_dir,"account","urls.py")
    if type_project==2:
        with open(urls_file,mode="w") as f:
            f.write("from django.urls import path\nfrom rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView\n\nurlpatterns = [\n\t# JWT authentication URLs  - Token ObtainPairView and TokenRefreshView  are provided by DRF-SimpleJWT library.  They generate JWT tokens for authenticated users.  The JWT tokens are then used for subsequent API requests.  The JWT token is passed in the Authorization header with the value 'Bearer <token>' where <token> is the JWT token.\n\tpath('token/', TokenObtainPairView.as_view(), name='login'),\n\tpath('token/refresh/', TokenRefreshView.as_view(), name='login_refresh'),\n\t]\n")
    else:
        with open(urls_file,mode="w") as f:
            f.write("")
    print("set the urls.py file for 'account'.")
    # set the account data
    config_urls_file = os.path.join(project_dir,"config","urls.py")
    with open(config_urls_file,"r") as f:
        content = f.read()
    
    content , urls_content = re.subn(
        r"from django.urls import path",
        "from django.urls import path , include\n",
        content,
        flags=re.MULTILINE
    )
    content, urls_content = re.subn(
    r"path\s*\(\s*'admin/'\s*,\s*admin\.site\.urls\s*\),",
    "path('admin/', admin.site.urls),\n    path('api/account/', include('account.urls')),",
    content,
    flags=re.MULTILINE
    )
    with open(config_urls_file,"w") as f:
        f.write(content)
    if urls_content :
        print("urls of account is set to api/account/ .")
    else :
        print("failed to set the urls for account.")




def main():
    type_project = int(
        input(
            "Select the type of project 1 for Django or 2 for Django Rest Framework: "
        )
    )
    account_use = "y" == input("Do you need account management(having custom user)? 'y' for yes and anything else for no : ")
    parser = argparse.ArgumentParser(description="Simple Django Project Maker")
    parser.add_argument("project_name", help="Name for your new Django project")
    args = parser.parse_args()
    project_dir = os.path.abspath(args.project_name)
    print("Creating a Django project")
    create_directory(project_dir)
    create_virtualenv(project_dir)
    venv_python = get_venv_python(project_dir)
    install_packages(venv_python, type_project)
    create_env_file(project_dir)
    create_gitignore(project_dir)
    start_django_project(project_dir, args.project_name, venv_python)
    if account_use:
        make_user_app(project_dir,venv_python,type_project)
    update_settings_file(project_dir, args.project_name, type_project,account_use)


if __name__ == "__main__":
    main()
