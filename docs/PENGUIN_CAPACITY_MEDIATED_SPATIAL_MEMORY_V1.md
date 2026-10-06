# Capacity-mediated spatial memory in penguin breeding networks — synthesis v1

**Status:** generated mechanistic synthesis from already-exposed mina results and published penguin ecology. Not a new confirmatory result and not part of the frozen Ecology submission.

## Central biological question

How do penguin populations redistribute breeders among established breeding sites and islands as abundance declines and recovers?

The key distinction is not simply decline versus increase. It is whether additional or lost breeders are absorbed **within already occupied breeding sites** or cause a change in the **number and identity of occupied sites**.

## Mina evidence

### Decline: breeding space contracts non-proportionally

Five declining Palmer/Signy trajectories show effective breeding-component contraction beyond proportional thinning/count-error expectations:

- Palmer Cormorant: E -19.1%;
- Palmer Humble: E -50.6%;
- Palmer Litchfield: E -82.7%;
- Signy Adélie: E -37.2%;
- Signy chinstrap: E -50.6%.

The endpoint recurs, but the refuge route is not universal:
- Palmer loses the initially dominant component in all three trajectories;
- Signy retains and strengthens the initially dominant component in both species.

Thus simple fixed "largest colony = refuge" sorting is insufficient.

### Exact-zero losses are sticky in the existing component records

An exploratory exact-zero screen of the same five trajectories found:
- 22 positive -> zero loss spells across 21 breeding components;
- 1 completed reoccupation;
- 0 reoccupations within 2 y among 21 eligible spells;
- 0 within 3 y among 19;
- 0 within 5 y among 18;
- 0 within 10 y among 17.

The only completed return occurred after 16 y and at a lower surrounding-population state than at loss. Therefore a simple "return requires a higher regional N than loss" threshold is not supported.

Most Palmer losses occurred during sustained decline and the surrounding population never regained the loss-state abundance. These data therefore show sticky vacancy descriptively but do not establish hysteresis causally.

### Growth: two regional networks intensify strongly

In the three exposed increasing MAPPPD regional networks:

**Adélie, Victoria Land**
- total abundance +33.1%;
- E -26.6%;
- 8/11 retained monitored sites increased;
- initial dominant Cape Crozier West share 37.2% -> 48.6%;
- that one site absorbed 83.2% of net regional growth;
- initial top half of sites absorbed 95.4% of gross positive gains.

**Gentoo, Central-west Antarctic Peninsula**
- total abundance +21.8%;
- E -16.3%;
- 4/7 sites increased;
- initial dominant Cuverville share 33.9% -> 40.0%;
- initial dominant absorbed 67.9% of net growth;
- initial top half absorbed 95.8% of gross positive gains.

**Gentoo, South Shetland Islands**
- total abundance +64.1%;
- E -1.1%;
- growth was more diffuse;
- initial top half still absorbed 89.4% of gross positive gains.

These are descriptive exposed panels, not a colonisation test. They show that population growth can be absorbed very unevenly among already occupied sites.


### Simple network-cascade and rich-get-richer stories are not supported

Two additional exposed-data screens narrow the mechanism.

First, the whole-network loss-feedback screen used 632 occupied component-year transitions with 22 exact-zero losses. Focal local size was the strongest screened predictor of next-year loss (standardized coefficient about -1.99 across all five trajectories; -2.40 in Palmer-only). Adding the fraction of other breeding components still occupied did not improve leave-one-population-out prediction: log loss worsened from 0.1091 to 0.1117 across all five trajectories and from 0.1277 to 0.1316 in Palmer-only.

Thus the data do not support a simple process in which losing one breeding component globally erodes network integrity and thereby accelerates the next loss.

Second, in the three increasing MAPPPD networks, change in regional share was not consistently related to initial share. Descriptive Spearman correlations were -0.064, -0.143 and +0.100. A universal positive-frequency "largest colony gets proportionally larger" rule is therefore also unsupported.

Static mapped ice-free area and nearest-site distance were likewise non-transferable across the three networks. The sharpest local example is Victoria Land: Cape Crozier West gained +0.114 regional share while Cape Crozier East, only ~1.51 km away and with more mapped ice-free area within 2 km (771 versus 614 ha), lost -0.0355 share.

These null/heterogeneous results move the mechanism away from whole-network cascade or colony size alone and toward **site-specific residual capacity and local trajectory**.

## Published biological constraints

### Breeding-space limitation is real

Southwell & Emmerson (2020; Ecology and Evolution, doi:10.1002/ece3.6037) found strong nonlinear density dependence in East Antarctic Adélie populations associated with breeding-habitat availability.

Their fitted relationships predicted:
- regional growth falling below its maximum when unoccupied breeding habitat was <80 m2 per breeding pair;
- regional growth reaching zero near 28 m2 per breeding pair;
- local island growth falling below its maximum below about 200 m2 unoccupied breeding habitat per pair.

These values are study-specific and must not be treated as universal thresholds.

### Colonisation can be very delayed

Southwell, Wotherspoon & Emmerson (2021; Oecologia, doi:10.1007/s00442-021-04958-z) reported the first new breeding-patch colonisation in the Windmill Islands after roughly half a century of sustained regional population growth, as density-dependent resource limitation was becoming evident.

### Apparent site turnover is often false

Southwell et al. (2017; Auk, doi:10.1642/AUK-16-125.1) evaluated 16 proposed East Antarctic Adélie colonisation/extinction events using direct observations concurrent with satellite imagery and concluded that none of the 16 had actually occurred. This emphasizes that true breeding-site turnover is rare and that small colonies are easily missed.

### Increasing habitat can reduce inter-colony emigration

LaRue et al. (2013; PLOS ONE, Beaufort Island) reported a 71% increase in available nesting habitat since 1958, an 84% increase in population size, and reduced emigration from Beaufort to nearby Ross Island colonies after habitat availability increased.

This is direct evidence that terrestrial breeding-space capacity can alter inter-colony movement even in a species capable of long marine travel.

## Capacity-mediated spatial-memory hypothesis

The combined pattern suggests a thresholded redistribution game in which **local patch state** is more important than a coarse whole-network occupancy count.

For an occupied breeding site i:

U_stay(i) = Q_i + S_i(n_i) - C_i(n_i / K_i) + Phi_i

where:
- Q_i is physical breeding quality;
- S_i is conspecific/social benefit;
- C_i is crowding or breeding-space cost;
- K_i is local breeding capacity;
- Phi_i is philopatry/familiarity.

For an alternative site j:

U_move(j) = Q_j + S_neighbor(j) - D_ij - F_j

where D is effective isolation/travel cost and F is the cost/uncertainty of founding or switching.

### During decline

N falls -> crowding cost at established sites falls.

Therefore marginal breeding components can disappear while surviving sites gain spare capacity. Breeders do not need to spread over all former breeding sites to maintain the remaining population.

### During early recovery

N rises, but surviving sites still have spare capacity.

Growth can therefore be absorbed by established sites:
- no founding cost;
- known nesting substrate;
- conspecifics already present;
- philopatry favours return.

This predicts **intensification before expansion**.

### Near saturation

As n_i / K_i rises, crowding and breeding-space limitation increase.

Only then can the payoff of moving/founding another site exceed the payoff of staying. Colonisation and inter-island redistribution should therefore accelerate near local habitat limitation rather than increase smoothly with total regional abundance.

## Why island structure matters

The island landscape makes the redistribution decision discrete.

In continuous habitat, a breeder can shift gradually through space. In Antarctic breeding archipelagos, suitable ice-free ground is divided among islands and rock outcrops separated by ocean, snow and ice. Crossing from one established breeding site to another therefore involves a real behavioural and spatial transition.

The resulting prediction is not simply "isolated islands are colonised less often." It is:

> **island boundaries raise the threshold at which population growth switches from intensification of established colonies to spatial expansion.**

Isolation, accessible ice-free area, local habitat capacity and nearby colony state may jointly determine that threshold, but the current Palmer/Signy screen provides no support for a coarse whole-network cascade. Any social/rescue effect now needs to be local and spatially explicit rather than inferred from the number of occupied components.

## Strong falsifiable predictions

1. In increasing populations, expansion into new/reoccupied sites should occur preferentially when established sites have low remaining breeding-habitat availability.
2. Before that point, most growth should occur within established sites.
3. Increasing local habitat capacity should reduce emigration, as observed at Beaufort.
4. Following decline, lost sites should remain empty while surviving sites have spare capacity; reoccupation should accelerate only after survivors again approach local limitation.
5. Geographic connectivity should matter most at the expansion step, not necessarily during within-site intensification.
6. If conspecific attraction adds an additional barrier, otherwise suitable empty sites should colonise less readily than equally connected already occupied sites even after accounting for capacity.

## What would be genuinely new

The novel claim to test is not that Adélie penguins are philopatric, density dependent, or capable of colonisation. Those are known.

The new synthesis is:

> **population decline and recovery may follow different spatial routes because loss creates spare capacity in surviving colonies. Recovery is therefore first expressed as intensification, and island-to-island expansion is delayed until local breeding capacity again becomes limiting.**

This mechanism can generate apparent spatial hysteresis without requiring a strict social Allee effect. Conspecific attraction could strengthen the delay, but it is not required.

## Immediate empirical priority

The cleanest next test is an independent site-level occupancy/population dataset containing:
- true repeated occupancy observations;
- local abundance or occupied area;
- potential/remaining breeding habitat;
- coordinates/connectivity;
- enough growth periods to observe both intensification and colonisation.

The East Antarctic occupancy database is structurally appropriate according to its published description, but current AADC download infrastructure requires an access handoff and the dataset's citation guidance asks users to contact the originator before applying the data. No effect analysis should be opened until that provenance step is completed.
