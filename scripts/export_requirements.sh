#!/bin/bash
# Export minimal requirements for HF Spaces
# Only includes runtime dependencies needed for app.py
cat > requirements.txt << 'EOF'
# Minimal requirements for HF Spaces deployment
# Only the dependencies needed for app.py
gradio>=5.9.0
huggingface-hub>=0.27.0
joblib>=1.4.0
EOF
echo "✅ requirements.txt generated for HF Spaces"
