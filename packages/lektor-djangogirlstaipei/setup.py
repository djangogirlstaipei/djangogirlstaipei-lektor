from setuptools import find_packages, setup

setup(
    name='lektor-djangogirlstaipei',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'markupsafe',
        'mistune',
        'pygments',
        'six',
        'slugify',
    ],
    entry_points={
        'lektor.plugins': [
            'djangogirlstaipei = lektor_djangogirlstaipei:Plugin',
        ],
    },
    zip_safe=False,
)
