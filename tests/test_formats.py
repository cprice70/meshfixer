from pathlib import Path
import pytest
import pymeshlab
from meshfixer.formats import load_mesh, save_mesh, UnsupportedFormatError

FIXTURES = Path(__file__).parent / "fixtures"


def test_load_stl_returns_meshset():
    ms = load_mesh(FIXTURES / "broken_tetrahedron.stl")
    assert isinstance(ms, pymeshlab.MeshSet)
    assert ms.current_mesh().face_number() == 3


def test_load_nonexistent_raises():
    with pytest.raises(FileNotFoundError):
        load_mesh(Path("nonexistent.stl"))


def test_load_unsupported_extension_raises(tmp_path):
    f = tmp_path / "model.obj"
    f.write_text("v 0 0 0\n")
    with pytest.raises(UnsupportedFormatError):
        load_mesh(f)


def test_save_stl_roundtrip(tmp_path):
    ms = load_mesh(FIXTURES / "broken_tetrahedron.stl")
    out = tmp_path / "out.stl"
    save_mesh(ms, out)
    assert out.exists()
    ms2 = load_mesh(out)
    assert ms2.current_mesh().face_number() == 3


def test_save_unsupported_extension_raises(tmp_path):
    ms = load_mesh(FIXTURES / "broken_tetrahedron.stl")
    with pytest.raises(UnsupportedFormatError):
        save_mesh(ms, tmp_path / "out.obj")
