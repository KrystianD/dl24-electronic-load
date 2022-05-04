from setuptools import setup

setup(
        name='dl24',
        version='1.0',
        description='DL24 connector',
        author='Krystian Dużyński',
        author_email='krystian.duzynski@gmail.com',
        license='MIT',
        packages=[
            "dl24",
            "dl24.tools.manage",
            "dl24.tools.monitor",
            "dl24.tools.plotter",
        ],
        install_requires=[
            'pyserial>=3.5',
            'matplotlib>=3.1.1',
        ],
        entry_points={
            'console_scripts': [
                'dl24-manage = dl24.tools.manage.__main__:main',
                'dl24-monitor = dl24.tools.monitor.__main__:main',
                'dl24-plotter = dl24.tools.plotter.__main__:main',
            ],
        },
)
