1. Installing python packages offline:

mkdir pip_packages
cd pip_packages

pip wheel requests -w .

cd path/to/pip_packages
pip install * -f ./ --no-index
python -c "import requests; print(requests.__version__)"

============================================================================
