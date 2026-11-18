# January 2007 / 2008 source-only local QA: real observed scenes

Post hoc source feasibility window, not an independent ecological confirmatory analysis.

The earlier February–March 2008 QA probe yielded no clear non-snow, non-water point-neighborhood pixels at Litchfield, Humble or Torgersen. Instead of declaring historical imagery impossible, the **separately labeled January 2007 and January 2008** source audit at the same region and QA method succeeded: [Actions 40859849012](https://github.com/zuizui0223/mina/actions/runs/40859849012), original artifact **12890723051**, ZIP SHA-256 **511a38535e151b1f7502a25be5ea5989409c067601bd7374d2db06656ef76268**. It read 6 January 2007 scenes and 3 January 2008 scenes across all three fixed 5×5 site-neighborhood grids without asset errors.

| Site | Jan 2007 max QA clear points (scene date) | Jan 2008 max QA clear points (scene date) |
|---|---:|---:|
| Litchfield | 25 (2007-01-05) | **7** (2008-01-15) |
| Humble | 0 | **16** (2008-01-15) |
| Torgersen | 17 (2007-01-05) | **3** (2008-01-15) |

These are **per-scene local ground-probe maxima**, not measured growing vegetation, colony area or plant cover. One January 2008 image with 13% whole-scene reported cloud also had some locally QA-clear pixels; this explicitly demonstrates why the isolated March 2008 94% cloud scene does not prove all months in that season lack observability.

**New immediate next source-quality gate:** determine whether *exactly the same EPSG:3031 ground sample locations* pass QA in any January 2007 × January 2008 pair, selecting images based solely on common QA support, not NDVI. Even if there are overlapping clear points, the historic nesting polygons, independent soil/plant-class validation, and multiple pre/post years remain required. Also note native 30 m raster pixel footprints can differ across paths despite the same ground-point coordinates.

No numeric conclusion about vegetation succession or penguin causation is available.
