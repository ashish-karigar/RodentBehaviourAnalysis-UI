#!/bin/bash

set -e

echo "Building RodentBehaviourAnalysis UI for macOS..."

cd "$(dirname "$0")/.."

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate RBA-UI

pip install -r requirements.txt
pip install pyinstaller

echo "Cleaning previous builds..."

if [ -d "build" ]; then
  chmod -R u+w build || true
  rm -rf build
fi

if [ -d "dist" ]; then
  chmod -R u+w dist || true
  rm -rf dist
fi

rm -f *.spec
rm -rf __pycache__
find . -type d -name "__pycache__" -prune -exec rm -rf {} +

pyinstaller --noconfirm --clean build-scripts/rba_ui_mac.spec

echo ""
echo "Build complete."
echo "App created at:"
echo "dist/RodentBehaviourAnalysisUI.app"
echo ""
echo "Run:"
echo "open dist/RodentBehaviourAnalysisUI.app"