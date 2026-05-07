files(
    name="mesh_assets",
    sources=[
        "test_mesh_object/taper.stl",
    ],
)

python_tests(
    name="tests",
    sources=["test_*.py"],
    dependencies=[
        "src/python/arcor2_ur/data/urdf:urdf",
        "src/python/arcor2_ur/data:moveit_yaml",
        ":mesh_assets",
    ],
    runtime_package_dependencies=[
        "src/python/arcor2_ur/scripts:ur",
        "src/python/arcor2_ur/scripts:robot_publisher",
        "src/python/arcor2_storage/scripts:storage",
    ],
)

python_test_utils(
    name="test_utils",
    sources=["conftest.py"],
)