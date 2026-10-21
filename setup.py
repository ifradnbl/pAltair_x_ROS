from setuptools import find_packages, setup
from glob import glob
package_name = 'altair_phase3'
setup(
    name=package_name, version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.py')),
    ],
    install_requires=['setuptools'], zip_safe=True,
    maintainer='Ifrad Nabil', maintainer_email='you@example.com',
    description='Altair Phase 3', license='MIT',
    entry_points={'console_scripts': [
        'telemetry_pub = altair_phase3.telemetry_pub:main',
        'monitor = altair_phase3.monitor:main',
        'turtle_menu = altair_phase3.turtle_menu:main',
        'mission = altair_phase3.mission:main',
    ]},
)
