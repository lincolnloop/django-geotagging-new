from setuptools import setup, find_packages

setup(
    name='django-geotagging-new',
    version='0.0.2',
    description='This is a geotagging application. It can be used to localize your content.',
    author='Nicolas Lara',
    author_email='nicolaslara@gmail.com',
    url='https://github.com/lincolnloop/django-geotagging-new',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    include_package_data=True,
    zip_safe=False,
)
