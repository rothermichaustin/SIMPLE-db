import pytest
from astropy.table import Table
from astrodb_utils.utils import (
    AstroDBError,
)
from simple.utils.spectral_types import (
    convert_spt_string_to_code,
    convert_spt_code_to_string,
    ingest_spectral_type,
)
from simple.utils.companions import ingest_companion_relationships


# Create fake astropy Table of data to load
@pytest.fixture(scope="module")
def t_plx():
    t_plx = Table(
        [
            {"source": "Fake 1", "plx": 113.0, "plx_err": 0.3, "plx_ref": "Ref 1"},
            {"source": "Fake 2", "plx": 145.0, "plx_err": 0.5, "plx_ref": "Ref 1"},
            {"source": "Fake 3", "plx": 155.0, "plx_err": 0.6, "plx_ref": "Ref 2"},
        ]
    )
    return t_plx


# Create fake astropy Table of data to load
@pytest.fixture(scope="module")
def t_pm():
    t_pm = Table(
        [
            {
                "source": "Fake 1",
                "mu_ra": 113.0,
                "mu_ra_err": 0.3,
                "mu_dec": 113.0,
                "mu_dec_err": 0.3,
                "reference": "Ref 1",
            },
            {
                "source": "Fake 2",
                "mu_ra": 145.0,
                "mu_ra_err": 0.5,
                "mu_dec": 113.0,
                "mu_dec_err": 0.3,
                "reference": "Ref 1",
            },
            {
                "source": "Fake 3",
                "mu_ra": 55.0,
                "mu_ra_err": 0.23,
                "mu_dec": 113.0,
                "mu_dec_err": 0.3,
                "reference": "Ref 2",
            },
        ]
    )
    return t_pm


def test_convert_spt_string_to_code():
    # Test conversion of spectral types into numeric values
    assert convert_spt_string_to_code("M5.6") == 65.6
    assert convert_spt_string_to_code("T0.1") == 80.1
    assert convert_spt_string_to_code("Y2pec") == 92


def test_convert_spt_code_to_string():
    # Test conversion of spectral types into numeric values
    assert convert_spt_code_to_string(65.6) == "M5.6"
    assert convert_spt_code_to_string(80.1) == "T0.1"
    assert convert_spt_code_to_string(92, decimals=0) == "Y2"


def test_ingest_spectral_type(temp_db):
    spt_data1 = {
        "source": "Fake 1",
        "spectral_type": "M5.6",
        "regime": "nir",
        "reference": "Ref 1",
    }
    spt_data2 = {
        "source": "Fake 2",
        "spectral_type": "T0.1",
        "regime": "nir",
        "reference": "Ref 1",
    }
    spt_data3 = {
        "source": "Fake 3",
        "spectral_type": "Y2pec",
        "regime": "nir",
        "reference": "Ref 2",
    }
    for spt_data in [spt_data1, spt_data2, spt_data3]:
        ingest_spectral_type(
            temp_db,
            source=spt_data["source"],
            spectral_type_string=spt_data["spectral_type"],
            reference=spt_data["reference"],
            regime=spt_data["regime"],
        )

    assert (
        temp_db.query(temp_db.SpectralTypes)
        .filter(temp_db.SpectralTypes.c.reference == "Ref 1")
        .count()
        == 2
    )
    results = (
        temp_db.query(temp_db.SpectralTypes)
        .filter(temp_db.SpectralTypes.c.reference == "Ref 2")
        .table()
    )
    assert len(results) == 1
    assert results["source"][0] == "Fake 3"
    assert results["spectral_type_string"][0] == "Y2pec"
    assert results["spectral_type_code"][0] == [92]


def test_ingest_spectral_type_errors(temp_db):
    # testing for publication error
    spt_data4 = {
        "source": "Fake 1",
        "spectral_type": "M5.6",
        "regime": "nir",
        "reference": "Ref 1",
    }
    # spt_data5 = {
    #     "source": "Fake 2",
    #     "spectral_type": "T0.1",
    #     "regime": "nir",
    #     "reference": "Ref 1",
    # }
    # spt_data6 = {
    #     "source": "Fake 3",
    #     "spectral_type": "Y2pec",
    #     "regime": "nir",
    #     "reference": "Ref 4",
    # }

    with pytest.raises(AstroDBError) as error_message:
        ingest_spectral_type(
            temp_db,
            spt_data4["source"],
            spectral_type_string=spt_data4["spectral_type"],
            reference=spt_data4["reference"],
            regime=spt_data4["regime"],
        )
    assert "Spectral type for Fake 1 already in the database" in str(
        error_message.value
    )
    # assert "The publication does not exist in the database" in str(error_message.value)


def test_companion_relationships(temp_db):
    # testing companion ingest
    # trying no companion
    with pytest.raises(AstroDBError) as error_message:
        ingest_companion_relationships(temp_db, "Fake 1", None, "Sibling")
    assert "Make sure all required parameters are provided." in str(error_message.value)

    # trying companion == source
    with pytest.raises(AstroDBError) as error_message:
        ingest_companion_relationships(temp_db, "Fake 1", "Fake 1", "Sibling")
    assert "Source cannot be the same as companion name" in str(error_message.value)

    # trying negative separation
    with pytest.raises(AstroDBError) as error_message:
        ingest_companion_relationships(
            temp_db,
            "Fake 1",
            "Bad Companion",
            "Sibling",
            projected_separation_arcsec=-5,
        )
    assert "cannot be negative" in str(error_message.value)

    # trying negative separation error
    with pytest.raises(AstroDBError) as error_message:
        ingest_companion_relationships(
            temp_db, "Fake 1", "Bad Companion", "Sibling", projected_separation_error=-5
        )
    assert "cannot be negative" in str(error_message.value)
