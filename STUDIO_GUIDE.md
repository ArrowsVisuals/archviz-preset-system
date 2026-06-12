# Studio Guide — (AV) Scene for in-house architecture teams

How to map real deliverables to templates, pools and workflow patterns.

## Pick by deliverable

| Deliverable | Template | People pool | Cars pool | Vegetation pool |
|---|---|---|---|---|
| Developer marketing — villas/townhouses | townhouse_row / villa | people_gulf_family or people_street | cars_luxury or cars_family_realistic | vegetation_gulf or vegetation_lush_marketing |
| Authority / municipality submission | (matching typology) | people_submission_minimal | cars_neutral_modest | vegetation_minimal_submission |
| Client design review | (matching typology) | people_submission_minimal or people_professional | cars_neutral_modest | vegetation_gulf |
| Office / mixed-use / tower | tower / apartment_midrise | people_professional | cars_family_realistic | vegetation_gulf |
| School | school | people_school_morning | cars_institutional | vegetation_gulf |
| Mosque | mosque | people_mosque_courtyard | cars_neutral_modest | vegetation_minimal_submission |
| Healthcare | apartment_midrise* | people_hospital_entrance | cars_institutional | vegetation_gulf |
| Retail frontage | commercial_retail | people_street or people_professional | cars_family_realistic | vegetation_minimal_submission |
| Any 3D/Enscape perspective view | perspective_exterior | (by audience, as above) | (by audience) | (by audience) |
| Interior view | interior_room | interior_life | — | — |
| Villa amenity / pool area | villa or perspective_exterior | gardens_pool_deck | — | — |
| Renovation & extension | renovation_photo | (by audience) | (by audience) | usually none — photo context |

*until a dedicated healthcare template exists; adjust drawing_notes.

## The audience pattern
Render the SAME elevation for different audiences as different SHOTS of
one project (see projects/example_school.txt):
```
front_marketing:  people_school_morning, cars_institutional, vegetation_lush_marketing
front_submission: people_submission_minimal, cars_neutral_modest, vegetation_minimal_submission
```

## The revision workflow (the in-house superpower)
When a design revision arrives, re-run the SAME shot + variation + seed
on the new drawing: identical entourage and composition, only the
architecture changes. Approved render filenames carry their own recipe
(`project_shot_v007_s42`) — type the numbers back in to reproduce.

## The option-study pattern (material schemes)
Duplicate the project file per scheme: `villa_a.txt`, `villa_b.txt`,
changing only the material_legend field. Same shots, same variation,
same seed across schemes = a perfectly comparable A/B/C set.

## Sheet-consistency rules
- Sun direction lives in the project identity field, stated by compass
  ("warm sun from the south-west"), never "from upper left" — front and
  back elevations flip left/right.
- Never put lighting, materials or camera in pool lines.
- Front and back shots use different pools so the same figures never
  appear on two elevations of one sheet.

## Cultural correctness defaults (Gulf practice)
- people_gulf_family / mosque / school pools: modest dress always,
  dignified scenes, guard clauses enforce no text and no inappropriate
  content.
- Match the car register to the program: luxury pools are wrong for
  schools, government and affordable housing.
- Where a landscape architect's drawing exists, use
  vegetation_minimal_submission and extend it with the actual species.
