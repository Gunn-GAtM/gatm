import os

chapter_names = (
    "trig_review itsasnap snap_flip rrg inf cmplx_geo vitamin_i mtrx_mult map_plane plane_rot mat_gen "
    "comp_map inverses mod_m eigen".split(" ")
)

for chapter in chapter_names:
    os.system(
        "./bf.sh {name}; cp -f {name}/{name}_source.pdf build/chapters/{name}.pdf".format(
            name=chapter
        )
    )
for chapter in chapter_names:
    os.system(
        "./bfa.sh {name}; cp -f {name}/{name}_answers.pdf build/chapters_answers/{name}.pdf".format(
            name=chapter
        )
    )
