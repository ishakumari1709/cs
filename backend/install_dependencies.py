#!/usr/bin/env python3
"""
Install dependencies with proper handling for Python 3.13 compatibility
"""
import subprocess
import sys

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✓ Installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install {package}: {e}")
        return False

def main():
    print("Installing dependencies for Python 3.13...")
    print("=" * 50)
    
    # Core dependencies (should work fine)
    core_packages = [
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "python-multipart==0.0.6",
        "sqlalchemy==2.0.23",
        "pydantic==2.5.0",
        "python-dotenv==1.0.0",
    ]
    
    # LangChain
    langchain_packages = [
        "langchain==0.1.0",
        "langchain-community==0.0.10",
    ]
    
    # Vector Database
    vector_packages = [
        "chromadb==0.4.18",
    ]
    
    # Embeddings
    embedding_packages = [
        "sentence-transformers==2.2.2",
    ]
    
    # Document Processing
    doc_packages = [
        "PyPDF2==3.0.1",
        "python-docx==1.1.0",
        "pypdf==3.17.1",
    ]
    
    # Image Processing (already fixed)
    image_packages = [
        "Pillow>=10.2.0",
    ]
    
    # ML/AI - Install numpy first with pre-built wheel
    print("\n1. Installing NumPy (pre-built wheel)...")
    install_package("numpy")
    
    # Then install other ML packages
    ml_packages = [
        "transformers",
        "torch",
        "accelerate==0.25.0",
        "huggingface-hub==0.19.4",
    ]
    
    # OCR (optional)
    ocr_packages = [
        "pytesseract==0.3.10",
        # "easyocr==1.7.0",  # Commented out as it's large and optional
    ]
    
    print("\n2. Installing core dependencies...")
    for package in core_packages:
        install_package(package)
    
    print("\n3. Installing LangChain...")
    for package in langchain_packages:
        install_package(package)
    
    print("\n4. Installing vector database...")
    for package in vector_packages:
        install_package(package)
    
    print("\n5. Installing embeddings...")
    for package in embedding_packages:
        install_package(package)
    
    print("\n6. Installing document processing...")
    for package in doc_packages:
        install_package(package)
    
    print("\n7. Installing image processing...")
    for package in image_packages:
        install_package(package)
    
    print("\n8. Installing ML/AI packages...")
    for package in ml_packages:
        install_package(package)
    
    print("\n9. Installing OCR packages (optional)...")
    for package in ocr_packages:
        install_package(package)
    
    print("\n" + "=" * 50)
    print("Installation complete!")
    print("\nNote: If some packages failed, they may not be critical.")
    print("Try running: python start.py")

if __name__ == "__main__":
    main()

