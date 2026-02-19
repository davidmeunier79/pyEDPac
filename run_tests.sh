#!/bin/bash

# Script pour lancer tous les tests

echo "=========================================="
echo "Running EDPac Python Test Suite"
echo "=========================================="

# Créer environnement venv si nécessaire
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activer venv
source venv/bin/activate

# Installer les dépendances
echo "Installing dependencies..."
pip install -q pytest pytest-cov numpy scipy matplotlib pandas

# Lancer les tests
echo ""
echo "Running tests..."
pytest tests/ -v --tb=short

# Générer coverage report
echo ""
echo "Generating coverage report..."
pytest tests/ --cov=src/edpac --cov-report=html --cov-report=term-missing

echo ""
echo "=========================================="
echo "Test suite completed!"
echo "=========================================="