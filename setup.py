from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="agentguard",
    version="0.1.0",
    author="Your Name",
    author_email="you@example.com",
    description="Agentic AI Threat Modeling Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/agentguard",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "agentguard": ["../models/**/*.yaml", "../templates/*.j2"],
    },
    install_requires=[
        "click>=8.1.0",
        "pyyaml>=6.0",
        "jinja2>=3.1.0",
        "rich>=13.0.0",
        "pydantic>=2.0.0",
        "jsonschema>=4.17.0",
        "weasyprint>=59.0",   # PDF export
    ],
    entry_points={
        "console_scripts": [
            "agentguard=agentguard.cli:main",
        ],
    },
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="ai security threat-modeling llm agents grc compliance mitre-atlas",
)
```

---

## 📁 `requirements.txt`
```
click>=8.1.0
pyyaml>=6.0
jinja2>=3.1.0
rich>=13.0.0
pydantic>=2.0.0
jsonschema>=4.17.0
weasyprint>=59.0
pytest>=7.4.0
pytest-cov>=4.1.0
```

---

## 📁 `.gitignore`
```
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
.venv/
venv/
*.html           # generated reports
*.pdf            # generated reports
.env
.DS_Store
