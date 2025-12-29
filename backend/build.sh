#!/bin/bash
set -e

echo "🚀 Starting build process..."

# Set writable directories for Rust/Cargo (fixes read-only filesystem error)
export CARGO_HOME=/tmp/cargo
export RUSTUP_HOME=/tmp/rustup
export PATH="$CARGO_HOME/bin:$PATH"

echo "✅ Set Rust/Cargo environment variables"

# Upgrade pip and install build tools
echo "📦 Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel

# Install numpy first (required by many ML packages)
echo "📦 Installing numpy..."
pip install numpy

# Install all other dependencies
echo "📦 Installing project dependencies..."
pip install --no-cache-dir -r requirements.txt

echo "✅ Build completed successfully!"

