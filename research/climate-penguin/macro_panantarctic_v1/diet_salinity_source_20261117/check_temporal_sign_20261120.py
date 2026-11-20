"""Post-discovery temporal stability diagnostic using the frozen original inputs.

This reuses already examined observations, so it is not independent replication.
"""
import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd
import fit_one_frozen_DEEPAA_100km_optical_d15N_20261119 as original


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--isotope-zip', required=True)
    parser.add_argument('--polynya-source-zip', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    expected = '702ab3eeff9ed953c19a9e696492ba9bf5cddce204d40a9c7d9b1234d98f9f96'
    assert hashlib.sha256(Path(args.polynya_source_zip).read_bytes()).hexdigest() == expected
    panel, _ = original.load(args)
    rows = []
    early_sites = set(panel.loc[panel.season.between(2004, 2006), 'site_id'])
    for label, start, end in [('all', 2004, 2010), ('early', 2004, 2006),
                              ('late', 2007, 2010), ('late_known_sites', 2007, 2010)]:
        sample = panel.loc[panel.season.between(start, end)].copy().reset_index(drop=True)
        if label == 'late_known_sites':
            sample = sample.loc[sample.site_id.isin(early_sites)].reset_index(drop=True)
        for model in ('M_P', 'M_SP'):
            result = original.association(sample, model, 'region')
            coefficient = original.extract_feature(result, original.P)
            rows.append({
                'period': label, 'start': start, 'end': end, 'model': model,
                'rows': len(sample), 'sites': sample.site_id.nunique(),
                'regions': sample.source_region.nunique(),
                'beta_per_10pp': coefficient['native_beta'] * 0.1,
                'ci_low_per_10pp': coefficient['t95ci'][0] * 0.1,
                'ci_high_per_10pp': coefficient['t95ci'][1] * 0.1,
            })
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(output / 'temporal_sign_diagnostic.csv', index=False, lineterminator='\n')
    holdout, _ = original.holdout(panel)
    (output / 'temporal_prediction_replay.json').write_text(
        json.dumps(holdout, indent=2), encoding='utf-8', newline='\n')
    print(pd.DataFrame(rows).to_string(index=False, lineterminator='\n'))


if __name__ == '__main__':
    main()
