"""Illustration choices and explicit, playful bird collecting sets.

These are collection themes, not taxonomic families (long-tailed tits, for
example, join the tit collection). Scientific names keep membership stable.
"""
from chirpecho.chirp.catalogue import SPECIES as BIRDS
from chirpecho.web.portraits import profile

# Each group is an explicit checklist, never a substring match on a bird name.
BIRD_COLLECTIONS = (
    ('tit-club', 'The tit club', 'Collect all six tits in this set, including the long-tailed tit.',
     ('Parus major', 'Cyanistes caeruleus', 'Periparus ater', 'Poecile palustris', 'Aegithalos caudatus', 'Lophophanes cristatus')),
    ('goose-parade', 'Goose parade', 'Collect the greylag, Canada, greater white-fronted, pink-footed, tundra bean, brent, barnacle and Egyptian goose.',
     ('Anser anser', 'Branta canadensis', 'Anser albifrons', 'Anser brachyrhynchus', 'Anser serrirostris', 'Branta bernicla', 'Branta leucopsis', 'Alopochen aegyptiaca')),
    ('owl-patrol', 'Owl patrol', 'Collect the tawny, little, long-eared and barn owl.',
     ('Strix aluco', 'Athene noctua', 'Asio otus', 'Tyto alba')),
    ('crow-crew', 'The crow crew', 'Collect the magpie, jackdaw, carrion crow, rook and jay.',
     ('Pica pica', 'Corvus monedula', 'Corvus corone', 'Corvus frugilegus', 'Garrulus glandarius')),
    ('woodpecker-duo', 'Knock knock!', 'Collect the great spotted, green and black woodpecker.',
     ('Dendrocopos major', 'Picus viridis', 'Dryocopus martius')),
    ('finch-party', 'Finch party', 'Collect the chaffinch, greenfinch, goldfinch, bullfinch, hawfinch and linnet.',
     ('Fringilla coelebs', 'Chloris chloris', 'Carduelis carduelis', 'Pyrrhula pyrrhula', 'Coccothraustes coccothraustes', 'Linaria cannabina')),
    ('thrush-choir', 'The thrush choir', 'Collect the blackbird, song thrush, mistle thrush, redwing and fieldfare.',
     ('Turdus merula', 'Turdus philomelos', 'Turdus viscivorus', 'Turdus iliacus', 'Turdus pilaris')),
    ('birds-of-prey', 'Lords of the sky', 'Collect all eight daytime birds of prey in this set.',
     ('Buteo buteo', 'Falco tinnunculus', 'Accipiter nisus', 'Haliaeetus albicilla', 'Pernis apivorus', 'Circus aeruginosus', 'Circus cyaneus', 'Milvus milvus')),
    ('pigeon-post', 'Pigeon post', 'Collect the wood pigeon, rock pigeon, stock dove and collared dove.',
     ('Columba palumbus', 'Columba livia', 'Columba oenas', 'Streptopelia decaocto')),
    ('sparrow-pals', 'Sparrow pals', 'Collect the house sparrow and tree sparrow.',
     ('Passer domesticus', 'Passer montanus')),
    ('waterfront', 'By the water', 'Collect the mallard, grey heron, night heron, moorhen, coot, mute swan, whooper swan, white stork, black stork, kingfisher, crane, lapwing, cormorant and great egret.',
     ('Anas platyrhynchos', 'Ardea cinerea', 'Nycticorax nycticorax', 'Gallinula chloropus', 'Fulica atra', 'Cygnus olor', 'Cygnus cygnus', 'Ciconia ciconia', 'Ciconia nigra', 'Alcedo atthis', 'Grus grus', 'Vanellus vanellus', 'Phalacrocorax carbo', 'Ardea alba')),
    ('sky-acrobats', 'Sky acrobats', 'Collect the swift, barn swallow, house martin, common tern, bee-eater and nightjar.',
     ('Apus apus', 'Hirundo rustica', 'Delichon urbicum', 'Sterna hirundo', 'Merops apiaster', 'Caprimulgus europaeus')),
    ('colourful-hunters', 'Flying colours', 'Collect the kingfisher, roller, bee-eater and bluethroat.',
     ('Alcedo atthis', 'Coracias garrulus', 'Merops apiaster', 'Luscinia svecica')),
    ('field-singers', 'Songs over the fields', 'Collect the skylark, woodlark, tree pipit and meadow pipit.',
     ('Alauda arvensis', 'Lullula arborea', 'Anthus trivialis', 'Anthus pratensis')),
    ('duck-pond', 'Duck pond', 'Collect the mallard, tufted duck and gadwall.',
     ('Anas platyrhynchos', 'Aythya fuligula', 'Mareca strepera')),
    ('red-tail-duo', 'Rusty tails', 'Collect the bluethroat and black redstart.',
     ('Luscinia svecica', 'Phoenicurus ochruros')),
    ('scrub-singers', 'Hedgerow voices', 'Collect the blackcap and common whitethroat.',
     ('Sylvia atricapilla', 'Curruca communis')),
    ('leaf-warblers', 'Songs in the leaves', 'Collect the chiffchaff, willow warbler and wood warbler.',
     ('Phylloscopus collybita', 'Phylloscopus trochilus', 'Phylloscopus sibilatrix')),
)


def artwork(*names):
    """Reuse the collection's original full-colour, versioned portraits."""
    bird_names = {item['scientific'] for item in BIRDS}
    return [profile(name, name in bird_names) for name in names]

# Only species supported by the bundled bat classifier are achievement targets.
BAT_COLLECTIONS = (
    ('pipistrelle-trio', 'The pipistrelle trio', 'Collect the common, soprano and Nathusius’ pipistrelle.',
     ('Pipistrellus pipistrellus', 'Pipistrellus pygmaeus', 'Pipistrellus nathusii')),
    ('open-air-hunters', 'Above the treetops', 'Collect the noctule, Leisler’s bat and serotine.',
     ('Nyctalus noctula', 'Nyctalus leisleri', 'Eptesicus serotinus')),
    ('myotis-club', 'The Myotis club', 'Collect all six supported mouse-eared bats in this set.',
     ('Myotis daubentonii', 'Myotis nattereri', 'Myotis mystacinus', 'Myotis brandtii', 'Myotis alcathoe', 'Myotis bechsteinii')),
    ('long-ears', 'All ears', 'Collect the brown and grey long-eared bat.',
     ('Plecotus auritus', 'Plecotus austriacus')),
    ('horseshoe-duo', 'Lucky horseshoes', 'Collect the greater and lesser horseshoe bat.',
     ('Rhinolophus ferrumequinum', 'Rhinolophus hipposideros')),
)
