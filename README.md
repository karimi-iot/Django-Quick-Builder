# Django Quick Builder

## Overview
Django Quick Builder is a command-line utility designed to rapidly spin up a new Django or Django REST Framework project. It automatically handles virtual environment creation, required package installation, and initial project settings.

## Why This Project?
Manually setting up each new Django project was time-consuming. This script streamlines project creation, helping you get started faster by automating:
- Virtual environment setup
- Installing Django, python-dotenv, and optionally Django REST Framework + JWT
- Initial project scaffolding
- Environment variable handling and settings configuration

## Requirements
- Python 3.x

## How to Use
1. Clone or download this repository.
2. Open a terminal in the project directory.  
3. Run the script and follow the prompts.  
   Example:  python django-maker.py MyNewProject
4. Select the type of project you want:
- (1) Standard Django project  
- (2) Django REST Framework project  

Once it's done, you’ll have a fully functional Django project with environment variables, .gitignore, and optional DRF + JWT support.

## Contributions
If you spot any issues or have enhancements, you’re welcome to open a pull request or submit an issue. Any contributions are appreciated.