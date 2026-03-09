.PHONY: setup reproduce clean demo test

# Setup environment
setup:
	pip install -r requirements.txt
	mkdir -p data/raw data/processed data/sample

# Run full reproduction pipeline
reproduce: setup
	python src/preprocessing.py
	python src/analysis.py
	@echo "Analysis complete! Run 'make demo' to launch dashboard."

# Launch Streamlit dashboard
demo:
	streamlit run demo/app.py

# Run on sample data (for quick testing)
sample:
	python src/preprocessing.py --sample
	streamlit run demo/app.py

# Clean generated files
clean:
	rm -rf data/processed/*
	rm -rf __pycache__
	rm -rf .ipynb_checkpoints

# Run tests
test:
	python -m pytest tests/ -v

# Download data instructions
data:
	@echo "Download the dataset from:"
	@echo "   https://archive.ics.uci.edu/dataset/502/online+retail+ii"
	@echo ""
	@echo "   Place the file 'online_retail_II.xlsx' in data/raw/"
