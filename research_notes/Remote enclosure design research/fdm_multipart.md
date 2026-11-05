# Multi-part FDM handheld enclosures that look premium and print without supports

Context: remote enclosure 51 x 206 x 15.8 mm. Parts: front shell (screen window + key holes), back plate with palm swell, button caps. Printed on a consumer FDM printer (Bambu/Prusa) with a 0.4 mm nozzle, in PLA or PETG, possibly two-tone.

Source quality note: there are few primary sources for FDM-specific cosmetic rules. The strongest numeric sources are the Prusa KB, the Hydra Research design rules, the Makers Making Change (MMC) OpenAT design guide (tuned on Bambu P1S and Prusa MK4) and the CNC Kitchen insert datasheet. Many search hits were SEO or affiliate pages. Those were excluded, or their claims are flagged where used.

## 1. Splitting strategy and making seams look intentional

### Takeaway
Split so that every visible surface is either on the bed or faces upward, and make the seam a deliberate shadow line (an overlapping lip with a small visible step) rather than a flush butt joint. A flush joint between two FDM parts always shows mismatch. A consistent overlap with a chamfer reads as designed. The only fully dimensioned recipe found is MMC's: 1.6 mm walls, a 1.6 mm lip, a 0.2 mm offset and a 0.4 mm outer chamfer.

### Cited Findings
- Shadow-line recipe for 1.6 mm walls:
  - On the bottom half, sketch offsets of 0.2 mm and 1.8 mm from the inner wall edge and extrude both down 1.6 mm.
  - Extrude only the 0.2–1.8 mm band up 1.6 mm to form the lip.
  - Chamfer the lip base by 1.8 mm so it prints without support.
  - Chamfer the outer edge of both halves by 0.4 mm "so any misalignment doesn't create a visible overhang".
  - The overlap self-aligns the halves and hides print inconsistencies better than a butt joint.
  - [MMC OpenAT – Shadow Lines](https://makersmakingchange.github.io/OpenAT_Design_Guide/Design_Elements_For_3D_Printed_Parts/Shadow-Lines.html)
- A shadow line is one half with a rim that underlaps and the other half overlapping with a small standoff. It self-locates the parts and gives a consistent look at the seam. A commenter notes the lip also stiffens the shell. — [Hackaday 2023](https://hackaday.com/2023/08/07/enhance-your-enclosures-with-a-shadow-line)
- A uniform gap reads as intentional even when the dimensional errors are unchanged. This is opinion from a less authoritative write-up. — [chaplaintig write-up](https://chaplaintig.pages.dev/articles/shadow-lines-borrowing-factory-wisdom-to-make-your-3d)
- General workflow: split the shell at a parting line, then add a lip-and-groove feature with clearance. — [All About Circuits](https://www.allaboutcircuits.com/industry-articles/six-steps-for-designing-a-custom-3d-printed-electronics-enclosure/)
- Split large or complex parts so each piece can be oriented well and needs fewer supports. Seams are more visible on smaller models. Alignment pegs help glued seams. — [Prusa KB – Modeling with 3D printing in mind](https://help.prusa3d.com/article/modeling-with-3d-printing-in-mind_164135)
- Two-tone and separate-faceplate example: a NES controller shell prints the shell on a smooth PEI plate and the removable faceplate on a textured PEI plate to get contrasting finishes. — [MakerWorld NES shell with removable faceplate](https://makerworld.com/en/models/1082113-nes-controller-shell-with-removable-faceplate) (via search summary)

### Inferences
- Recommended split for this remote:
  - (a) Front shell, printed face-down so the top face sits on the bed.
  - (b) Back plate with palm swell.
  - (c) Optionally a separate bezel or screen surround, or an accent plate, in a second colour.
  - (d) Button caps.
- Put the main parting line on the side wall, not on the top face edge. A line roughly 3–5 mm below the top face lets the front shell carry the crisp top edge and corner chamfer, while the back carries the curve. Add the MMC lip (1.6 mm tall) inside the wall.
- Visible reveal: the 0.4 mm chamfer on each half creates a V-groove about 0.8 mm wide by 0.4 mm deep at the seam. That is a practical shadow-gap size for a 0.4 mm nozzle. If a stepped reveal is preferred, 0.5–1.0 mm wide by 0.5 mm deep matches one to two extrusion widths. No source gives a specific number for this; it is derived from the MMC chamfer and nozzle width.
- Two-tone without a seam on the face: a separate inlay or bezel plate dropped into a pocket in the front shell, held by press-fit or tape. Alternatively, an AMS colour change on Z layers so that the first few millimetres of the face-down top surface are one colour. A Z colour change is seam-free and needs no assembly.

### Gaps
- No primary source gives reveal or shadow-gap widths specifically for FDM handhelds, beyond MMC's chamfer and offset numbers.
- No authoritative guidance was found on a mid-frame or accent-band split for printed handhelds.

## 2. Print orientation, visible surfaces, curved backs, surface tricks

### Takeaway
Print the front shell face-down on the plate. A textured PEI plate gives a uniform, injection-moulded-looking texture that hides layer lines. A smooth plate gives gloss. Print the curved back so its layer lines follow the long axis and the curve is built up in Z, and use variable or adaptive layer heights (0.08–0.12 mm on shallow curves) to suppress stair-stepping. Place seams on inner or hidden faces, and keep visible faces of buttons at 0.12–0.16 mm.

### Cited Findings
- Surfaces printed directly on the bed are smooth. Surfaces over supports are rougher. — [Prusa KB](https://help.prusa3d.com/article/modeling-with-3d-printing-in-mind_164135)
- Textured PEI hides layer lines better than smooth PEI. This comes from a lower-authority guide. — [evetech textured vs smooth PEI](https://evezone.evetech.co.za/deep-dives/textured-pei-vs-smooth-pei-build-plates-which-finish-for-which-print)
- Visible-surface orientation in controller shells:
  - A GameCube shell remix prints the visible top on the bed.
  - It prints a panel upright because flat orientation causes stair-stepping on curves.
  - Both points are designer notes from the search summary. — [MakerWorld GameCube shell](https://makerworld.com/en/models/3424403-mario-cube-gamecube-shell)
- Use 0.12–0.16 mm layers for buttons and visible surfaces. Print buttons with the contact face smooth and the visible face up. Avoid supports on surfaces that should feel good. A smooth plate gives a clean button bottom, while textured plates can make buttons feel too rough. — [Held Games guide](https://heldgames.com/guides/how-to-3d-print-handheld-shell-buttons)
- Seam placement: one 8BitDo grip designer says the Z seam is the hardest part to manage. They placed it on the inside front, where fingers don't rest, using X/Y coordinates. — [Printables 8BitDo Zero 2 grip](https://www.printables.com/model/355248-8bitdo-zero-2-grip)
- Scarf joint seams in OrcaSlicer: modes are none, contour, and contour plus hole. Related settings include scarf angle threshold, speed, start height and steps. The wiki notes whole-loop scarf "may increase print time without significant seam improvement". — [OrcaSlicer wiki – seam](https://www.orcaslicer.com/wiki/print_settings/quality/quality_settings_seam)
- Variable layer height in PrusaSlicer can partly improve fillets. — [Prusa KB](https://help.prusa3d.com/article/modeling-with-3d-printing-in-mind_164135)
- Both PrusaSlicer and Bambu Studio disable adaptive layer height in vase mode. — [slicerguide](https://slicerguide-com.pages.dev/posts/adaptive-layer-height-guide) (secondary source)
- Fuzzy skin settings:
  - "Thickness" is the maximum offset of each skin point perpendicular to the perimeter.
  - "Point distance" is the spacing between inserted points.
  - Source: [SimplyPrint PrusaSlicer settings](https://simplyprint.io/slicer/prusaslicer.md)
- Matte filaments hide layer lines better than glossy ones. This is a vendor claim for both matte PLA and matte PETG. — [Bambu forum: matte PETG vs PLA](https://forum.bambulab.com/t/matte-optics-for-petg-vs-pla/172750); [3DPC Unveil matte PETG](https://3dprintingcanada.com/products/white-unveil-form-matte-petg-1-75mm-1kg)

### Inferences
- Front shell: print top face down on textured PEI. You get a uniform stippled face with no layer lines, and the screen window and key holes become simple through-cuts. Their top edges are bed-crisp, so give them a 0.3–0.5 mm chamfer on the bed face (see section 3).
- Back plate with palm swell: print outside face up so the swell is built from layers. Use variable layer height around 0.08 mm near the flattest part of the dome and up to 0.2–0.24 mm on steep side walls. Use top-surface ironing only if the crown is near-flat. Ironing only affects top-most flat layers, so it does nothing on curved slopes. An alternative is to print the back face-down on textured PEI if the palm swell can be moved into a separate insert, or if the back is made flat with a chamfered perimeter.
- Long axis (206 mm) along X or Y keeps layer lines running lengthwise on the side walls. They then read as fine pinstripes along the device, which looks more intentional than lines crossing it.
- Fuzzy skin can be painted only onto the grip area of the back or sides as a grip texture. Exact Bambu defaults could not be verified; see gaps.
- Bed size check: 206 mm exceeds a 180 mm bed (Bambu A1 mini) but fits a 256 mm bed (P1/X1/A1) and a 250 x 210 mm bed (Prusa MK4). Diagonal placement on a 180 mm bed gives about 254 mm, so it fits flat for thin parts. This comes from general knowledge of printer specs, so verify against the specific printer.

### Gaps
- The Bambu Lab wiki pages (fuzzy skin, ironing, variable layer height) returned HTTP 402 and could not be read, so the default values for fuzzy skin thickness and point distance and the default ironing flow are unverified.
- No controlled test was found comparing stair-stepping versus layer height on shallow domes.

## 3. Rules for printing without supports

### Takeaway
Keep every downward-facing surface at or below 45° from vertical; 50–60° is fine on well-cooled machines. Use chamfers rather than fillets on downward edges, teardrop or flat-roofed horizontal holes, and bridges under about 10 mm. Add a 0.3–0.5 mm chamfer on all bed-contact edges instead of relying only on slicer elephant-foot compensation.

### Cited Findings
- Overhang limits:
  - 45–60° overhangs print cleanly with a 0.4 mm nozzle.
  - Machines with 360° cooling (Prusa MK4S, CORE One) can print up to 75°.
  - Fillets on bed-facing surfaces create a steep overhang, so use a chamfer when finish matters. Chamfer mating edges to ease assembly.
  - Source: [Prusa KB](https://help.prusa3d.com/article/modeling-with-3d-printing-in-mind_164135)
- Hydra Research design rules:
  - Avoid unsupported overhangs steeper than about 50° from vertical. Many printers manage about 70°.
  - Keep bridges under about 10 mm.
  - Fillets should be larger than about 1 mm. Avoid downward-facing fillets and use chamfers instead.
  - Add a base chamfer of about 0.3 mm (first layer plus layer height) to counter first-layer squish.
  - Round base corners of large parts with a radius above 4 mm to reduce warping.
  - Unsupported holes: add two tangent rectangles above the hole, one layer and two layers high (the "sacrificial bridging" trick).
  - Source: [Hydra Research design rules](https://www.hydraresearch3d.com/design-rules)
- Teardrop holes: give horizontal holes a pointed 45° roof and keep vertical holes round. — [Superhive precision holes](https://superhivemarket.com/products/precision-holes?num=4&src=new); [Pollen AM – holes](https://www.pollen.am/design_for_3d_printing_holes)
- Elephant foot:
  - A bottom chamfer makes the first layers progressively smaller and offsets the spreading. — [Wevolver](https://www.wevolver.com/article/troubleshooting-the-3d-printing-elephant-foot-phenomenon)
  - One user adds a 0.5 mm chamfer and skips slicer compensation. — [Creality forum](https://forum.creality.com/t/elephants-foot-and-brim-dont-play-nice-together/52835)
  - Slicer compensation also shrinks interior holes on the first layers. — [Simplify3D forum](https://forum.simplify3d.com/viewtopic.php?p=37828)
- The MMC lip uses a 1.8 mm chamfer at its base so it prints unsupported. — [MMC Shadow Lines](https://makersmakingchange.github.io/OpenAT_Design_Guide/Design_Elements_For_3D_Printed_Parts/Shadow-Lines.html)
- MMC snap tabs should overhang at 45° or more from horizontal. — [MMC Snap Fits](https://makersmakingchange.github.io/OpenAT_Design_Guide/Design_Elements_For_3D_Printed_Parts/Snap_Fits.html)

### Inferences
- For the face-down front shell:
  - Screen window and key holes are vertical through-cuts, so no supports are needed.
  - The inner top-face edge of each opening can have a 45° chamfer facing inward, which prints fine.
  - Inner ledges that hold the display or PCB must be chamfered at 45° or bridged under 10 mm. The display ledge across a 51 mm-wide shell is too long to bridge, so make it a 45° chamfered step.
- Snap-hook barbs and lip undersides need 45° lead-ins.
- Bed-face edge of the front shell: a 0.4–0.5 mm chamfer covers elephant foot and doubles as a visual edge. Set slicer elephant-foot compensation to about 0.1–0.15 mm or zero so key holes are not undersized.

### Gaps
- No controlled source gives a maximum bridge length for PLA versus PETG at 0.4 mm. The "~10 mm" figure is a conservative rule of thumb, and many printers bridge 30 mm or more.

## 4. Joining: snap fits, heat-set inserts, bosses, magnets, alignment, tolerances

### Takeaway
For a remote that must be opened, use M2 or M2.5 heat-set inserts in the back plate bosses (or the front), with screws hidden under a rubber foot or label. Alternatively, use cantilever snaps designed for at most about 2% strain in PLA (higher in PETG), printed with the hook in the XY plane. Use 0.1 mm clearance for tight fits on a tuned Bambu or Prusa, and 0.2–0.3 mm for slip fits, hinges and button caps.

### Cited Findings
- CNC Kitchen insert datasheet (L = insert length, D1 = insert outer diameter, D2 = hole diameter, W = minimum wall around the hole):

  | Insert | L | D1 | D2 hole | W min wall |
  |---|---|---|---|---|
  | M2 x 3 | 3.0 | 3.6 | 3.2 | 1.3 |
  | M2.5 x 4 | 4.0 | 4.6 | 4.0 | 1.6 |
  | M3 x 3 (short) | 3.0 | 4.6 | 4.0 | 1.6 |
  | M3 x 5.7 | 5.7 | 4.6 | 4.0 | 1.6 |

  - Blind holes should be at least L + 1 mm deep.
  - Source: [CNC Kitchen Heat-Set Insert Dimensions & Design Guidelines PDF](https://www.cnckitchen.com/s/CNCKitchen_Heat-Set-Insert-Dimensions-and-Design-Guidelines.pdf)
- Install inserts with the iron 10–20 °C above print temperature: about 225 °C for PLA and 245 °C for PETG. Print the hole-size test, since printed holes come out small. — [CNC Kitchen tips & tricks for inserts](https://www.cnckitchen.com/blog/tipps-amp-tricks-fr-gewindeeinstze-im-3d-druck-3awey); [hole test on Printables](https://www.printables.com/model/1648510-hole-size-test-for-heat-set-inserts)
- Tolerances from several sources:
  - MMC's standard clearance is 0.1 mm, tuned on Bambu P1S and Prusa MK4. Use 0.2–0.3 mm for older printers. — [MMC 3D Printing Design Tips](https://makersmakingchange.github.io/OpenAT_Design_Guide/3D_Printing_Design_Tips/3D-Printing-Design-Tips.html)
  - Hydra: about 0.1 mm for a tight fit and 0.2 mm for a loose fit. — [Hydra](https://www.hydraresearch3d.com/design-rules)
  - Prusa: printers are accurate to at least 0.2 mm, and moving parts such as hinges should start at 0.3 mm or more. — [Prusa KB](https://help.prusa3d.com/article/modeling-with-3d-printing-in-mind_164135)
  - Hubs: 0.5 mm nominal clearance for FDM snap fits, more conservative and generic across printers. — [Hubs snap-fit guide](https://www.hubs.com/knowledge-base/how-design-snap-fit-joints-3d-printing/)
- Snap fits, from Hubs:
  - Root fillet at least 0.5 x base thickness. Clip width at least 5 mm.
  - Taper the cantilever toward the tip. Avoid cantilevers built in Z.
  - Use locating lugs to take shear.
  - Deflect the clip only during assembly, not in service.
  - PLA is brittle and less suitable; PETG is tough and ductile.
  - Source: [Hubs](https://www.hubs.com/knowledge-base/how-design-snap-fit-joints-3d-printing/)
- Snap fits, from MMC:
  - 0.4 mm clearance between snap fins and the receiving hole "provided a good balance between ease of assembly/disassembly and tightness".
  - Layer lines must not lie in the plane of the tab.
  - Use a barbed hook with a flat back for a permanent joint, and angle both faces for a removable one.
  - Source: [MMC Snap Fits](https://makersmakingchange.github.io/OpenAT_Design_Guide/Design_Elements_For_3D_Printed_Parts/Snap_Fits.html)
- Cantilever strain formula: ε = 1.5·t·y / L², where t is the root thickness, y the undercut deflection and L the beam length. Fictiv's version adds a magnification factor Q. — [Fictiv snap-fit article](https://www.fictiv.com/articles/how-to-design-snap-fit-components); [Xometry snap-fit calc](https://xometry.pro/en/?p=156440)
- Fictiv lists PLA allowable strain as 4–8%. Its tables conflict internally for ABS (7% versus 20–40%). — [Fictiv](https://www.fictiv.com/articles/how-to-design-snap-fit-components)
- If a cantilever must be built along Z, elongation at break drops by about 50% and tensile strength by 20–30%, so halve the allowable strain. — [Core77 snap-fit](https://www.core77.com/posts/65318/How-to-Design-Snap-Fit-Components)
- Pins: use a diameter of at least about 1.8 mm (four extrusion widths). For functional pins, prefer store-bought dowels in holes. — [Hydra](https://www.hydraresearch3d.com/design-rules)
- Prusa: light sanding plus alignment pegs for glued seams. — [Prusa KB](https://help.prusa3d.com/article/modeling-with-3d-printing-in-mind_164135)

### Inferences
- Worked snap example. Assumptions: printed PLA, design strain no more than 2%, which is conservative against Fictiv's 4–8% and allows for FDM layer defects.
  - For a 0.6 mm undercut and a 1.2 mm root thickness: L ≥ sqrt(1.5 × 1.2 × 0.6 / 0.02) ≈ 7.3 mm.
  - Practical spec: 8–10 mm long, 1.2 mm thick tapering to 0.8 mm at the tip, 5–6 mm wide, 0.6 mm undercut with a 30–45° lead-in, root fillet of at least 0.6 mm.
  - In PETG, 3–4% design strain allows shorter or stiffer hooks.
  - Snaps in this shell (15.8 mm deep) are necessarily short. Hooks lying in the XY plane, printed as part of the lip, are preferable.
- Insert bosses for M2 x 3: hole 3.2 mm, at least 4.0 mm deep. Boss outer diameter is at least 3.2 + 2 × 1.3 = 5.8 mm; use 6.0 mm. Tie each boss to the side wall with ribs.
- Insert bosses for M2.5 x 4: hole 4.0 mm, at least 5.0 mm deep, boss outer diameter at least 7.2 mm.
- With 15.8 mm total depth, M2 x 3 inserts with M2 x 6–8 screws fit comfortably.
- Hidden screws:
  - Place 3–4 screws in the back plate near the ends, under a stick-on rubber foot strip or a recessed label or battery-door-style cover plate.
  - Alternatively, use screws only at one end plus a hooked tongue at the other end. The front shell lip slides under a hook, then one or two screws at the opposite end lock it.
  - This "hook-and-screw" pattern is common in commercial remotes but was not sourced here.
- Magnets: commonly press-fit into blind holes. No sourced dimensions were found (see gaps). Typical practice is a hole about 0.1–0.2 mm over the magnet diameter with a drop of CA glue, or a pause-and-insert to fully embed the magnet.
- Button caps should run at 0.2–0.3 mm radial clearance in the key holes (per side), a "loose fit" by the sources above, so they do not rub. Add a 0.3–0.5 mm flange underneath that is larger than the hole to retain them.

### Gaps
- There is no authoritative published allowable strain for printed PETG, and the PLA figures conflict.
- No sourced FDM-specific magnet press-fit tolerances were found.
- The Hubs page gives no cantilever length or thickness ratios.

## 5. Wall thickness, ribs, stiffness of a long thin shell, materials, post-processing

### Takeaway
Use walls at least 1.6 mm (four perimeters at 0.4 mm), consistent with the MMC recipe. A 200 mm shell flexes mainly in torsion and bending, so add the perimeter lip plus longitudinal and transverse ribs, which can be thicker than moulding rules allow because FDM has no sink marks. PETG or matte PLA are the best looks-to-ease trade-offs. For a truly premium surface, sand (wet, 220 to 2000 grit), use filler primer, then paint or coat.

### Cited Findings
- Wall thickness:
  - Wall thickness steps for a 0.4 mm nozzle: 1, 2, 3 and 4 perimeters give about 0.45, 0.9, 1.35 and 1.8 mm. Walls under one perimeter cannot print. — [Prusa KB](https://help.prusa3d.com/article/modeling-with-3d-printing-in-mind_164135)
  - Hydra recommends at least two extrusion widths (about 0.9 mm), and more for strength. — [Hydra](https://www.hydraresearch3d.com/design-rules)
  - MMC's enclosure recipe uses 1.6 mm walls. — [MMC](https://makersmakingchange.github.io/OpenAT_Design_Guide/Design_Elements_For_3D_Printed_Parts/Shadow-Lines.html)
- Injection-moulding rules:
  - Ribs no more than 60% of the nominal wall. Boss walls 40–60% of the wall they rise from. Tie bosses to walls with ribs rather than thickening them. — [Protolabs ribs/gussets](https://www.protolabs.com/resources/design-tips/design-stronger-molded-parts/); [Protolabs boss design](https://www.protolabs.com/resources/design-tips/plastic-boss-design-on-molded-parts/)
  - The 60% limit exists to avoid sink marks in moulding. That reason does not apply to FDM; this is an inference.
- The lip and overlap also stiffens the shell (Hackaday commenter). — [Hackaday](https://hackaday.com/2023/08/07/enhance-your-enclosures-with-a-shadow-line)
- Materials:
  - PLA is easy to print and fine for low-stress shells. PETG is tougher and more heat resistant, better for parts that flex or wear (buttons, clips). ABS and ASA are stronger but need ventilation. Keep filament dry. — [Held Games](https://heldgames.com/guides/how-to-3d-print-handheld-shell-buttons)
  - Prusa: PETG and ASA print fine details less well than PLA. — [Prusa KB](https://help.prusa3d.com/article/modeling-with-3d-printing-in-mind_164135)
- Matte PLA and PETG hide layer lines (vendor claims). A user reports matte PETG-CF has slight texture that "washes away layer lines". — [Bambu forum](https://forum.bambulab.com/t/matte-optics-for-petg-vs-pla/172750)
- Silk PLA+ was used for an Alpakka open-source controller shell remix (designer note). — via search summary of [MakerWorld](https://makerworld.com/en/models/3217848)
- Post-processing:
  - Grit progression: 120–220 to remove lines, then 400, 800–1000 and 1500–2000.
  - Wet-sand PLA at high grits, because dry friction heat smears it.
  - Filler primer reveals and fills defects.
  - XTC-3D is an epoxy coating, not a solvent. It fills striations to a gloss but won't fix blobs or elephant foot.
  - Primer can soak into prints and need extra coats.
  - These are hobbyist and blog sources. — [JLC3DP PLA smoothing](https://jlc3dp.com/blog/pla-smoothing); [makers101 XTC-3D](https://makers101.com/how-to-smooth-pla-with-xtc-3d/); [RPF forum](https://therpf.com/forums/threads/filling-sanding-3d-prints.359848); [Printed Solid XTC-3D](https://www.printedsolid.com/blogs/news/37036355-xtc-3d)
- Post-print finishing for button shells: trim, dry test-fit, lightly sand pins, optionally sand, prime and paint. — [Held Games](https://heldgames.com/guides/how-to-3d-print-handheld-shell-buttons)

### Inferences
- Shell stiffness for 51 x 206 x 15.8 mm:
  - Walls: 1.6–2.0 mm sides, 1.6 mm top face (about 4 perimeters plus 5–6 top and bottom layers at 0.2 mm).
  - Add one or two transverse ribs or bulkheads, 1.2 mm thick, that also locate the PCB. Add a longitudinal rib under the key area if the PCB is not screwed to the front.
  - The closed box formed by front, back and an overlapping lip with 4 screws or inserts is far stiffer in torsion than either half alone. That is the main stiffness lever, more than wall thickness.
  - Infill doesn't matter for thin shells, since they are mostly perimeters and skins.
- Material choice for looks:
  - Matte PLA on textured PEI gives the most "injection-moulded" look with the least effort.
  - PETG is better for snaps and buttons and for heat. Note that a remote left in a hot car can warp PLA (glass transition around 55–60 °C, general knowledge).
  - ASA gives an outdoor or heat-proof matte finish but is harder to print.
  - Avoid silk PLA for snaps, as it is weaker. It suits accent parts.
- No-paint premium route: matte filament, textured PEI faces, chamfered edges, shadow-line seams and two-tone accent parts.
- Paint route: the sanding and primer steps above, then a 2K or satin clear coat for durability under handling. No source was found that tested coat wear.

### Gaps
- No test data was found on bending or torsional flex of long thin FDM shells versus rib layout.
- No authoritative test was found comparing hand-feel or durability of the PLA-matte, PETG and ASA surfaces.
- Vapor smoothing applies to ABS/ASA with acetone, but no source on it was gathered in this research.

## 6. Examples of well-regarded printed handheld enclosures

### Takeaway
Community handheld and controller shells converge on a few patterns: visible faces on the bed, seams on inner faces, smooth versus textured plates for contrasting parts, removable faceplates, PETG for buttons, and 0.12–0.16 mm layers for visible parts. No in-depth published write-up of a premium FDM remote was found.

### Cited Findings
- NES controller shell with a removable faceplate, printed on mixed smooth and textured PEI. — [MakerWorld](https://makerworld.com/en/models/1082113-nes-controller-shell-with-removable-faceplate)
- GameCube shell: visible top on the bed, and a panel printed upright to avoid stair-stepping. — [MakerWorld](https://makerworld.com/en/models/3424403-mario-cube-gamecube-shell)
- 8BitDo Zero 2 grip: printed upside down with a brim, Z seam on the inside front. — [Printables](https://www.printables.com/model/355248-8bitdo-zero-2-grip)
- PS5 controller front shell remake: sanding or paint suggested for a better look. — [MakerWorld](https://makerworld.com/ru/models/2551360-ps5-controller-front-shell)
- MMC OpenAT design guide: a whole library of open assistive-tech enclosure elements, including shadow lines, snap fits, screw posts, battery covers, captured buttons, PCB capture and non-slip bases. Tuned for Bambu and Prusa. — [MMC Design Elements index](https://makersmakingchange.github.io/OpenAT_Design_Guide/Design_Elements_For_3D_Printed_Parts/Design-Elements-for-3D-Printed-Parts.html)

### Inferences
- MMC's "Captured Buttons", "Screw Posts" and "Battery Covers" pages are likely directly applicable for button caps and hidden fasteners, but were not read in this research.

### Gaps
- No detailed write-ups were reviewed for the Flipper Zero community shells, the Alpakka controller main repo, or keyboard cases (for example, gasket-mount printed cases).
- The Bambu Lab wiki was not accessible (HTTP 402).
