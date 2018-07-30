
from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()

setup(name='ota-suit-test-server',
      version='0.1.1',
      description=' Test server to allow configuring and sending OTA updates and collecting diagnostics.',
      long_description=readme(),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'Intended Audience :: Telecommunications Industry',
        'Intended Audience :: Information Technology',
        'Framework :: AsyncIO',
        'Topic :: System :: Software Distribution'
      ],
      keywords='ota suit coap http',
      url='https://github.com/riot-appstore/ota-suit-test-server',
      author='Koen Zandberg <koen@bergzand.net>',
      author_email='koen@bergzand.net',
      license='MIT',
      packages=['ota_suit_server'],
      entry_points={
          'console_scripts': [
              'ota-suit-server = ota_suit_server.__main__:main'
          ]
      },
      install_requires=[
        'aiocoap',
        'aiohttp',
        'aiohttp-jinja2',
        'async-timeout',
        'attrs',
        'chardet',
        'idna',
        'idna-ssl',
        'Jinja2',
        'LinkHeader',
        'MarkupSafe',
        'multidict',
        'yarl',
        'cbor',
        'ed25519',
        'pyasn1'
      ],
      include_package_data=True,
      zip_safe=True
)


