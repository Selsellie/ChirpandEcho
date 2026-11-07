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


def bird_art(row):
    body,breast,wing,bill,shape,mark,_ = row
    body,breast,wing,bill = ['#'+c for c in (body,breast,wing,bill)]
    art=[]
    long = shape in ('longtail','woodpecker','climber')
    aquatic = shape in ('duck','waterhen','gull','goose','swan')
    headx,heady = (184,67) if shape in ('swan','heron','goose') else (176,82)
    rx,ry = BIRD_BUILD[BIRD_ART.index(row)]
    if shape in ('swift','swallow'):
        art += [path('M139 99Q84 12 22 32Q68 66 102 121Z',wing),path('M159 102Q212 17 274 35Q219 69 187 126Z',body),path('m130 124-34 59 42-26 26 26-9-59',wing)]
    else:
        art += [path('m120 124-'+str(67 if long else 39)+' '+str(47 if long else 26)+' 51-9 20-42Z',wing)]
    if shape in ('heron','waterhen','lark'):
        art += [path('M137 149v35m-12 0h24m21-35 9 35m-12 0h23',bill,stroke=bill,stroke_width=4)]
    else:
        art += [path('m139 149-6 20m-10 0h21m23-20 6 20m-10 0h21','none',stroke=bill,stroke_width=4)]
    art += [ellipse(143,126,rx,ry,body),ellipse(158,135,rx*.64,ry*.72,breast)]
    if shape in ('swan','heron','goose'):
        art += [path('M164 129Q146 101 173 71L197 71Q176 102 188 127Z',body)]
    if shape=='owl': headx,heady=153,80
    art += [ellipse(headx,heady,32 if shape!='tiny' else 25,29,body)]
    if shape=='raptor':
        art += [path('m202 79q30-2 18 23l-9-12-11 1Z',bill)]
    else:
        tip = 253 if shape=='heron' else 238 if shape=='climber' else 219 if shape not in ('finch','duck','goose') else 227
        art += [path(f'M{headx+26} {heady-1} {tip} {heady+8} {headx+26} {heady+13}Z',bill)]
    if shape in ('swift','swallow'):
        art += [path('M116 105Q112 142 161 147L181 118Q148 132 116 105Z',wing)]
    else:
        art += [path('M112 108Q89 154 141 155Q164 151 166 124Q141 132 112 108Z',wing)]
    # Each marking is drawn separately rather than recolouring a shared portrait.
    if mark=='orange-face': art += [ellipse(185,94,22,23,breast)]
    if mark in ('bib','blue-mask','nape-white','cap'):
        art += [ellipse(187,89,16,13,'#f5efdc')]
        if mark=='bib': art += [path('m160 105 17 4-9 46h-8Z','#28332f')]
        if mark=='blue-mask': art += [path('m153 76 48 7-1 5-47-7Z','#29455c'),path('M155 64q24-20 43 8Z','#438dce')]
        if mark=='nape-white': art += [ellipse(153,77,7,12,'#eee9dc')]
        if mark=='cap': art += [path('M147 72q22-31 53 1Z','#292f30')]
    if mark in ('sparrow','cheek-spot'):
        art += [ellipse(188,90,14,13,'#e4d8bd'),path('m173 105 17 0-8 16Z','#302d29')]
        if mark=='sparrow': art += [path('M153 65q13-12 29-5l-3 13Z','#9a9e99')]
        else: art += [ellipse(187,91,4,5,'#34302c')]
    if mark in ('wingbars','yellow-wing','white-shoulder','pigeon-bars','jay-blue','woodpecker'):
        colour='#f7efdc' if mark in ('wingbars','white-shoulder','woodpecker') else '#dfcf35' if mark=='yellow-wing' else '#292e35' if mark=='pigeon-bars' else '#4199cc'
        art += [path('m113 123 40 10-5 7-39-10Z',colour),path('m110 136 29 9-5 5-24-8Z',colour)]
        if mark=='jay-blue':
            for x in range(117,148,7): art += [path(f'm{x} 125 0 10','none',stroke='#293646',stroke_width=2)]
        if mark=='woodpecker': art += [path('m133 151 26-9-5 19-17 3Z','#d34d40')]
    if mark=='red-mask': art += [ellipse(192,82,16,20,'#ce493c'),path('m113 128 42 10-6 8-40-10Z','#ebd039')]
    if mark in ('streaks','bars','spots','large-spots','red-flank','grey-head','buzzard','kestrel','owl-brown','owl-white','ear-tufts','treecreeper','goose-bars'):
        count={'spots':6,'large-spots':8,'buzzard':4,'kestrel':9,'owl-brown':7,'owl-white':5,'treecreeper':10}.get(mark,4)
        for i in range(count):
            x=142+(i%3)*10; y=122+(i//3)*10
            art += [path(f'm{x} {y} 3 5 2-5',wing,stroke_width=1)]
        if mark=='bars': art += [path('M108 113h38m-43 11h44m-43 11h32','none',stroke=body,stroke_width=3)]
        if mark=='red-flank': art += [path('m164 130 16-4-4 25-14 8Z','#b4623e'),path('m157 69 40-2','none',stroke='#eadab3',stroke_width=4)]
        if mark=='treecreeper': art += [path('m157 73 40-5','none',stroke='#e8dbc0',stroke_width=4)]
    if mark=='grey-nape': art += [path('M149 63q-18 18 0 38l13-7-4-28Z','#929b9d')]
    if mark=='bare-face': art += [ellipse(198,87,11,15,'#b8b7aa')]
    if mark=='neck-white': art += [path('m166 103 27 2-4 10-27-3Z','#f1efdf')]
    if mark=='collar': art += [path('m153 104q21 11 39 1','none',stroke='#313735',stroke_width=5)]
    if mark=='red-cap': art += [path('M150 69q24-26 49 7l-27-4Z','#ce4b36'),path('m161 83 27 5-8 16-15-4Z','#344037')]
    if mark=='eye-stripe': art += [path('m150 76 49 8-2 5-45-8Z','#303b40')]
    if mark=='pink': art += [path('m114 109 15 8-15 29-9-13Z','#d6b5b7')]
    if mark=='gold-crown': art += [path('M153 68q17-23 38 1l-17-3Z','#f0c934')]
    if mark=='blackcap': art += [path('M147 73q22-33 55 0Z','#303538')]
    if mark=='eyebrow': art += [path('m155 73 40-4','none',stroke='#e8dfa9',stroke_width=4)]
    if mark=='plain': art += [path('m157 76 37-3','none',stroke='#b4bb80',stroke_width=2)]
    if mark=='cuckoo-bars': art += [path('M145 125h35m-36 9h34m-35 9h29m-29 9h22','none',stroke=body,stroke_width=3)]
    if mark=='pale-throat': art += [ellipse(188,101,10,7,'#b0a38b')]
    if mark=='red-throat': art += [ellipse(191,96,11,12,'#b66a46')]
    if mark=='white-rump': art += [path('m117 137 21 9-13 12-17-10Z','#f4eee2')]
    if mark=='wagtail': art += [ellipse(184,84,18,20,'#f4efe0'),path('m164 108 29-3-12 17Z','#2e343a')]
    if mark=='crest': art += [path('m153 61 5-18 12 11 10-8 4 17Z',body)]
    if shape=='owl':
        art += [ellipse(153,83,28,24,'#e7d5b4')]
        if mark=='heart-face': art += [path('M153 70Q119 51 128 87L153 109Q185 83 175 68Q162 61 153 70Z','#fff0d3')]
        if mark=='ear-tufts': art += [path('m127 64-2-28 18 24m20 0 19-24-3 32',body)]
        for x in (141,165): art += [ellipse(x,81,8,9,'#dbb049' if mark!='owl-brown' and mark!='heart-face' else '#353331'),ellipse(x,81,3,5,'#242b2c')]
        art += [path('m148 94 5 9 5-9Z',bill)]
    if mark=='mallard': art += [ellipse(176,82,30,28,'#346c51'),path('m157 107 35 1','none',stroke='#efe9d2',stroke_width=5),path('m112 128 39 8-5 9-36-7Z','#526fa1')]
    if mark=='heron': art += [path('m161 68 31-17-10 12 19 1','none',stroke='#303d46',stroke_width=4)]
    if mark=='moorhen': art += [path('m187 62 13 4 5 23-13-6Z','#d34b37')]
    if mark=='coot': art += [ellipse(197,71,10,16,'#f4efe2')]
    if mark=='gull-hood': art += [ellipse(176,82,31,28,'#57423a')]
    if mark=='gull-grey': art += [path('m148 149 14 2-5 5-13-2Z','#333b40')]
    if mark=='canada': art += [path('M164 129Q146 101 173 71L197 71Q176 102 188 127Z','#2d3438'),ellipse(184,67,30,26,'#2d3438'),path('m173 77 30 0-9 13-18-2Z','#f4eedb')]
    if mark=='swan': art += [ellipse(210,69,8,10,'#343739')]
    if shape!='owl':
        eye='#dce4df' if mark=='grey-nape' else '#f1a834' if mark=='eye-ring' else '#29343a'
        art += [ellipse(headx+11,heady-6,5.5,6,eye),ellipse(headx+12,heady-7,2,2,'#fff8e9')]
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
    for x in (140,160): art += [ellipse(x,89,4,5,'#252c2c'),ellipse(x+1,88,1.5,1.5,'#fff6df')]
    if feature not in ('horseshoe','lesser'): art += [path('m147 100 3 3 3-3Z','#392f2c')]
    art += [path('m144 109q6 4 12 0','none',stroke='#40332d',stroke_width=2)]
    return ''.join(art)


def build():
    full=[]; locked=[]
    for kind,rows,draw in [('bird',BIRD_ART,bird_art),('bat',BAT_ART,bat_art)]:
        for number,row in enumerate(rows,1):
            content=draw(row)
            silhouette=re.sub(r'#[0-9a-fA-F]{6,8}', '#293843', content)
            full.append(content); locked.append(silhouette)
            for suffix,art in [('',content),('-locked',silhouette)]:
                svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200"><g stroke="#293843" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round">'+art+'</g></svg>\n'
                (OUT/f'{kind}-{number:03d}{suffix}.svg').write_text(svg)
    assert len(full)==len(set(full)), 'Duplicate coloured portraits'
    assert len(locked)==len(set(locked)), 'Duplicate silhouette portraits'
    print(f'Built {len(full)} unique portraits and {len(locked)} unique silhouettes.')

if __name__=='__main__': build()
