from setuptools import setup

package_name = 'depth_image_processor'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    py_modules=[],
    data_files=[
        ('share/ament_index/resource_index/packages',
         ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='your_email@example.com',
    description='Pacote para processar imagens de profundidade',
    license='Apache License 2.0',
    entry_points={
        'console_scripts': [
            'depth_image_node = depth_image_processor.depth_image_node:main',
        ],
    },
)
