"""V48 Dryad original public DOI and island status file metadata: synthetic only."""
import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import audit_paper2_dryad_rat_original_metadata_v48 as m


def test_source_DOI_is_literal_publisher_doi_no_search():
    assert m.DOI=="doi:10.5061/dryad.dj524"
    assert m.ENCODED_DOI=="doi%3A10.5061%2Fdryad.dj524"
    assert m.MAX_FILES_LISTED==100


def test_no_private_or_other_host_dryad_source():
    with pytest.raises(ValueError,match="OUTSIDE_PREDECLARED"):
        m.first_party_public_get(None,"https://example.com/api/v2/datasets")


def test_version_is_explicitly_published(monkeypatch):
    calls=[]
    def fake(session,path):
        calls.append(path)
        assert path=="/api/v2/versions/454"
        return {"curationStatus":"Published","id":454}
    monkeypatch.setattr(m,"first_party_public_get",fake)
    source={"identifier":m.DOI,"license":"CC0 1.0",
            "_links":{"stash:version":{"href":"/api/v2/versions/454"}}}
    version,lic,data=m.extract_versions_metadata(source,None)
    assert version==454 and lic=="CC0 1.0"
    assert len(calls)==1


def test_wrong_original_doi_stops_without_result_matching():
    with pytest.raises(ValueError,match="DATASET_DOI"):
        m.extract_versions_metadata({"identifier":"doi:10.5061/dryad.different","curationStatus":"Published"},None)


def test_dryad_listing_must_be_complete(monkeypatch):
    def fake(session,path):
        return {"total":3,"_embedded":{"stash:files":[
          {"path":"rat_islands.csv","id":24,"size":1234,"mimeType":"text/csv","digest":"x","digestType":"md5"}
        ]}}
    monkeypatch.setattr(m,"first_party_public_get",fake)
    with pytest.raises(ValueError,match="PAGINATED"):
        m.original_file_listing(None,454)


def test_valid_original_source_file_list_distinguishes_tabular_from_pdf(monkeypatch):
    def fake(session,path):
        return {"total":2,"_embedded":{"stash:files":[
          {"path":"rat_islands.csv","id":24,"size":1234,"mimeType":"text/csv","digest":"x","digestType":"md5"},
          {"path":"article.pdf","id":25,"size":999,"mimeType":"application/pdf","digest":"y","digestType":"md5"},
        ]}}
    monkeypatch.setattr(m,"first_party_public_get",fake)
    files=m.original_file_listing(None,454)
    assert len(files)==2
    assert files[0]["tabular_source_candidate"] is True
    assert files[1]["tabular_source_candidate"] is False
    assert files[0]["bounded_download_allowed_by_size"] is True


def test_public_Dryad_version_metadata_may_omit_id_when_link_is_explicit(monkeypatch):
    def stub(session,path):
        assert path=="/api/v2/versions/26724"
        return {"curationStatus":"Published","versionNumber":1,
                "license":"https://spdx.org/licenses/CC0-1.0.html"}
    monkeypatch.setattr(m,"first_party_public_get",stub)
    original={"identifier":m.DOI,"curationStatus":"Published",
              "_links":{"stash:version":{"href":"/api/v2/versions/26724"}}}
    vid,lic,meta=m.extract_versions_metadata(original,None)
    assert vid==26724
    assert "CC0" in lic


def test_dryad_version_id_mismatch_must_stop(monkeypatch):
    def stub(session,path):
        return {"curationStatus":"Published","id":9}
    monkeypatch.setattr(m,"first_party_public_get",stub)
    original={"identifier":m.DOI,
              "_links":{"stash:version":{"href":"/api/v2/versions/26724"}}}
    with pytest.raises(ValueError,match="ID_MISMATCH"):
        m.extract_versions_metadata(original,None)


def test_dryad_public_file_id_resolved_from_official_self_link(monkeypatch):
    def fake(session,path):
        return {"total":1,"_embedded":{"stash:files":[{
            "path":"survey_island.csv","size":1200,"mimeType":"text/csv",
            "_links":{"self":{"href":"/api/v2/files/49022"}},
        }]}}
    monkeypatch.setattr(m,"first_party_public_get",fake)
    files=m.original_file_listing(None,26724)
    assert len(files)==1
    assert files[0]["official_file_id"]==49022
    assert files[0]["published_file_bytes"]==1200


def test_dryad_cross_domain_file_links_rejected(monkeypatch):
    def fake(session,path):
        return {"total":1,"_embedded":{"stash:files":[{
            "path":"survey_island.csv","size":1200,
            "_links":{"self":{"href":"https://malicious.example/api/v2/files/2"}},
        }]}}
    monkeypatch.setattr(m,"first_party_public_get",fake)
    with pytest.raises(ValueError,match="NOT_FIRST_PARTY"):
        m.original_file_listing(None,26724)
