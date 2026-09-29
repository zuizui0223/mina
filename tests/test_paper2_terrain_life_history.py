import numpy as np
import pandas as pd

from scripts.run_paper2_terrain_life_history import (
    SPECIES,
    build_terrain_frames,
    center_terrain_within_block,
    permute_terrain_within_blocks,
)


def fake_terrain():
    return pd.DataFrame(
        {
            "site_id":[f"S{i:03d}" for i in range(122)],
            "elevation_relief_p90_p10_m_2000m":np.linspace(0.5,900.0,122),
        }
    )


def fake_units():
    rows=[]
    for sp,offset in zip(SPECIES,(0,10,20)):
        for j in range(4):
            site=f"S{offset+j:03d}"
            rows.append(
                {
                    "unit_id":f"{sp}|{site}",
                    "site_id":site,
                    "species_id":sp,
                    "region":"R1" if j<2 else "R2",
                    "ccamlr_id":"48.1" if j<2 else "88.1",
                    "seasons":"1990;1995;2000;2005;2010",
                }
            )
    return pd.DataFrame(rows)


def test_global_terrain_standardization_is_shared_across_species():
    terrain=fake_terrain()
    units=fake_units()
    frames=build_terrain_frames(units,terrain,expected=None)
    assert {sp:len(frames[sp]) for sp in SPECIES} == {
        "ADPE":4,"CHPE":4,"GEPE":4
    }
    atlas_raw=np.log1p(
        terrain["elevation_relief_p90_p10_m_2000m"].to_numpy(float)
    )
    expected=(atlas_raw-atlas_raw.mean())/atlas_raw.std(ddof=0)
    value=float(
        frames["ADPE"].loc[
            frames["ADPE"]["site_id"].eq("S000"),"T"
        ].iloc[0]
    )
    assert np.isclose(value,expected[0])
    assert "A" not in frames["ADPE"].columns
    assert "H" not in frames["ADPE"].columns
    assert "AH" not in frames["ADPE"].columns


def test_centering_is_exactly_within_frozen_trait_block():
    frames=build_terrain_frames(fake_units(),fake_terrain(),expected=None)
    centered=center_terrain_within_block(frames["ADPE"])
    means=centered.groupby("trait_block")["Tc"].mean().to_numpy(float)
    assert np.allclose(means,0.0,atol=1e-12)


def test_block_permutation_preserves_each_blocks_terrain_multiset():
    frames=build_terrain_frames(fake_units(),fake_terrain(),expected=None)
    frame=frames["ADPE"]
    perm=permute_terrain_within_blocks(
        frame,global_index=3,species_index=0,seed=99
    )
    for block in sorted(frame["trait_block"].unique()):
        a=sorted(frame.loc[frame["trait_block"].eq(block),"T"].tolist())
        b=sorted(perm.loc[perm["trait_block"].eq(block),"T"].tolist())
        assert np.allclose(a,b)
    assert frame["unit_id"].tolist() == perm["unit_id"].tolist()
