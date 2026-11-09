"""Species-specific illustration recipes and original field notes.

Colours depict a representative adult plumage; sexes and seasons vary.
"""
# Body, breast, wing, bill, shape, markings, original field note.
BIRD_ART = [
('292d32','34363b','20262c','efa731','song','eye-ring','The garden flautist. A male wears coal-black feathers and a golden bill; females are brown. Listen for flowing phrases from a favourite rooftop.'),
('89734e','e77b42','705c41','453b32','round','orange-face','A small guardian with a bright orange face and breast. It watches for worms and insects, and sings even through the colder months.'),
('303936','e6d14e','788457','373b34','tit','bib','A bold woodland acrobat with white cheeks, a black cap and a dark stripe down its yellow belly. Its ringing song often sounds like a repeated two-note phrase.'),
('5296c5','eddb68','397db2','34414a','tit','blue-mask','A tiny canopy explorer in blue, yellow and white. It hangs upside down to inspect twigs for insects and readily visits garden feeders.'),
('9c7955','c9b797','775639','655345','round','sparrow','A sociable neighbour of houses and hedges. Males have a grey crown and black bib; this seed eater often gathers in chattering groups.'),
('a76b43','dac9a8','785239','594c40','round','cheek-spot','A chestnut-capped sparrow with a black spot on each pale cheek. It favours hedgerows, farmland and the edges of villages.'),
('708398','c78978','404b50','a99885','finch','wingbars','A woodland singer with a descending flourish. Males show a blue-grey crown and pinkish breast, with bright white bars flashing across the wings.'),
('879649','a9b85a','617443','c2ac86','finch','yellow-wing','An olive-green seed cracker with a chunky bill. Yellow edges flash along its wings and tail as it flies between hedges and feeders.'),
('ad885a','e7d2ab','303737','d7b897','finch','red-mask','A thistle specialist dressed in red, black and gold. Its fine bill extracts small seeds, while a broad yellow wing stripe shines in flight.'),
('8e795f','92989a','6f5b44','514c43','song','streaks','A quiet hedge wanderer with a slate-grey face and finely streaked brown back. It searches the ground for small insects beneath cover.'),
('9b6f45','c39a6c','785332','594132','wren','bars','A tiny bird with a proudly cocked tail and a surprisingly powerful song. It slips through tangled vegetation in search of insects.'),
('374343','484b49','283b3e','e3b049','song','speckles','An iridescent flock dancer. Its plumage gleams green and purple, winter feathers carry pale spots, and its repertoire includes skilful imitations.'),
('253d45','eee9dc','316d73','333c42','longtail','white-shoulder','A black-and-white collector with a long, shimmering tail. It builds a large twig nest and explores lawns, fields and gardens for food.'),
('454c54','4d555e','303943','30343b','crow','grey-nape','A compact crow with a silver-grey nape and pale eyes. It lives socially and often nests in cavities, chimneys and old buildings.'),
('252c33','2e343c','1d242b','30343a','crow','black','An all-black problem solver with a strong bill. It searches open ground for varied food and often patrols its territory in a pair.'),
('30323b','393c45','242730','a9aaa0','crow','bare-face','A farmland crow with a pale bare patch around the bill in adults. Rooks nest together in noisy treetop colonies called rookeries.'),
('b99082','d5b3a1','5b463d','393936','crow','jay-blue','A woodland gardener with a pinkish-brown coat and a vivid blue wing panel. Buried acorns can grow into the next generation of oak trees.'),
('82909c','c5a6b6','667986','e0ad75','pigeon','neck-white','A large pigeon with a soft pink breast, white neck patches and bold white wing flashes. Its deep cooing is a familiar woodland soundtrack.'),
('7d91a2','abb2bd','596d81','777279','pigeon','pigeon-bars','A cliff nester whose descendants thrive in towns. The classic plumage has two dark wing bars and a neck that glints green and purple.'),
('b7ab99','d4c5b4','988e80','51463f','pigeon','collar','A pale dove wearing a fine black half-collar. Its repeated three-part coo carries across gardens, farms and quiet streets.'),
('2d3338','f0e7d6','242b32','575c59','woodpecker','woodpecker','A black-and-white tree drummer with a red patch beneath the tail. Its strong bill chisels wood and its stiff tail braces against trunks.'),
('81934d','bcc785','5c793c','6f7461','woodpecker','red-cap','A green-backed woodpecker with a red crown and a laughing call. It spends much of its feeding time on the ground looking for ants.'),
('6b8fa6','d6a16b','52748a','555e64','song','eye-stripe','A blue-grey climber with a warm buff belly and a dark eye stripe. It can walk headfirst down trunks while probing crevices for food.'),
('947a58','eee5ce','755c40','89775a','climber','treecreeper','A bark-patterned climber with a pale belly and a curved bill. It spirals up trunks, using its stiff tail as a prop.'),
('d6c6c0','f1e8dd','343b3f','393c40','longtail','pink','A tiny feather ball with a tail longer than its body. Family parties travel together through trees, calling softly as they forage.'),
('343b3c','d5c5a8','697b82','3e4546','tit','nape-white','A small conifer visitor with a black cap, white cheeks and a white nape patch. It often carries seeds away to hide them for later.'),
('8b7e68','d7cbb4','6b6459','3e3d38','tit','cap','A neat black-capped woodland bird with pale cheeks and a small bib. It stores food and often stays close to its home woodland.'),
('8b9a53','d8d1a2','596e45','4f493b','tiny','gold-crown','A miniature conifer explorer with a golden crown bordered in black. Its very fine bill picks tiny prey from needles and twigs.'),
('9b7e59','ead8b6','795e40','8e795c','song','spots','A brown-backed singer with a cream breast dotted in dark arrowheads. It repeats short musical phrases and may break snail shells on a stone.'),
('9d9480','eee4cb','7f7968','9d8a66','thrush','large-spots','A sturdy thrush with bold round breast spots. It sings from exposed treetops and can vigorously defend a berry-laden tree.'),
('8b765b','e6d7bc','6d5944','bc9b62','thrush','red-flank','A winter visitor with a cream eyebrow and rusty-red flanks. It searches fields and berry bushes, sometimes travelling on clear nights.'),
('87919b','e1c18a','947455','dab24c','thrush','grey-head','A colourful thrush with a grey head, chestnut back and spotted breast. Winter flocks descend on fields, orchards and berry-bearing trees.'),
('99988a','d2cfc0','7e8071','53564f','song','blackcap','A grey woodland singer with a neat cap: black in males, warm brown in females. Its rich song can pour from deep inside leafy cover.'),
('8d9661','d2ce99','6f7d48','615c42','slender','plain','An olive-brown leaf searcher named for its repeated chiff-chaff song. It flicks through foliage to catch tiny invertebrates.'),
('a0aa6b','e1db9d','7c8d50','a29162','slender','eyebrow','A light-footed migrant with a pale eyebrow and a soft yellowish wash. Its song tumbles down in a gentle cascade.'),
('788a98','dddcd2','536d81','d5ad56','longtail','cuckoo-bars','A grey migrant with barred underparts and a long tail. The male gives the famous two-note call; females lay eggs in other birds’ nests.'),
('3d3935','514a41','292d31','33322f','swift','pale-throat','A dark aerial specialist with long, scythe-shaped wings. It catches insects on the wing and spends much of its life in flight.'),
('274b5c','eadbc4','203c4d','41413d','swallow','red-throat','A blue-backed insect hunter with a red throat and long forked tail. It sweeps over fields and often builds mud nests inside buildings.'),
('294d60','f4eee1','294151','41484b','swallow','white-rump','A smart blue-black flier with a bright white rump and short forked tail. It builds enclosed mud nests beneath eaves.'),
('929ca2','f0ede0','404c54','454b4b','longtail','wagtail','A slim walker in black, white and grey with a constantly bobbing tail. It chases small invertebrates across open ground and watersides.'),
('a18a61','d8c79b','806a46','9e8b65','lark','crest','A streaked field singer with a small crest. It delivers a long, bubbling song while hovering high above open farmland and grassland.'),
('78563e','d8c3a0','59412f','cfb347','raptor','buzzard','A broad-winged hunter often seen circling above fields. Plumage ranges from very pale to dark brown; it watches for prey from convenient perches.'),
('b37c4c','ead4a4','785843','a6a093','raptor','kestrel','A russet-backed falcon with dark spotting. It can hover facing into the wind while scanning rough grass for small mammals.'),
('96704c','d8c19d','725137','d2ad62','owl','owl-brown','A round-headed woodland owl with dark eyes and mottled brown plumage. Its familiar night-time duet belongs to two birds calling to each other.'),
('9c8a65','e5d6ae','786847','ccb75d','owl','owl-white','A compact owl with a stern expression and bright yellow eyes. It watches from posts and branches for insects and other small prey.'),
('a78050','e1bf88','6f5136','b9a16b','owl','ear-tufts','A slender owl with long ear tufts and orange eyes. It hunts open ground and may gather in shared winter roosts.'),
('d9ba86','fff0d4','b18e5d','e2c6a0','owl','heart-face','A pale night hunter with a heart-shaped face. It quarters grassland on quiet wings, listening for small mammals beneath the vegetation.'),
('748654','c7b9a3','8a8172','dcbb4d','duck','mallard','A familiar dabbling duck of ponds and wetlands. A breeding male has a green head and chestnut breast; females wear mottled brown camouflage.'),
('92a0aa','e7e4d8','6f8596','dab064','heron','heron','A tall water-edge hunter with long legs and a dagger-like bill. It waits patiently before striking at fish and other small prey.'),
('3d4440','4b4c43','695844','ce4b38','waterhen','moorhen','A dark wetland walker with a red bill tipped yellow. It picks its way around reeds on long toes and flashes white undertail feathers.'),
('343b40','444d50','30383e','f1eade','waterhen','coot','A charcoal-coloured swimmer with a white bill and forehead shield. Broad lobes on its toes help it paddle through open water.'),
('b6bdc1','f3f0e7','8a9ba8','dfb54a','gull','gull-grey','A large coastal gull with a grey back and pink legs in adults. Young birds start mottled brown and take several years to reach adult plumage.'),
('a8b2b6','f6f0e2','8e9da9','ae4b3b','gull','gull-hood','A lively smaller gull with a chocolate-brown hood in breeding season. In winter a dark ear spot remains on its otherwise white head.'),
('a99b81','d5c9b0','837861','e6a264','goose','goose-bars','A sturdy grey goose with an orange bill. It grazes in fields and wetlands, often travelling with a vocal family group.'),
('857c67','d6c8a7','625f53','383d3c','goose','canada','A large goose with a black head and neck crossed by a white chinstrap. It grazes beside lakes and often flies in a V-shaped flock.'),
('eeeade','fff9ee','d7d8d0','e49447','swan','swan','A graceful white waterbird with a long curved neck. Adults have an orange bill with a black base; young swans begin grey-brown.'),
]
# Body, belly, wing, ear length, wing reach, head width, feature.
BIRD_ART.extend([('657887', 'e4cbb0', '485e70', '37414a', 'raptor', 'kestrel', 'A woodland ambush hunter with short rounded wings and a very long barred tail. Adult males show slate-grey upperparts, orange-barred underparts and bright yellow eyes.'), ('889195', 'db7d81', '313b42', '30343a', 'finch', 'cap', 'A quiet seed eater with a sturdy build. Males wear a black cap and face, coral-pink breast, grey back, white rump and a short deep black bill.'), ('b39558', 'ead864', '826745', '9c987d', 'finch', 'streaks', 'A bright farmland singer. Males have a lemon-yellow head and breast, streaked chestnut-brown back, rusty rump and a long tail with white outer edges.'), ('a77c55', 'd4bc98', '4e4a41', '899395', 'finch', 'bib', 'A powerful seed cracker with an enormous deep conical bill. Its warm chestnut head, black face and bib, buff body, grey nape and broad white wing patches make a striking combination.'), ('e9e7db', 'f1eee1', '303b43', 'c15c48', 'heron', 'white', 'A tall white wading bird with black flight feathers, a very long straight red bill and long red legs. It often soars on broad wings and clatters its bill at the nest.'), ('88915b', 'e9d656', '525e49', '39423b', 'longtail', 'grey-head', 'A slender yellow-bellied bird of damp meadows and farmland. A representative male shows a blue-grey head, olive back, bright yellow underparts and a long dark tail with white edges.'), ('9c7459', 'c98583', '514e44', '515853', 'finch', 'red-mask', 'A small lively finch of hedges and open ground. Breeding males have a grey head, crimson forehead and breast, warm chestnut back and fine dark bill; white wing and tail edges flash in flight.'), ('84939b', 'b8a8aa', '627781', 'a38e79', 'pigeon', 'pigeon-bars', 'A compact blue-grey pigeon with a glossy green neck patch, dark eyes and two short dark wing bars. It lacks the white neck and wing patches of a wood pigeon and often nests in tree cavities.')])

BIRD_ART.extend([('695e48', '968269', '443f35', 'd8b447', 'raptor', 'kestrel', 'A huge sea eagle with broad fingered wings, a short wedge-shaped white tail, a pale buff head and a massive yellow hooked bill. Adults have dark brown bodies and powerful yellow feet.'), ('348d9c', 'd58243', '28677f', '343e42', 'song', 'orange-face', 'A compact waterside jewel with vivid turquoise-blue back and wings, an orange breast, white throat and cheek patch, short tail, tiny red feet and a long straight black dagger-like bill.'), ('b9c3c7', 'eeeee5', '7b8c99', 'bd5547', 'gull', 'black-cap', 'A slender seabird with pale grey upperparts, white underside, a black cap, red legs and a narrow red bill with a black tip. Long pointed wings and a deeply forked tail support agile flight above water.'), ('80715c', 'd8cdb4', '5f584b', '414849', 'raptor', 'kestrel', 'A woodland raptor with a small pigeon-like grey head, slender neck, long barred tail and broad wings. A representative male has brown upperparts, pale barred underside, yellow eyes and a dark bill.'), ('68543d', 'a28d65', '4c4439', '424949', 'raptor', 'kestrel', 'A long-winged wetland raptor with a long tail and yellow legs. A representative adult female is chocolate brown with a contrasting creamy crown, throat and shoulder patches; wings are held in a shallow V when gliding.')])

BIRD_ART.append(('80715e', 'c5b9a5', '574e43', 'e39b91', 'goose', 'white-front', 'A grey-brown goose with a white patch around the pink bill and bold black bars across the adult belly. Orange feet carry it across open grasslands, where flocks gather in winter.'))

BAT_ART = [
('76503c','b89770','56463f',16,105,23,'pip'),
('a8734d','d8b38d','665047',15,100,21,'soprano'),
('79563f','c2a785','544942',18,110,24,'nathusius'),
('a66a39','c79b60','5e4032',14,125,29,'noctule'),
('77513a','b49169','513f36',17,120,26,'mane'),
('644b39','bb9d72','423b35',20,117,30,'serotine'),
('8a7159','e5dcc6','685b50',22,101,23,'feet'),
('94836b','eee5d4','716351',26,102,24,'fringe'),
('584838','a29379','4a4038',21,97,21,'whiskers'),
('927249','c7ac7f','65503e',23,99,22,'brandt'),
('a57a50','cdb18a','71604e',19,92,20,'alcathoe'),
('9b7d59','e0cdb0','74624e',39,104,25,'bechstein'),
('957453','d7bd99','75604d',57,108,24,'long-brown'),
('7f7c77','d9d7ce','626267',54,111,26,'long-grey'),
('424449','9c9e9b','33363b',27,109,28,'joined'),
('aa8059','d6b995','77614f',24,115,29,'horseshoe'),
('9e805c','d8c3a0','6d5c48',22,94,21,'lesser'),
('a59172','eee2c9','81725b',32,124,32,'mouse'),
('817361','e4dfce','615a51',25,113,27,'pond'),
('676360','c8c6bf','45454a',17,118,27,'silver'),
('b17f59','d9b58e','80604a',28,106,24,'notch'),
('987049','cfb38e','66503e',18,107,22,'margin'),
('756044','c6b28a','48443e',16,112,25,'savi'),
('938474','cec1ac','615c57',13,128,23,'bent'),
]

BIRD_ART.append(('92918a', 'd2c6b4', '777970', '333137', 'goose', 'pink-footed', 'A compact goose with a dark brown head and neck, pale grey back, pink feet and a short dark bill with a pink band. Winter flocks graze in open fields and grasslands.'))

BIRD_ART.extend([
('a7adb4', 'eeeeea', '202931', '343b40', 'heron', 'night-heron', 'A stocky heron with a black crown and back, grey wings, white underside and red eyes. Adults have slender white nape plumes and hunt along water edges at dusk and at night.'),
('877665', 'cbbca6', '514538', '343137', 'goose', 'tundra-bean', 'A brown-grey goose with a dark head and neck, orange legs and a short stout black bill with an orange band. Winter flocks graze on grasslands and fields.'),
])

BIRD_ART.extend([('39b9cc', '55cbd1', '2769ac', '343b40', 'song', 'plain', 'A colourful bird with a turquoise head and belly, chestnut back and deep blue wings. It watches from exposed perches for large insects on open ground.'), ('ae7743', '43b9be', '549966', '333b3c', 'longtail', 'eye-stripe', 'A slender aerial insect hunter with a chestnut crown and back, yellow throat, turquoise belly and black eye stripe. Its long curved bill catches flying insects.'), ('263f40', 'f2eee3', '223238', 'c54e42', 'heron', 'black', 'A large shy bird with a glossy black head, neck and wings, white belly and red bill and legs. It feeds in shallow water and nests in quiet forests.')])

BIRD_ART.extend([
('999fa2', 'b7babc', '596166', '9b946c', 'heron', 'plain', 'Tall grey crane with long dark legs, black face and neck, white stripe behind the eye down the neck, red crown patch and drooping dark tail-like tertial feathers.'),
('827363', 'c1b19a', '514c46', '373b38', 'swift', 'plain', 'Mottled grey-brown cryptic plumage, large dark eyes, tiny bill with wide gape, long folded wings and long barred tail, short legs.'),
('282e32', '353c40', '20272c', 'c9bf9b', 'woodpecker', 'plain', 'Large entirely black woodpecker, adult male with full bright red crown, pale eyes, long pale ivory pointed bill, stiff tail and strong grasping feet.'),
('8e795c', 'e7d7bf', '6d604c', '373d3d', 'song', 'plain', 'Adult male white-spotted bluethroat, brilliant blue throat with small white central spot, black and chestnut breast bands, brown back, cream eyebrow, rusty patches at tail base.'),
('9faeb7', 'ecede7', '627580', '333c43', 'raptor', 'plain', 'Adult male Hen Harrier, pale blue-grey head and back, white underside, yellow eyes and legs, dark hooked bill, long wings with black tips, long barred tail and white rump.'),
('9e8663', 'e8d8b8', '756145', 'a89679', 'slender', 'plain', 'Slim brown Tree Pipit, strongly streaked warm buff breast, finer streaks on flanks, pale belly, cream eyebrow, pinkish legs and relatively short curved hind claw.'),
('335d5b', 'f0eee3', '2a4645', '343b3d', 'waterhen', 'plain', 'Northern Lapwing with long fine upward black crest, metallic green and purple back, black breast and face markings, white belly, pink legs and short dark bill.'),
('a96a43', 'c58e65', '5d4434', 'b9aa75', 'raptor', 'plain', 'Red Kite with pale grey streaked head, rusty red-brown body, dark folded wings, yellow eyes and feet, hooked bill, very long deeply forked rusty tail fully visible.'),
('928367', 'dfd3b8', '6e604a', '9f9075', 'slender', 'plain', 'Meadow Pipit, olive-brown streaked upperparts, pale buff breast and belly with dark streaks continuing boldly down flanks, thin bill, pinkish legs and long slender hind claw.'),
('9f8663', 'e2d0ad', '766047', 'a28c6d', 'lark', 'plain', 'Small compact Woodlark, brown streaked plumage, bold cream eyebrows meeting behind head, short crest, short tail, buff streaked breast, black-and-white marking on folded wing edge.'),
('655f55', '8d887c', '45453f', '303534', 'goose', 'plain', 'Dark-bellied Brent Goose, compact goose with black head neck and breast, small white patch on each side of neck, dark grey-brown body, white undertail, black bill and black webbed feet.'),
('939b9d', 'e4e4dc', '515c64', '303738', 'goose', 'plain', 'Barnacle Goose, white face contrasting with black crown neck and breast, silver-grey back with black-and-white barred wings, pale belly, short black bill and black webbed feet.'),
])

BIRD_ART.extend([
('293239', 'eeeeea', '242b30', '8796a0', 'duck', 'plain', 'Adult male Tufted Duck with glossy black head breast and back, clean white flanks, long drooping black crest, bright yellow eyes, blue-grey bill with black tip and dark webbed feet.'),
('978e7a', 'ded3bb', '706957', '363b3c', 'tit', 'plain', 'Small Crested Tit, tall pointed black-and-white speckled crest, pale cheeks bordered with a black curved line, black bib, grey-brown back and buff-white belly.'),
('91a54e', 'faf5e4', '6a843d', '8c8360', 'slender', 'plain', 'Wood Warbler with bright moss-green back, lemon-yellow face throat and long eyebrow, clean white belly, dark eye stripe, long folded wings and slim fine bill.'),
('263b3c', '304140', '263136', 'a3a08b', 'heron', 'plain', 'Adult Great Cormorant, glossy black plumage with bronze scalloped wings, long neck, sturdy hooked grey bill with yellow skin at base, pale cheek and throat patches, black webbed feet and long stiff tail.'),
('8f8b7e', 'c6c3b6', '69665b', '383b37', 'duck', 'plain', 'Adult male Gadwall, finely patterned grey body, brown head with steep forehead, black rear end, dark bill, chestnut shoulder and small white wing patch visible on folded wing, orange webbed feet.'),
('a48b6b', 'd5c3a5', '73553f', 'c78379', 'goose', 'plain', 'Egyptian Goose with sandy buff head, distinct dark chocolate eye patches, dark neck ring and brown breast spot, grey-buff belly, chestnut back and folded wings with white patches, pink bill and long pink webbed feet.'),
])

BIRD_ART.append(('9a8062', 'e5d6c4', '68747c', 'b9a489', 'slender', 'plain', 'A lively hedgerow warbler with a bright white throat, grey male head, rusty wing panels and a long white-edged tail. It sings from scrub tops and makes brief fluttering song flights.'))

BIRD_ART.append(('555b60', '989b9b', '292d31', 'c97543', 'slender', 'plain', 'An alert insect hunter of rocks, rooftops and buildings. The western male has a charcoal-black face and breast, slate-grey back, pale wing panel and a vivid rusty-red tail that frequently quivers.'))

BIRD_ART.append(('eeeee9', 'ffffff', 'ccd3d7', '33393d', 'heron', 'plain', 'An elegant white heron with a long S-shaped neck, black legs and feet, and a yellow bill outside the breeding season. It stalks fish in shallow water and also hunts in wet grassland.'))
BIRD_ART.append(('eeeee9', 'ffffff', 'ccd3d7', 'e9bd37', 'swan', 'whooper', 'A large white swan with a long upright neck, black feet and a yellow-and-black bill. The yellow forms a pointed wedge extending beyond the nostril. Winter flocks graze on wet grasslands and give loud trumpeting calls.'))
