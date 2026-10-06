# East Antarctic Adélie potential-habitat support audit v1

**Status:** structural pre-effect audit only.

## Source
Australian Antarctic Data Centre dataset:
- metadata ID: AAS_4088_Adelie_Potential_Habitats
- DOI: 10.4225/15/5758F4EC91665

## Purpose
Establish a denominator of candidate breeding habitat that is independent of whether
Adélie penguins were observed breeding there.

This is required to distinguish:
- intensification of already occupied breeding sites;
- recolonisation of previously occupied sites;
- first colonisation of potential but previously unoccupied breeding habitat.

## Allowed audit information
- manifest/file names;
- schema/field names;
- row or feature counts;
- candidate-site identifiers;
- group/subgroup/region identifiers;
- geometry or coordinate availability;
- whether the identifiers can be joined structurally to the occupancy database.

No occupancy values or colonisation outcomes may be opened here.

## Gate
A future first-colonisation analysis is structurally eligible only if:
1. potential habitat has a stable candidate-site identifier or geometry;
2. spatial coordinates/geometry are present;
3. at least 20 candidate habitat units are available;
4. a deterministic structural join or spatial relation to the occupancy-site system can be specified before outcomes are opened.

Failure stops the never-occupied-site route. It does not alter the already-frozen recovery-memory screen or Paper 1.
