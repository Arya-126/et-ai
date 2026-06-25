#!/usr/bin/env bash
# One-command setup for macOS/Linux/WSL.
#   ./setup.sh            # full bootstrap
#   SKIP_CNN=1 ./setup.sh # skip currency CNN training (features-only)
set -euo pipefail
root="$(cd "$(dirname "$0")" && pwd)"
echo "==> Fraud Shield setup"

# 1. Backend venv + deps
cd "$root/backend"
[ -d .venv ] || python3 -m venv .venv
py=".venv/bin/python"
"$py" -m pip install --quiet --upgrade pip
echo "==> Installing torch (CPU) + backend deps..."
"$py" -m pip install --quiet torch==2.12.1 torchvision==0.27.1 --index-url https://download.pytorch.org/whl/cpu
"$py" -m pip install --quiet -r requirements.txt
[ -f .env ] || cp ../.env.example .env

# 2. Data + currency model
echo "==> Generating synthetic data..."
"$py" -m data.generate
if [ "${SKIP_CNN:-0}" != "1" ]; then
  echo "==> Training currency CNN (~2 min)..."
  "$py" -m cv.generate_notes
  "$py" -m cv.train
fi

# 3. Build the unified platform
echo "==> Building the platform UI..."
cd "$root/platform"
npm install
npm run build

cd "$root"
echo
echo "==> Done. Start the platform:"
echo "    cd backend && . .venv/bin/activate && uvicorn app.main:app --port 8000"
echo "    open http://localhost:8000"
