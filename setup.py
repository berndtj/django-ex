import os
from setuptools import find_packages, setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-ex',
    version='0.1.0',
    packages=find_packages(),
    py_modules=['manage', 'wsgi'],
    package_data={
        'welcome': ['templates/*.html', 'templates/**/*.html']
    },
    include_package_data=True,
    license='BSD License',  # example license
    description='A simple Django app to conduct Web-based polls.',
    author='Berndt Jung',
    author_email='bjung@vmware.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',  # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
