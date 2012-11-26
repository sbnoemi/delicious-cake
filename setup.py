try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup


def README():
    with open('README.rst', 'r') as readme:
        return readme.read()


setup(
    name='delicious-cake',
    version='0.0.0',
    description='A flexible & capable API layer for Django.',
    author='Mike Urbanski',
    author_email='mike@theitemshoppe.com',
    url='http://github.com/mcu/django-delicious-cake/',
    long_description=README(),
    packages=[
        'delicious_cake',
        'delicious_cake.utils',
        'delicious_cake.management',
        'delicious_cake.management.commands'],
    package_data={},
    zip_safe=False,
    requires=[
        'mimeparse',
        'dateutil(>=1.5, !=2.0)'],
    install_requires=[
        'mimeparse',
        'python_dateutil>=1.5, !=2.0'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'],)