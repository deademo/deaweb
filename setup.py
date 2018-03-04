from setuptools import setup, find_packages
import sdist_upip


setup(
    name='deaweb',
    version='1.0.3',
    descrition='Lightweight asynchronous web-framework for Micropython',
    url='https://github.com/deademo/deaweb',
    author='Dmitry Khylia',
    # classifiers=[
    #     'Development Status :: 2 - Beta',
    #     'Intended Audience :: Developers',
    #     'Topic :: Software Development :: Build Tools',
    #     'License :: OSI Approved :: MIT License',
    # ],
    keywords='micropython web framework webframework web-framework server',
    packages=['deaweb'],
    cmdclass={'sdist': sdist_upip.sdist},
    # install_requires=['micropython-uasyncio'], # package has not setup script
    # project_urls={
    #     'Source': 'https://github.com/deademo/deaweb',
    # }
)
