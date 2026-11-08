"""Build the checked-in, species-specific SVG field-guide collection."""
from pathlib import Path
import re
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from chirpecho.common.field_art import BIRD_ART, BAT_ART

OUT = Path(__file__).resolve().parents[1] / 'chirpecho/web/static/species'
OUT.mkdir(parents=True, exist_ok=True)


def path(d, fill, **attrs):
    extra = ' '.join(f'{key.replace("_", "-")}="{value}"' for key, value in attrs.items())
    return f'<path d="{d}" fill="{fill}" {extra}/>'


def ellipse(x,y,rx,ry,fill):
    return f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{fill}"/>'


# Body proportions vary with species build, rather than a shared songbird outline.
BIRD_BUILD = [(44,39),(34,37),(37,36),(32,33),(36,35),(34,34),(37,35),(38,36),(33,34),(33,35),(27,30),(41,37),(42,35),(44,38),(49,41),(48,40),(43,38),(52,40),(47,37),(43,34),(39,38),(43,39),(34,32),(29,34),(26,28),(29,30),(30,31),(23,26),(41,39),(46,42),(39,37),(44,40),(32,34),(28,31),(29,32),(43,36),(32,27),(30,28),(28,27),(31,30),(35,36),(51,43),(42,37),(47,42),(35,38),(41,42),(44,44),(53,33),(43,40),(42,36),(44,35),(49,34),(42,31),(55,38),(57,39),(58,35)]


BIRD_BUILD += [(43,37),(39,37),(34,35),(43,38),(44,42),(30,30),(32,33),(43,36)]

BIRD_BUILD += [(55,43),(34,34),(42,30),(48,39),(47,38)]

def eye(x, y, iris='#343c43', size=8):
    size *= .57
    return '<g data-part="eye">'+ellipse(x,y,size,size,iris)+ellipse(x,y,size*.57,size*.7,'#252c2d')+ellipse(x+size*.3,y-size*.3,.7,.7,'#e7dfcc')+'</g>'


def owl_art(row):
    body,breast,wing,bill,_,mark,_=row
    body,breast,wing,bill=['#'+c for c in (body,breast,wing,bill)]
    rx,ry=BIRD_BUILD[BIRD_ART.index(row)]
    art=[ellipse(150,128,rx,ry,body),ellipse(150,137,rx*.65,ry*.74,breast)]
    for side in (-1,1):
        x=150+side*rx*.8
        art += [path(f'M{x} 105Q{x+side*20} 142 {x-side*7} 161Q{x-side*13} 133 {x} 105Z',wing,data_part='wing')]
    if mark=='ear-tufts':
        art += [path('M121 61 115 17 142 50M158 50 185 17 179 61',body,data_part='ear-tufts')]
    art += [ellipse(150,78,42,36,body)]
    if mark=='heart-face':
        art += [path('M150 56C127 34 105 59 121 85L150 111 179 85C195 59 173 34 150 56Z','#fff5dc')]
    else:
        face='#c2a383' if mark=='owl-brown' else '#e4c797' if mark=='ear-tufts' else '#e3d8b8'
        art += [ellipse(134,81,21,25,face),ellipse(166,81,21,25,face)]
    iris='#332b29' if mark in ('owl-brown','heart-face') else '#e68b35' if mark=='ear-tufts' else '#e8cb43'
    art += [eye(134,78,iris,11),eye(166,78,iris,11)]
    if mark=='owl-white':
        art += [path('M117 61 139 66M161 66 183 61','none',stroke='#fff4d8',stroke_width=5)]
        for x,y in [(132,48),(147,44),(162,47),(176,52)]:art += [ellipse(x,y,3,2,'#f7e9c8')]
    for x,y in [(139,120),(159,126),(147,138),(163,147),(135,151)]:
        art += [path(f'm{x} {y} 3 6 3-6','none',stroke=wing,stroke_width=2)]
    art += [path('M145 94 150 106 155 94Q150 91 145 94Z',bill,data_part='beak'),path('M135 165v7m-8 2 8-3 8 3m22-9v7m-8 2 8-3 8 3','none',stroke='#b89c61',stroke_width=4,data_part='feet')]
    return ''.join(art)


def flying_bird_art(row):
    body,breast,wing,bill,shape,mark,_=row
    body,breast,wing,bill=['#'+c for c in (body,breast,wing,bill)]
    swift=shape=='swift'
    left='M139 107C115 64 68 26 22 22C73 19 119 46 151 95Z' if swift else 'M137 111 35 37Q103 45 153 101Z'
    right='M158 103C181 64 230 27 278 23C225 20 185 48 146 98Z' if swift else 'M154 105 263 38Q193 44 143 98Z'
    art=[path(left,wing,data_part='wing'),path(right,body,data_part='wing')]
    tail='M137 137 116 164 147 154 168 166 159 137Z' if mark!='red-throat' else 'M137 137 105 188 147 159 179 188 159 137Z'
    art += [path(tail,wing,data_part='tail'),ellipse(149,120,27 if swift else 29,36,body),ellipse(157,128,18,25,breast),ellipse(177,86,29,28,body)]
    if mark=='red-throat':art += [ellipse(192,100,12,12,'#b66343')]
    if mark=='white-rump':art += [path('m128 139 26 7 4 11-25-4Z','#fbf5e7')]
    if mark=='pale-throat':art += [ellipse(192,104,10,6,'#c1b49a')]
    art += [eye(190,82,'#343d45',7),path('M202 88 216 94 201 97Z',bill,data_part='beak')]
    return ''.join(art)


def waterbird_art(row):
    body,breast,wing,bill,shape,mark,_=row
    body,breast,wing,bill=['#'+c for c in (body,breast,wing,bill)]
    rx,ry=BIRD_BUILD[BIRD_ART.index(row)];ry=min(ry,33)
    tall=shape in ('swan','heron','goose')
    hx,hy=(195,47) if shape in ('heron','swan') else (190,63) if shape=='goose' else (183,84)
    head='#356d50' if mark=='mallard' else '#2b343c' if mark=='canada' else '#624636' if mark=='gull-hood' else body
    if mark=='gull-grey':head='#f8f4e8'
    feet='#a9aa79' if shape=='heron' else '#dcaa8e' if mark=='gull-grey' else '#a8b35f' if mark=='moorhen' else '#8a947c' if mark=='coot' else '#434840' if mark=='swan' else '#d98357'
    art=[path('M107 127 69 138 110 148Z',wing,data_part='tail')]
    bottom=184 if shape=='heron' else 174
    if shape in ('duck','goose','swan'):
        art += [path(f'M135 153v14l-13 8h25l-6-8m24-14v14l-9 8h25l-10-8','none',stroke=feet,stroke_width=4,data_part='feet')]
    else:
        art += [path(f'M133 151V{bottom}m-12 2 12-4 11 4m21-35v{bottom-151}m-12 2 12-4 13 4','none',stroke=feet,stroke_width=3.5,data_part='feet')]
    art += [ellipse(143,133,rx,ry,body),ellipse(156,141,rx*.67,ry*.72,breast)]
    if tall:
        neck='#2b343c' if mark=='canada' else body
        art += [path(f'M166 137C157 109 173 {hy+24} {hx-14} {hy+12}L{hx+14} {hy+11}C{hx-5} 99 184 116 193 137Z',neck,data_part='neck')]
    if mark=='mallard':art += [path('M167 111Q192 105 200 124L188 145 165 130Z','#885b43')]
    art += [path('M107 117Q87 146 130 156L168 142Q140 134 107 117Z',wing,data_part='wing')]
    if shape=='gull':art += [path('M110 142 145 154 130 158 105 148Z','#35424a')]
    if mark=='mallard':art += [path('m117 134 29 8-6 7-26-7Z','#536fa6'),path('m169 108 30 1','none',stroke='#fbf4dc',stroke_width=4)]
    if mark=='moorhen':art += [path('M119 145 155 149','none',stroke='#f2e5d6',stroke_width=3)]
    if mark=='goose-bars':art += [path('m122 124 14 5m-17 5 16 5m-14 5 13 4','none',stroke='#b4a78b',stroke_width=2)]
    art += [ellipse(hx,hy,28 if shape!='heron' else 24,27,head)]
    if mark=='canada':art += [path('M185 69Q194 83 209 68L209 79Q195 93 181 81Z','#f5eedb')]
    if shape=='heron':art += [path('M177 35 162 28 174 44','none',stroke='#33414c',stroke_width=4)]
    if shape=='duck':beak=f'M{hx+23} {hy+1}Q{hx+57} {hy-2} {hx+52} {hy+12}L{hx+22} {hy+13}Z'
    elif shape=='heron':beak=f'M{hx+21} {hy-2} 273 {hy+5} {hx+21} {hy+11}Z'
    elif shape=='waterhen':beak=f'M{hx+22} {hy-2} {hx+45} {hy+8} {hx+22} {hy+15}Z'
    else:beak=f'M{hx+23} {hy} {hx+51} {hy+4} {hx+48} {hy+14} {hx+23} {hy+12}Z'
    art += [path(beak,bill,data_part='beak')]
    if mark=='swan':art += [ellipse(hx+24,hy,6,9,'#303a40')]
    if mark=='gull-grey':art += [ellipse(hx+41,hy+12,3,3,'#d96c47')]
    if mark=='moorhen':art += [ellipse(hx+22,hy-8,7,14,'#d64e3d'),path(f'M{hx+39} {hy+5}l7 3-7 3Z','#edcf59')]
    if mark=='coot':art += [ellipse(hx+22,hy-9,8,16,'#f5f0e0')]
    iris='#efcc68' if mark in ('heron','gull-grey') else '#b85c43' if mark in ('moorhen','coot') else '#35434a'
    art += [eye(hx+10,hy-6,iris,7)]
    return ''.join(art)


def bird_art(row):
    body,breast,wing,bill,shape,mark,_=row
    if shape=='owl':return owl_art(row)
    if shape in ('swift','swallow'):return flying_bird_art(row)
    if shape in ('duck','waterhen','gull','goose','swan','heron'):return waterbird_art(row)
    body,breast,wing,bill=['#'+c for c in (body,breast,wing,bill)]
    head=body
    if mark=='wingbars':head=body;body='#b7896c'
    if mark=='grey-head':head=body;body='#9e7458'
    if mark=='kestrel':head='#8799a5'
    if mark in ('speckles','black'):body=body
    rx,ry=BIRD_BUILD[BIRD_ART.index(row)]
    art=[]
    if shape=='wren':tail='M112 126 75 76 80 127 115 149Z'
    elif shape in ('longtail','woodpecker','climber') or mark=='kestrel':tail='M116 127 49 177 93 166 126 146Z'
    else:tail='M119 128 77 153 111 154 131 139Z'
    art += [path(tail,wing,data_part='tail'),path('M137 152v18m-10 3 10-4 10 4m20-21v18m-10 3 10-4 10 4','none',stroke='#b99a60' if shape=='raptor' else bill,stroke_width=3.5,data_part='feet')]
    art += [ellipse(145,127,rx,ry,body),ellipse(163,134,rx*.64,ry*.76,breast),ellipse(176,80,35 if shape!='tiny' else 29,32,head)]
    if mark in ('bib','blue-mask','nape-white','cap'):
        art += [ellipse(190,90,17,15,'#f6efd9')]
        if mark=='bib':art += [path('M166 110 181 108 175 159 169 161Z','#2c3737')]
        if mark=='blue-mask':art += [path('M148 72Q176 42 203 65L199 73Q171 63 148 72Z','#4d9bd1'),path('M151 79 203 79','none',stroke='#345872',stroke_width=3)]
        if mark=='nape-white':art += [ellipse(148,75,6,10,'#f6efd9')]
        if mark=='cap':art += [path('M142 72Q170 38 207 70L205 76Q173 66 142 78Z','#303737'),path('m177 109 11-2-7 9Z','#303737')]
    if mark in ('sparrow','cheek-spot'):
        art += [ellipse(191,93,16,15,'#ecdfbf'),path('m174 108 18 0-8 15Z','#343632')]
        if mark=='sparrow':art += [path('M150 58Q164 44 180 51L176 63Z','#9da6a4')]
        else:art += [ellipse(191,96,4,5,'#343632')]
    if mark=='red-mask':
        art += [path('M144 77Q147 48 177 48Q197 51 208 68L195 105 180 100Z','#303b3f'),ellipse(183,91,19,18,'#f2e6cb'),ellipse(202,79,12,21,'#d25344')]
    if mark=='orange-face':art += [ellipse(187,96,26,27,breast)]
    if mark=='grey-nape':art += [path('M148 58Q129 75 144 106L159 101 158 59Z','#9ca8aa')]
    if mark=='bare-face':art += [ellipse(204,89,9,14,'#c3c3b8')]
    if mark=='neck-white':art += [path('M161 109Q179 117 193 107L191 118Q172 129 157 118Z','#f8f1df')]
    if mark=='collar':art += [path('M152 109Q171 121 192 111','none',stroke='#354039',stroke_width=4)]
    if mark=='red-cap':art += [path('M145 69Q167 34 204 62L202 70Q171 58 145 75Z','#d44f3e'),path('M167 82 190 85 186 100 169 98Z','#344439')]
    if mark=='eye-stripe':art += [path('M144 75 206 78','none',stroke='#293b45',stroke_width=5)]
    if mark=='gold-crown':art += [path('M150 64Q176 38 202 64','none',stroke='#303b33',stroke_width=9),path('M153 62Q176 43 199 62','none',stroke='#f2cc45',stroke_width=5)]
    if mark=='blackcap':art += [path('M142 71Q172 35 208 67L209 75Q176 64 142 78Z','#303838')]
    if mark in ('eyebrow','treecreeper','red-flank'):art += [path('M151 72Q177 65 204 69','none',stroke='#f0dfb7',stroke_width=4)]
    if mark=='plain':art += [path('M154 74 203 72','none',stroke='#bec891',stroke_width=2)]
    if mark=='wagtail':art += [ellipse(188,83,22,25,'#f4eedb'),path('M166 110 194 106 181 125Z','#303b43')]
    if mark=='crest':art += [path('M153 57 156 38 169 49 180 44 185 55Z',head)]
    if mark in ('spots','large-spots','red-flank','grey-head','buzzard','kestrel','crest'):
        for i in range(8 if mark=='large-spots' else 6):
            x=160+(i%3)*10;y=122+(i//3)*13
            art += [ellipse(x,y,2,3,wing) if mark=='large-spots' else path(f'm{x} {y} 2 4 2-4','none',stroke=wing,stroke_width=1.8)]
    if mark=='cuckoo-bars':art += [path('M155 121h32m-33 9h32m-33 9h31m-29 9h26','none',stroke=body,stroke_width=2.5)]
    if mark=='red-flank':art += [path('M178 129 189 128 184 153 173 158Z','#b66743')]
    art += [path('M114 109Q93 141 119 154Q138 164 151 143L154 129Q130 135 114 109Z',wing,data_part='wing')]
    if mark in ('wingbars','yellow-wing','white-shoulder','pigeon-bars','jay-blue','woodpecker','red-mask'):
        color='#f8efdb' if mark in ('wingbars','white-shoulder','woodpecker') else '#eccb38' if mark in ('yellow-wing','red-mask') else '#33414b' if mark=='pigeon-bars' else '#489dd0'
        art += [path('M111 127 146 139 142 146 108 134Z',color,stroke='none')]
        if mark in ('wingbars','pigeon-bars'):art += [path('M111 141 137 150','none',stroke=color,stroke_width=3)]
        if mark=='jay-blue':
            for x in range(116,143,7):art += [path(f'M{x} 131v8','none',stroke='#30414c',stroke_width=2)]
    if mark in ('treecreeper','streaks','bars'):
        art += [path('M113 126 136 133M110 135 134 142M115 145 129 149','none',stroke=body,stroke_width=2)]
    if mark=='woodpecker':art += [ellipse(190,92,14,13,'#f4eddb'),path('m181 103 19-6','none',stroke='#303a3f',stroke_width=3),path('M132 158 155 150 151 167 139 170Z','#d74d40')]
    if mark=='pink':art += [path('M108 116 120 124 111 143 101 134Z','#d5b2bb')]
    if mark=='speckles':
        for x,y in [(156,118),(174,123),(163,139),(179,148),(167,157),(122,134),(129,148)]:art += [ellipse(x,y,1.8,2.8,'#e0d4b2')]
        art += [path('M112 118 136 133','none',stroke='#4b7d75',stroke_width=2)]
    iris='#edb34b' if mark=='eye-ring' else '#b6d1d2' if mark=='grey-nape' else '#ce9d49' if shape=='raptor' else '#34424b'
    art += [eye(191,77,iris,8)]
    if shape=='raptor':beak='M206 82Q229 79 224 99L216 90 205 91Z'
    elif shape=='climber':beak='M207 80Q234 80 244 99Q224 88 207 90Z'
    elif shape=='finch' and mark!='red-mask' or mark in ('sparrow','cheek-spot'):beak='M207 79 225 88 207 96Z'
    elif shape=='woodpecker':beak='M207 79 238 84 207 90Z'
    else:beak='M207 81 226 87 207 93Z'
    art += [path(beak,bill,data_part='beak')]
    return ''.join(art)


def bat_art(row):
    body,belly,wing,ear,reach,head,feature=row
    body,belly,wing=['#'+c for c in (body,belly,wing)]
    left=150-reach; right=150+reach
    tip=42 if feature=='bent' else 53
    art=[path(f'M132 98Q98 41 {left} {tip}L{left+14} 117Q{left+34} 99 94 139Q113 121 136 150M168 98Q202 41 {right} {tip}L{right-14} 117Q{right-34} 99 206 139Q187 121 164 150',wing),path(f'M132 100 {left+10} {tip+8} 94 139M168 100 {right-10} {tip+8} 206 139','none',stroke='#302d2c',stroke_width=2),ellipse(150,126,head,34,body),ellipse(150,134,head*.64,25,belly)]
    # Independently specified ears and head proportions for every species.
    for direction in (-1,1):
        x=150+direction*(head-5)
        art += [path(f'M{x-8} 85Q{x-direction*8} {64-ear} {x+direction*12} {73-ear}Q{x+direction*16} 65 {x+8} 86Z',body),path(f'M{x-3} 77Q{x+direction*4} {79-ear} {x+direction*7} {83-ear}L{x+3} 79Z','#b38e80')]
    art += [ellipse(150,91,head+2,22,body)]
    if feature=='mane': art += [path('m124 104-8 8 9 2-5 8 12-4m44-14 8 8-9 2 5 8-12-4',body)]
    if feature=='joined': art += [path('M132 75q18-22 36 0l-7 8h-22Z',body)]
    if feature in ('horseshoe','lesser'):
        art += [path('M140 103q-8-25 10-25t10 25l-7-1q8-19-3-17t-3 17Z','#b99a80'),path('m145 97 5-16 5 16Z',belly)]
    elif feature in ('whiskers','brandt'):
        art += [path('m141 101-14-5m14 9-15 3m33-7 14-5m-14 9 15 3','none',stroke=belly,stroke_width=1.5)]
    elif feature=='silver':
        for x,y in [(135,78),(143,72),(154,73),(164,79),(130,115),(170,118),(128,125),(173,130)]: art += [path(f'm{x} {y} 3 4','none',stroke='#d9d9d0',stroke_width=2)]
    elif feature=='soprano': art += [ellipse(150,101,10,7,'#b48a68')]
    elif feature=='nathusius': art += [path('m132 114 5-7 3 10m28-3-5-7-3 10','none',stroke=belly,stroke_width=2)]
    elif feature=='serotine': art += [ellipse(150,101,14,7,'#433932')]
    elif feature=='alcathoe': art += [ellipse(150,100,8,6,'#b18b69')]
    elif feature=='mouse': art += [ellipse(150,102,12,7,'#c2a18b')]
    elif feature=='savi': art += [ellipse(150,101,11,8,'#443b34')]
    if feature=='margin': art += [path(f'M{left+14} 117Q{left+34} 99 94 139Q113 121 136 150M{right-14} 117Q{right-34} 99 206 139Q187 121 164 150','none',stroke='#ded5bb',stroke_width=3)]
    if feature=='notch': art += [path('m174 63-6 3 7 3',belly)]
    if feature=='fringe':
        for x in range(136,166,4): art += [path(f'm{x} 153 0 6','none',stroke=belly,stroke_width=1.5)]
    foot=10 if feature in ('feet','pond') else 5
    for x in (140,160): art += [path(f'm{x} 153-4 {foot}m4-{foot} 1 {foot}m-1-{foot} 5 {foot}','none',stroke=body,stroke_width=3)]
    for x in (140,160): art += [ellipse(x,89,2,2.5,'#252c2c')]
    if feature not in ('horseshoe','lesser'): art += [path('m147 100 3 3 3-3Z','#392f2c')]
    art += [path('m146 109 8 0','none',stroke='#40332d',stroke_width=.7)]
    return ''.join(art)


def encounter_scene(kind, number, row, creature):
    """Small habitat vignettes with a clear foreground action."""
    night = kind == 'bat' or row[4] == 'owl'
    sky = '#465452' if night else '#eee9dc'
    back = f'<rect width="300" height="200" rx="18" fill="{sky}" stroke="none"/>'
    back += ellipse(250,32,17,17,'#f4e4b4' if night else '#fff0b0')
    water = kind == 'bird' and row[4] in ('duck','waterhen','gull','goose','swan','heron')
    if water:
        back += path('M0 125Q70 112 150 129T300 123V200H0Z','#8dbfc0',stroke='none')
        for x,y in [(20,155),(220,170),(68,186)]:
            back += path(f'M{x} {y}q22-5 44 0','none',stroke='#d6eece',stroke_width=3)
        back += path('M18 170 15 102m0 27-9-12m10 28 11-19M282 186V121m0 27-11-15','none',stroke='#557d55',stroke_width=4)
    else:
        for x in (18,270):
            back += path(f'M{x} 200V5m0 55-30-27m30 55 28-28','none',stroke='#455d55' if night else '#a0b6a0',stroke_width=12)
        back += path('M0 187Q80 165 158 186T300 180V200H0Z','#354f48' if night else '#8da66e',stroke='none')
        for x,y in [(38,48),(260,83),(46,141)]:
            for dx,dy in [(-14,0),(0,-12),(15,3)]:
                back += path(f'M{x+dx} {y+dy}q-19-20-27-13q-2 19 27 13q12-26 25-20q4 15-25 20', '#64776a' if night else '#a5ad8d',stroke='none')
        if kind == 'bird' and row[4] not in ('swift','swallow'):
            back += path('M65 183Q160 173 249 180l31-12','none',stroke='#88624c',stroke_width=8)
    front = ''
    angle = -5 + number % 4 * 3
    if kind == 'bird' and row[5] == 'jay-blue':
        angle = -8
        # A jay carrying an acorn at the tip of its bill, beside a tiny cache.
        front += ellipse(230,98,10,14,'#b87e43')
        front += path('M219 92Q230 81 241 92L240 96H220Z','#70593f')
        front += path('M230 84q0-8 5-10','none',stroke='#70593f',stroke_width=2)
        front += ellipse(65,187,13,5,'#5d7050')
        front += ellipse(69,181,6,8,'#b87e43')
    if night:
        for x,y in [(66,22),(214,46),(99,39)]:
            back += ellipse(x,y,1.5,1.5,'#f6e7b8')
    return back + f'<g transform="translate(150 106) rotate({angle}) translate(-150 -106)">' + creature + front + '</g>'


def build():
    full=[]; locked=[]
    for kind,rows,draw in [('bird',BIRD_ART,bird_art),('bat',BAT_ART,bat_art)]:
        for number,row in enumerate(rows,1):
            content=draw(row)
            silhouette=re.sub(r'#[0-9a-fA-F]{6,8}', '#293843', content)
            full.append(content); locked.append(silhouette)
            for suffix,art in [('',content),('-locked',silhouette)]:
                if not suffix:
                    art = encounter_scene(kind, number, row, art)
                # Fine ink outlines and restrained pigment suit the field journal UI.
                def pigment(match):
                    value=match.group(0)[1:7]
                    rgb=[int(value[i:i+2],16) for i in (0,2,4)]
                    grey=sum(rgb)/3
                    return '#'+''.join(f'{round(c*.74+grey*.18+235*.08):02x}' for c in rgb)
                if not suffix:
                    art=re.sub(r'#[0-9a-fA-F]{6}',pigment,art)
                svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200"><defs><filter id="paper"><feTurbulence type="fractalNoise" baseFrequency=".65" numOctaves="3" stitchTiles="stitch"/><feColorMatrix type="saturate" values="0"/></filter></defs><g stroke="#505448" stroke-width="1" stroke-linejoin="round" stroke-linecap="round">'+art+'</g>'
                if not suffix:
                    svg+='<rect width="300" height="200" filter="url(#paper)" opacity=".055" style="mix-blend-mode:multiply"/>'
                svg+='</svg>\n'
                (OUT/f'{kind}-{number:03d}{suffix}.svg').write_text(svg)
    assert len(full)==len(set(full)), 'Duplicate coloured portraits'
    assert len(locked)==len(set(locked)), 'Duplicate silhouette portraits'
    print(f'Built {len(full)} unique portraits and {len(locked)} unique silhouettes.')

if __name__=='__main__': build()
