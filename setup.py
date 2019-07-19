import os

from setuptools import find_packages, setup


setup(name='pwned-passwords-django',
      zip_safe=False,  # eggs are the devil.
      version='1.3.2',
      description='A Pwned Passwords implementation for Django sites.',
      long_description=open(
          os.path.join(
              os.path.dirname(__file__),
              'README.rst'
          )
      ).read(),
      author='James Bennett',
      author_email='james@b-list.org',
      url='https://github.com/ubernostrum/pwned-passwords-django/',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Framework :: Django :: 1.11',
                   'Framework :: Django :: 2.0',
                   'Framework :: Django :: 2.1',
                   'Framework :: Django :: 2.2',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.4',
                   'Programming Language :: Python :: 3.5',
                   'Programming Language :: Python :: 3.6',
                   'Programming Language :: Python :: 3.7',
                   'Programming Language :: Python :: 3 :: Only',
                   'Topic :: Utilities'],
      python_requires=">=3.4",
      install_requires=[
          'Django>=1.11,<3.0',
          'requests',
      ],
)
