from setuptools import setup, find_packages

setup(
    name="employee_events",
    version="1.0.0",
    packages=find_packages(),
    package_data={"employee_events": ["*.db"]},
    install_requires=["pandas"],
    python_requires=">=3.10",
)