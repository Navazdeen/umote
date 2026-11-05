# Ergonomics of a One-Handed TV Remote (51 x 206 x 15.8 mm + 3 mm palm swell, 2.4" screen at top, ring D-pad at ~108 mm, 9 x 8.6 mm keys, 150-180 g)

Research note scope: anthropometry, thumb reach, balance, back contours, tactile keys, HCI studies on remotes. The budget was limited to about 15 tool calls. Several primary PDFs (the remote-layout paper in EJMSTE, the RWTH CHI 2018 thumb-reach paper, the Human Factors 2019 smartphone-form paper) could not be read: one would not render, one refused the connection and one returned 404. Those gaps are flagged below. Where numbers come from my own geometry for this design, they are in the Inferences sections, not presented as sourced facts.

## 1. Hand anthropometry and grip dimensions (5th percentile female to 95th percentile male)

### Takeaway
The design range is a hand length of 165-210 mm and a hand breadth of 72-96 mm (ANSUR II). A 51 mm wide, roughly 16-19 mm thick body is well within comfortable one-handed holding range. Phone studies show comfort and thumb performance degrade as width rises past about 60-70 mm. A 51 mm remote is narrower than any phone tested, so width is not a risk. Thickness and edge rounding matter more.

### Cited Findings
- ANSUR II (US Army 2010-12, 1,986 women and 4,082 men), percentiles computed from the public database, 5th / 50th / 95th, in mm. Hand length: women 165/180/199, men 177/193/210. Hand breadth: women 72/78/85, men 81/88/96. Hand circumference: women 173/187/202, men 195/212/230. Palm length: women 100/108/119, men 107/116/127. The site says these agree within 1 mm of Gordon et al. 2014 (NATICK/TR-15/007). The sample is military, not the general public. — [Made Good Designs hand size chart (ANSUR II)](https://madegooddesigns.com/tools/hand-size-chart/)
- Hand dimensions have grown over time. Male 50th-percentile hand length was 183 mm in 1988 and 188 mm in 2016; breadth went from 82 to 86 mm. — [search summary of PMC table, PMC10308009](https://pmc.ncbi.nlm.nih.gov/articles/PMC10308009/table/T1) (snippet only, not fetched)
- Grip-diameter design values: power grip 30-50 mm (about 40 mm optimum); precision grip 8-16 mm (about 12 mm). The most comfortable firm-grip diameter is 19.7% of hand length (Kong and Lowe 2005), which gives about 32.5 mm for a 165 mm hand and about 41.4 mm for a 210 mm hand. — [Made Good Designs, citing CCOHS and Kong & Lowe 2005](https://madegooddesigns.com/tools/hand-size-chart/)
- Thumb length measured at about 56.5 mm (SD 4.75), with palm width about 78 mm, in a Chinese sample (Zhu & Li, Harbin). The authors note one-handed operation becomes hard on touch screens larger than 5.7". — [MATEC Conf. ICMES 2016, 09001](https://www.matec-conferences.org/articles/matecconf/pdf/2016/03/matecconf_icmes2016_09001.pdf) (via search summary)
- One unlabeled table gives a thumb length of 66.0 +/- 3.2 mm vs 59.4 +/- 2.8 mm, with hand length 181.4 vs 168.7 mm (probably male vs female, but the label is unclear). — [PMC5454107 table](https://pmc.ncbi.nlm.nih.gov/articles/PMC5454107/table/T1) (snippet only)
- Indian women (n=95): thumb-forefinger length 5th/50th/95th = 80/93/106 mm. — [Nag et al. 2003](https://www.ece.uvic.ca/~bctill/papers/mocap/Nag_etal_2003.pdf) (snippet)
- Phone width: back-of-device index-finger interaction was 12.3% more uncomfortable on a 90 mm wide device than a 60 mm one (Lee et al., Ergonomics 2016). — [UNIST ScholarWorks](https://scholarworks.unist.ac.kr/handle/201301/18907)
- In thumb tasks, performance got worse as width increased, and a wider body with a smaller bottom bezel made touch behaviour harder (Applied Ergonomics 2018, "Smartphone form factors: effects of width and bottom bezel"). — [record](https://bvbvf1.bib-bvb.de/vufind/PrimoRecord/cdi_proquest_miscellaneous_1963269489)
- A grip-comfort study (Human Factors 2019) varied height, width, thickness, edge roundness and mass together. A secondary excerpt says the most preferred size was 138 H x 70 W x 8 T mm. I could not verify this because the primary PDF returned 404. — [search result, "Determining Ergonomic Smartphone Forms With High Grip Comfort and Attractive Design"](https://scholarworks.bwise.kr/erica/bitstream/2021.sw.erica/3547/1/Determining%20Ergonomic%20Smartphone%20Forms%20With%20High%20Grip%20Comfort%20and%20Attractive%20Design.pdf)
- Reference remote: the 2021 Siri Remote is 130 x 35 x 9.3 mm and 63 g. — [Coolblue listing via search](https://coolblue.be/en/productreviews/917111). The original Siri Remote, which was thinner and smaller, was criticised because it "seemed to get lost in your hand". — [Macworld review](https://www.macworld.com/article/347504/2021-siri-remote-review-apple-tv.html)

### Inferences
- A remote is held in a flat, cradled grip: the fingers wrap the sides and back while the thumb works the front. It is not held in a cylindrical power grip. A useful check is cross-section perimeter against the comfortable firm-grip circumference, pi x 0.197 x hand length, which is about 102 mm for a 165 mm hand and about 130 mm for a 210 mm hand. For 51 x 15.8 mm with roughly 4-5 mm edge radii, the perimeter is about 125-130 mm, rising to about 135 mm where the 3 mm palm swell adds depth. That is at the large-hand end, so a 5th-percentile female hand will not close around it. That is acceptable for a remote resting on the fingers, but it argues against making the swell any thicker. 18.8 mm (15.8 + 3) is a reasonable maximum section.
- 51 mm sits between the Siri Remote (35 mm) and phones (about 70 mm). It is wide enough that the thumb travels across a 35 mm D-pad without the fingers losing their side purchase. Do not go wider.
- Rounded long edges on the back (large radius, 5-8 mm) matter more for comfort than absolute thickness, because the edges press into the finger pads and palm. The phone-form study listed edge roundness as a factor, but I could not read its result.

### Gaps
- No primary percentile table for thumb length (tip to MCP or CMC joint) was found. The best figures here are about 56-66 mm means from single-population studies. Pheasant's "Bodyspace" and NASA-STD-3000 tables were not retrieved.
- Primary Human Factors 2019 values for optimal thickness, edge radius and mass were not accessible.

## 2. Thumb reach / functional area on a held device; placement of D-pad, volume, back/home; is the top touchscreen reachable?

### Takeaway
On a hand-held device, the thumb comfortably covers a band of only about 50-60 mm tall, centred near the thumb's natural resting point. Users shift their grip to reach far zones, and the centre of the operable area is touched fastest and most accurately. On a 206 mm remote, the D-pad/OK should sit where the thumb naturally lands. Volume and back/home belong directly around it, within about 25-30 mm. A touchscreen whose zone spans 10-60 mm from the tip is roughly 50-100 mm above a D-pad at 108 mm, which is outside the comfortable one-handed thumb zone. Expect either a grip shift (slide the hand up) or a second hand.

### Cited Findings
- Hoober (2013), 1,333 field observations, of which 780 involved touching: 49% one-handed (67% right thumb), 36% cradled (two hands holding, one touching), 15% two-handed. Users shifted grip often, sometimes every few seconds, including to gain reach. — [UXmatters, "How Do Users Really Hold Mobile Devices?"](http://www.uxmatters.com/mt/archives/2013/02/how-do-users-really-hold-mobile-devices.php)
- A 2017 editor's note on that article retracts the popular "thumb zone" reach drawings. Later research found people touch the centre of the screen more often, faster and more accurately than the edges or corners. — [UXmatters (same article)](http://www.uxmatters.com/mt/archives/2013/02/how-do-users-really-hold-mobile-devices.php); see also [Hoober, "Touch Design for Mobile Interfaces"](https://smashingmagazine.com/ebooks/touch-design-for-mobile-interfaces-ebook)
- Hoober's later work replaced a single reach area with an accuracy chart that depends on grip and orientation, covering six common grips. — [CMS Conferences paper, via search](https://openaccess-api.cms-conferences.org/articles/download/978-1-964867-13-7_13)
- A replication of a tap-speed test found the centre and just below centre were fastest, with the top and bottom edges much slower (mis-hits were not recorded). — [Medium, M. Bosc](https://medium.com/@mibosc/mobile-ui-ergonomics-how-hard-is-it-really-to-tap-different-areas-of-your-phone-interface-bb043d409af8)
- CHI 2018 (RWTH, Le et al.) mapped a "comfortable area" (reachable without losing grip stability) and a "maximum range" (stretched fingers) across four phone sizes. — [RWTH PDF](https://almeida.informatik.rwth-aachen.de/publications/lahaye2019a.pdf) (fetch failed; numbers not obtained)
- Park & Han (2010, Int. J. Industrial Ergonomics) identified "good regions" for one-handed thumb touch keys on a phone. — [POSTECH record](https://remotecenter.postech.ac.kr/handle/2014.oak/26319)
- A remote-control-specific study measured palm dimensions of 22-28-year-old right-handed students. It mapped a "reachable range" and a "most comfortable range" for one-handed operation, moved the frequently used keys into the comfortable range, and reported higher efficiency (less finger travel, less time) than commercial remotes. — [EJMSTE, "Interface Design Optimization by an Improved Operating Model for College Students"](https://ejmste.com/article/interface-design-optimization-by-an-improved-operating-model-for-college-students-4788) (abstract only; the PDF could not be text-extracted)
- 2021 Siri Remote: the circular touch surface is at the top with buttons below. The asymmetric layout lets you find the top by feel. — [9to5Mac review](https://9to5mac.com/2021/06/21/review-the-new-apple-tv-remote-makes-everyone-happy/)
- Sofabaton X1S owner complaint: volume "blends in with the rest even though it is among the most-used buttons". — [AV Nirvana review](https://avnirvana.com/threads/real-world-review-the-sofabaton-x1s-smart-remote.14324)

### Inferences (geometry for this design; not sourced measurements)
- With a thumb length of about 55-65 mm, the comfortable arc is roughly 35-70 mm from the thumb's base joint. When a remote is held with the fingers wrapped behind the lower-middle section, the thumb base typically sits near one long edge, somewhere in the lower half. If the thumb tip lands naturally on OK at y ≈ 108 mm, the comfortable band is roughly y ≈ 80-140 mm, and the maximum stretch (without shifting grip) reaches about y ≈ 65-70 mm for large hands.
- Touchscreen zone (y 10-60 mm): the lower part of the screen (y ≈ 45-60) is at the limit of stretch for large hands. The upper part (y 10-40) needs a grip shift for nearly everyone. Recommendations:
  - Treat the screen mainly as a glanceable display.
  - Put any touch targets used one-handed in the bottom third of the screen, using large targets of at least 9-10 mm (see section 5).
  - Allow a slide-up grip, which needs a smooth, low-friction back below the screen and no deep finger groove that locks the hand position.
  - Alternatively, make on-screen items selectable with the D-pad, so touch is optional.
- Priority ring around OK (y ≈ 108):
  - D-pad/OK sits at the natural thumb landing point.
  - Back and Home sit immediately below or beside the ring (y ≈ 130-140). The thumb reaches them by flexing slightly, which is easier than extending.
  - Volume +/- and play/pause go next (y ≈ 135-150).
  - Rarely used keys go lowest (y > 160), near the bottom of the comfortable arc and over the battery.
- The 9 keys below the ring (8.6 mm each) probably extend to y ≈ 175-185. Keys beyond about y 160 will need thumb flexion, which is fine for a 3x3 cluster but should hold secondary functions only.
- Consider a tactile landmark on the remote's shape (see section 4) that locates the index finger so the thumb lands on OK by default.

### Gaps
- No public study gives thumb-zone coordinates in mm for a 200 mm class remote. The EJMSTE paper likely has them, but its text could not be extracted here, because no PDF tools were installed. The full text is downloadable from the EJMSTE link above for a manual read.
- Hoober's 2017+ accuracy chart values (mm of tap error by region) were not retrieved.

## 3. Balance point and weight distribution

### Takeaway
I found no measured study of centre-of-mass placement for remotes. Reviewers consistently praise heft: heavier remotes such as the 2021 Siri Remote and the Sofabaton X1S read as "solid" and "premium". For a 150-180 g remote that is much heavier than the Siri Remote (63 g) and the X1S (about 109 g listed), keep the centre of mass inside the palm/grip zone, near or slightly below the D-pad. Then the device does not tip forward when the thumb reaches up.

### Cited Findings
- 2021 Siri Remote: 63 g. Owners praise its "great button feel and weight" and say it "feels better in the hand"; one reviewer found it heavier. — [AppleInsider](https://appleinsider.com/inside/siri-remote); [Best Buy reviews](https://www.bestbuy.com/site/reviews/apple-siri-remote/6461546?page=12); [Daring Fireball](https://daringfireball.net/2021/05/the_new_siri_remote_etc)
- Sofabaton X1S: about 109 g per a retailer listing. Owners call it "beefy, solid, stable in your hand", and one reviewer said it "feels good in your hand". A former Harmony owner complained about the Harmony's "cheap plastic feel". — [AV Nirvana review](https://avnirvana.com/threads/real-world-review-the-sofabaton-x1s-smart-remote.14324); [HomeTechHacker](https://hometechhacker.com/sofabaton-x1s-replace-your-harmony-remote/)
- The Human Factors 2019 phone-form study included mass as a grip-comfort factor. Its result was not accessible. — [search result](https://scholarworks.bwise.kr/erica/bitstream/2021.sw.erica/3547/1/Determining%20Ergonomic%20Smartphone%20Forms%20With%20High%20Grip%20Comfort%20and%20Attractive%20Design.pdf)

### Inferences
- Rough centre-of-mass estimate for this design, with assumed masses:
  - LiPo: about 55 g, centred around y ≈ 145-150 mm if it spans y ≈ 95-200 under the lower keys.
  - Display module plus glass: about 15 g at y ≈ 35.
  - Shell, PCB and keys: about 80 g, centred near y ≈ 103.
  - Result: the centre of mass is about (55x148 + 15x35 + 80x103)/150 ≈ 113 mm from the tip, close to the D-pad and slightly below it.
- That position is favourable. The grip (fingers behind y ≈ 100-170) brackets the centre of mass, so the remote neither noses forward (screen-heavy) nor butt-drags. Putting the battery low is good. Moving it higher would shift the centre of mass toward the screen, and the remote would tip forward when the thumb stretches up.
- 150-180 g is about the weight of a phone, which people routinely hold one-handed, but it is 2.5x a Siri Remote. Reviews suggest heft reads as quality, but to limit fatigue in long sessions, aim toward 150 g. Avoid a top-heavy layout above all, because torque about the grip matters more than total mass.

### Gaps
- No quantitative study of remote or handheld centre-of-mass preference was found. Moment-of-inertia and tipping-torque thresholds for one-handed devices would need human-factors literature that was not retrieved, such as tool-handle balance studies.

## 4. Back contours: palm swells, finger rests, tapered or curved back, side profile, anti-roll

### Takeaway
Successful remotes use a rounded or curved back with a flat or crisp front. Apple prototyped a shallow oval index-finger indent on the 2021 Siri Remote but shipped it with a smooth rounded back. Reviewers say the combination of sharp front edges and a rounded backplate makes it feel grippier. The proposed 3 mm palm swell is consistent with this, as long as the remote still rests stably on a table.

### Cited Findings
- 2021 Siri Remote: "sharp edges paired with a rounded backplate", which AppleInsider says feels grippier. The 2021 model is thicker and longer than the 2015 model. The old model's symmetry meant people often held it upside down. — [AppleInsider](https://appleinsider.com/inside/siri-remote); [Macworld](https://www.macworld.com/article/347504/2021-siri-remote-review-apple-tv.html)
- FCC filings for the 2021 Siri Remote showed a shallow, oval-shaped finger-rest indent on the back above the Apple logo. It was removed before launch, and the shipping remote has a smooth back. — [MacRumors, "The 2021 Siri Remote Almost Had a Finger Rest"](https://macrumors.com/2022/10/03/2021-siri-remote-finger-rest)
- MIL-STD-1472D (excerpt): control surfaces should be concave to suit the finger or, if that is impractical, high-friction to prevent slipping. — [Human Engineering Design Data Digest (Scribd)](https://www.scribd.com/document/328391877/Human-Engineering-Design-Data-Digest) (snippet)

### Inferences
- Put the 3 mm palm swell where the palm and finger roots bear: the lower-middle, about y ≈ 110-180 (over the battery). Blend it with a long, gentle radius into the thinner tip region. This raises the tip, where the screen is, slightly toward the user. It also makes the remote asymmetric front-to-back and top-to-bottom, so orientation can be found by feel, which addresses Apple's "held upside down" problem.
- If an index-finger rest or groove is used, keep it shallow (≤ 1-1.5 mm) and centred behind the D-pad (y ≈ 95-115) so it registers the hand with the thumb on OK. Apple's decision to drop the indent suggests deep grooves fight the grip variety Hoober observed. A shallow one locates the hand without locking it, which matters because the screen needs a slide-up grip.
- Table stability: if the back is curved, it needs a flat land or two feet at least about 30 mm apart, or one long flat strip. Otherwise the remote rocks or spins when the screen or keys are pressed on a table. A swell only on the lower section makes it rest tip-down at a slight angle. Check that pressing the top of the touchscreen while it lies flat does not lever the tip up; a small foot or flat near the tip fixes that.
- Front-edge treatment: a crisp but not sharp front perimeter (about 0.5-1 mm radius) with large back radii follows the Siri Remote formula that reviewers liked.

### Gaps
- No measured back-profile data (swell height, radii) was found for Harmony, Sofabaton, Google TV or Siri remotes. Only reviewer impressions were available. The Google TV (Chromecast) remote's pebble shape was not researched within the budget.

## 5. Tactile key differentiation and blind operation: spacing, height/travel, cap shape, nubs, group shapes

### Takeaway
Thumb targets should be about 9-10 mm. The proposed 8.6 mm keys are slightly under the measured threshold for one-handed thumb accuracy, but they are acceptable for physical keys that the thumb can feel. Keep generous gaps, roughly 3-4 mm or more edge to edge (about 12-13 mm centre to centre). Use concave caps or high-friction caps. Make the most-used keys findable by feel through shape, size, height or position, not label alone.

### Cited Findings
- One-handed thumb target size: 9.2 mm for discrete taps and 9.6 mm for serial tasks "should be sufficiently large" (Parhi, Karlson & Bederson, MobileHCI 2006). — [Microsoft Research](https://www.microsoft.com/en-us/research/?p=155150)
- Small touch buttons raise thumb muscle effort, and "use of small touch buttons should be minimised for better thumb performance" (Xiong & Muraki, Ergonomics). — via search summary of [Park & Han / related results](https://remotecenter.postech.ac.kr/handle/2014.oak/26319)
- NRC review guidance recommends a 10 mm minimum diameter for fingertip-operated round pushbuttons, and a 2019 comment proposed 6 mm. — [NRC ML19092A160](https://www.nrc.gov/docs/ML1909/ML19092A160.pdf) (snippet)
- US Access Board research: button-array spacing is at least 18 mm (0.7 in), centre of one button to the nearest edge of the next. This is an accessibility (ADA kiosk) value, not a consumer handheld value. — [Access Board figure](https://webarchive.library.unt.edu/eot2008/20090813055724/http:/access-board.gov/research/HandsOnArch/figures/a1fig9.htm)
- MIL-STD-1472: pushbutton surfaces should be concave (or high-friction). — [Design Data Digest (Scribd)](https://www.scribd.com/document/328391877/Human-Engineering-Design-Data-Digest); the bare-finger separation for connectors (not buttons) is 25 mm. — [Eng-Tips thread, secondhand](https://eng-tips.com/threads/mil-spec.241607)
- Sofabaton X1S users complained that volume blends in with the other keys. — [AV Nirvana](https://avnirvana.com/threads/real-world-review-the-sofabaton-x1s-smart-remote.14324)
- Siri Remote: the asymmetric layout (round pad on top, buttons below) lets you orient by feel. — [9to5Mac](https://9to5mac.com/2021/06/21/review-the-new-apple-tv-remote-makes-everyone-happy/)

### Inferences
- 8.6 mm round keys are about 0.6-1 mm under the 9.2-9.6 mm thumb-target guidance, which comes from touchscreens. Physical keys with edges and travel give tactile confirmation, so 8.6 mm is workable. Compensate with a pitch of at least 12-13 mm (3.5-4.5 mm gaps) so a 15-20 mm thumb pad does not hit two keys at once. A 3-column row of 8.6 mm keys at 13 mm pitch spans 34.6 mm, which fits the 51 mm width with about 8 mm side margins.
- Grouping for blind use:
  - Give the D-pad ring a raised rim or a different texture from OK. A slightly concave or flush OK inside a raised ring makes the centre findable.
  - Make volume a distinct shape, such as an elongated rocker or a pair of keys with a nub on "+", or put it in a fixed position next to the ring. Do not make it one of nine identical round keys.
  - Use a small raised dot (a home nub, about 0.5 mm) on the single most-used key below the ring, by analogy with the F/J and keypad-5 convention.
  - Make keys in different groups differ in height or cap profile: concave for primary keys, flat or domed for secondary ones.
- Travel and force: no sourced value was found here for handheld remote keys. Typical silicone-dome remote keys are roughly 0.8-1.5 mm travel at about 1-2 N. This is common industry practice, not verified in this research.

### Gaps
- MIL-STD-1472 pushbutton diameter, displacement and resistance tables, and edge-to-edge separation values, were not retrieved. The DoD HFE TAG digest lists the section, but the numbers did not appear in snippets. ISO 9241-410 key-spacing values were not retrieved.
- No study on the ideal height difference between key groups for tactile discrimination was found.

## 6. Academic/HCI studies on remote control ergonomics

### Takeaway
The literature that applies directly to remotes is thin. The closest remote-specific study is the EJMSTE thumb-zone layout optimisation (reachable vs comfortable zones, frequent keys moved into the comfortable zone). Most quantitative guidance has to be borrowed from one-handed phone research: Hoober, Parhi et al. 2006, Park & Han 2010, Lee et al. 2016, Applied Ergonomics 2018, CHI 2018 and Human Factors 2019.

### Cited Findings
- EJMSTE remote layout optimisation (Taiwan, thu.edu.tw): measured palm dimensions, defined reachable (blue) and comfortable (green) zones for right-hand one-handed use, and reported fewer finger movements and shorter time after optimisation. — [EJMSTE article](https://ejmste.com/article/interface-design-optimization-by-an-improved-operating-model-for-college-students-4788)
- Industry view: "Button location and button size are the essential ingredients that determine usability" (URC and other manufacturers). — [Residential Systems](https://www.residentialsystems.com/?p=35700)
- Phone studies listed in sections 1, 2 and 5: [Parhi et al. 2006](https://www.microsoft.com/en-us/research/?p=155150), [Park & Han 2010](https://remotecenter.postech.ac.kr/handle/2014.oak/26319), [Lee et al. 2016](https://scholarworks.unist.ac.kr/handle/201301/18907), [Hoober 2013/2017](http://www.uxmatters.com/mt/archives/2013/02/how-do-users-really-hold-mobile-devices.php)

### Inferences
- The most transferable principles are:
  1. Put the most-used controls at the thumb's natural landing point, which on a remote is defined by the hand's resting grip, not by the device's centre.
  2. Centre placement beats edge placement for speed and accuracy.
  3. Users shift grip freely, so the shape should allow sliding rather than lock the hand.
  4. Physical asymmetry helps people orient the remote by feel.

### Gaps
- No peer-reviewed study of TV remote mass, centre of mass, or back-shape preference was found. No study of a touchscreen-plus-physical-key hybrid remote (Harmony One/Elite class) was found.
- The EJMSTE paper's numbers, and possibly older 1990s-2000s human-factors papers on VCR/TV remotes, were not reached within the tool budget.
