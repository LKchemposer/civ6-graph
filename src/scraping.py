import pandas as pd
import requests
from bs4 import BeautifulSoup

# ============
# 1. [Technologies](https://civilization.fandom.com/wiki/List_of_technologies_in_Civ6)
# 2. [Civics](https://civilization.fandom.com/wiki/List_of_civics_in_Civ6)
# 3. [Resources](https://civilization.fandom.com/wiki/List_of_resources_in_Civ6)
# 4. [Buildings](https://civilization.fandom.com/wiki/List_of_buildings_in_Civ6)
# 5. [Policy cards](https://civilization.fandom.com/wiki/List_of_policy_cards_in_Civ6)
# 6. [Improvements](https://civilization.fandom.com/wiki/List_of_improvements_in_Civ6)
# 7. [Units](https://civilization.fandom.com/wiki/List_of_units_in_Civ6/By_class)
#     * No Religious units, Great People
# 8. [Wonders](https://civilization.fandom.com/wiki/List_of_wonders_in_Civ6)
# 9. [Projects](https://civilization.fandom.com/wiki/List_of_projects_in_Civ6)
# 10. [Districts](https://civilization.fandom.com/wiki/List_of_districts_in_Civ6)
# 11. [Civilizations](https://civilization.fandom.com/wiki/Civilizations_(Civ6))
# 12. [Governments](https://civilization.fandom.com/wiki/Government_(Civ6))

# ============
# Technologies
tech_url = 'https://civilization.fandom.com/wiki/List_of_technologies_in_Civ6'
response = requests.get(tech_url)
bs = BeautifulSoup(response.text, 'html.parser')

for rf in bs.find_all('img', alt='R&F-Only.png'):
    rf.string = 'R&F'
for gs in bs.find_all('img', alt='GS-Only.png'):
    gs.string = 'GS'

def camelcase(word):
    if sum([l.islower() for l in word]) > 0 and sum([l.isupper() for l in word]) > 1:
        sep = ''.join([', ' + w if w.isupper() and i > 0 else w for i, w in enumerate(word)])
        return sep
    else: return word

infras = pd.concat([pd.read_csv('./Buildings.csv')['Building'],
                    pd.read_csv('./Improvements.csv')['Improvement'],
                    pd.read_csv('./Districts.csv')['District'],
                    pd.read_csv('./Wonders.csv')['Wonder']]).values

units = pd.read_csv('./Units.csv')['Unit'].values

tbls = bs.find_all('table', class_='article-table')[:-1]
eras = [i.text for i in bs.find_all('span', class_='mw-headline')][:-1]

lines = []
for tbl, era in zip(tbls, eras):
    for tr in tbl.find_all('tr')[1:]:
        if 'GS' not in tr.td.text:
            tds = tr.find_all('td')
            
            tech = tds[0].text.strip().strip('*')
            
            pre = list(tds[1].stripped_strings)
            pre = [i for i in pre if not ('('  in i or ')' in i)]
            pre = [i for i in pre if 'R&F' not in i]
            while 'GS' in pre:
                i = pre.index('GS')
                del pre[i]
                del pre[i - 1]
            pre = ', '.join(pre)
            
            cost = tds[2].text.strip().split('(')[0]
            
            eur = tds[3].text.split('\n')[0]
            eur = ' '.join([camelcase(i) for i in eur.split()]).replace('R&, F', 'R&F')
            eur = eur.split(', ')[0]
            if '(' in eur:
                eur = eur[:eur.index('(')] + eur[eur.index(')') + 1:]
            
            
            inf = tds[4].text.strip().replace('\xa0', ' ').strip(',')
            while '(' in inf:
                inf = inf[:inf.index(' (')] + inf[inf.index(')') + 1:]
            infchk = [i for i in inf.split(', ') if i and i in infras]
            inf_rest = [i for i in inf.split(', ') if i and i not in infras]
            inf = ', '.join(infchk)
            
            uni = tds[5].text.strip()
            uni = uni.replace('\xa0', ' ').replace('Imperiale', 'Impériale').replace('Anti-air', 'Anti-Air').strip(',')
            while '(' in uni:
                uni = uni[:uni.index(' (')] + uni[uni.index(')') + 1:]
            unichk = [i for i in uni.split(', ') if i and i in units]
            uni_rest = [i for i in uni.split(', ') if i and i not in units]
            uni = ', '.join(unichk)

            
            eff = list(tds[6].stripped_strings)
            eff = ' '.join(eff).replace('&plus;', '+')
            eff = eff.split(' ( GS )')[0]
            dip = 'Research Agreement' if 'Research Agreement' in eff else None
            while '(' in eff:
                eff = eff[:eff.index('(')] + eff[eff.index(')') + 1:]
            eff = eff.strip().replace(' ,', ',').replace('  ', ' ')
            
            lines.append([era, tech, pre, cost, eur, inf, uni, eff, dip])

cols = ['Era', 'Technology', 'Prerequisites', 'Cost', 'Eureka', 'Infrastructure', 'Units', 'Effects', 'Diplomacies']
techs = pd.DataFrame(lines, columns=cols)
techs[(techs == 'None') | (techs == '') | (techs == 'N/A')] = None
techs.to_csv('Technologies.csv', index=False)

# ======
# Civics
civ_url = 'https://civilization.fandom.com/wiki/List_of_civics_in_Civ6'
response = requests.get(civ_url)
bs = BeautifulSoup(response.text, 'html.parser')

tbl = bs.find('table', class_='article-table')
for rf in tbl.find_all('img', alt='R&F-Only.png'):
    rf.string = 'R&F'
for gs in tbl.find_all('img', alt='GS-Only.png'):
    gs.string = 'GS'

gs_civs = ['Environmentalism', 'Near Future Governance', 'Venture Politics', 'Distributed Sovereignty',
           'Optimization Imperative', 'Information Warfare', 'Global Warming Mitigation', 'Cultural Hegemony',
           'Smart Power Doctrine', 'Exodus Imperative', 'GS Future Civic']

vnl_pols = pd.read_csv('./data/Policies.csv')['Policy'].values

vnl_unlocks = pd.concat([pd.read_csv('./data/Buildings.csv')['Building'],
                         pd.read_csv('./data/Improvements.csv')['Improvement'],
                         pd.read_csv('./data/Districts.csv')['District'],
                         pd.read_csv('./data/Wonders.csv')['Wonder'],
                         pd.read_csv('./data/Governments.csv')['Government'],
                         pd.read_csv('./data/Units.csv')['Unit']]).values

vnl_dips = ['Joint War', 'Join Ongoing War', 'Open Borders', 'Casus Belli', 'Alliances', 'Resident Embassies', 'Defensive Pacts']

index = dict()
cols = ['Era', 'Inspiration', 'Policy Cards', 'Obsoletes', 'Unlocks', 'Other Effects', 'Diplomacies', 'Leads to']

for tr in tbl.find_all('tr')[1:]:
    if 'Era' in tr.th.text:
        era = tr.th.text.strip()
    if tr.th.text.strip() not in gs_civs:
        civ = tr.find('th').text.strip().replace('(vanilla Civilization VI, R&F) ', '')
        tds = tr.find_all('td')
        if tds:
            insp = tds[0].text.strip()
            insp = [i for i in insp.split('\n') if not ('GS' in i or 'None' in i)]
            insp = ''.join(insp)
            
            pols = list(tds[1].stripped_strings)
            polchk = [i for i in pols if i in vnl_pols or 'Obsolete' in i or 'Nobel Prize' in i]
            pol_rest = [i for i in pols if not (i in vnl_pols or 'Obsolete' in i)]
            pol = polchk[:polchk.index('Obsolete:')] if 'Obsolete:' in polchk else polchk
            obs = polchk[polchk.index('Obsolete:') + 1:] if 'Obsolete:' in polchk else []
            pol = ', '.join(pol).replace('Nobel Prize', 'Science Foundations')
            obs = ', '.join(obs)
            
            ulks = tds[2].text.strip().split('\n')
            ulk = [i.strip().replace('  ', ' ') for i in ulks if not ('GS' in i or 'R&F' in i) and i]
            leftover = [i for i in ulk if '+' in i]
            ulkchk = [i for i in ulk if i in vnl_unlocks]
            ulk_rest = [i for i in ulk if i not in vnl_unlocks and '+' not in i]
            ulk = ', '.join(ulkchk)
            
            other = list(tds[3].stripped_strings)
            dips = [''.join(other[other.index('Casus Belli'):other.index('Casus Belli') + 2])
                    if 'Casus Belli' == i else i for i in other if i in vnl_dips]
            other = ' '.join(other).replace(' :', ':').replace(' ,', ',').replace(' .', '.')
            other = ' '.join([other, ' '.join(leftover)]).strip()
            dips = ', '.join(dips)
            
            leads = tds[4].text.strip().split('\n')
            leads = [i.replace('Without GS:', '').replace('With GS:', '').replace('GS:', '').strip()  for i in leads]
            leads = [i for i in leads if i and i not in gs_civs and 'finished' not in i]
            leads = ', '.join(leads)
            
            index[civ] = {
                k: v for k, v in zip(cols, [era, insp, pol, obs, ulk, other, dips, leads])
            }

civs = pd.DataFrame.from_dict(index, 'index')
civs.index.name = 'Civic'
civs.columns = ['Era', 'Inspiration', 'Policies', 'Obsoletes', 'Unlocks', 'Effects', 'Diplomacies', 'Leads to']
civs[(civs == 'None') | (civs == '')] = None
civs.to_csv('./data/Civics.csv')

# =========
# Resources
rsrs_url = 'https://civilization.fandom.com/wiki/List_of_resources_in_Civ6'
response = requests.get(rsrs_url)
bs = BeautifulSoup(response.text, 'html.parser')

tbls = bs.find_all('table', class_='article-table')

lines = []

for tbl in tbls[0].find_all('tr')[1:]:
    line = [l.strip() for l in tbl.text.strip().split('\n\n')]
    line.insert(0, 'Bonus')
    lines.append(line)
    
for tbl in tbls[1].find_all('tr')[1:]:
    line = [l.strip() for l in tbl.text.strip().split('\n\n')]
    line.insert(3, 'None')
    line.insert(0, 'Luxury')
    lines.append(line)

for tbl in tbls[2].find_all('tr')[1:]:
    line = [l.strip() for l in tbl.text.strip().split('\n\n')]
    line[1] = line[1].split('\n')[0].replace('Pre-: ', '')
    en = line.pop(1)
    line.append(en)
    line.insert(3 , 'None')
    line.insert(0, 'Strategic')
    lines.append(line)

rsrs = pd.DataFrame(lines, columns=['Type', 'Resource', 'Base Yield Modifier', 'Improvement', 'Harvest with', 'Notes', 'Enables'])
rsrs['Resource'] = rsrs['Resource'].str.strip('\n[1] ')
rsrs['Base Yield Modifier'] = rsrs['Base Yield Modifier'].str.replace('  ', ' ').str.replace('\n', ' ')
rsrs['Notes'] = (rsrs['Notes'].str.replace('  ', ' ')
 .str.replace(' Revealed by Animal Husbandry.', '')
 .str.replace(' \( Refining\)', ''))

ls = []
for tbl in tbls[3].find_all('tr')[1:]:
    line = [l.strip().replace('  ', ' ') for l in tbl.text.strip().split('\n\n')]
    del line[2]
    line.insert(0, 'Special')
    ls.append(line)

arts = pd.DataFrame([dict(zip(['Type', 'Resource', 'Enables', 'Notes'], i)) for i in ls])

rsrs = rsrs.append(arts, ignore_index=True, sort=False)

def extract_reveal(notes):
    s = [i for i in notes.split('. ') if 'Revealed by' in i]
    if s: return s[0].replace('Revealed by ', '')
    else: return

rsrs['Revealed by'] = rsrs['Notes'].apply(extract_reveal)

rsrs.set_index('Resource').drop(['Amber', 'Olives', 'Turtles'], inplace=True)

rsrs.columns = ['Type', 'Resource', 'Yields', 'Improvement', 'Harvest with', 'Effects', 'Enables', 'Revealed by']
rsrs[(rsrs == 'None') | (rsrs == '')] = None
rsrs.to_csv('Resources.csv', index=False)

# =========
# Buildings
bds_url = 'https://civilization.fandom.com/wiki/List_of_buildings_in_Civ6'
response = requests.get(bds_url)
bs = BeautifulSoup(response.text, 'html.parser')

for rf in bs.find_all('img', alt='R&F-Only.png'):
    rf.string = 'R&F'
for gs in bs.find_all('img', alt='GS-Only.png'):
    gs.string = 'GS'

base = 'https://civilization.fandom.com'
hrefs = []
for tr in bs.find('table').find_all('tr')[1:]:
    if not ('R&F' in tr.td.text or 'Vanilla' in tr.td.text or 'GS' not tr.td.text):
        hrefs.append(base + tr.td.a['href'])

from time import sleep

bss = []
for i, href in enumerate(hrefs):
    response = requests.get(href)
    bs = BeautifulSoup(response.text, 'html.parser')
    bss.append(bs)
    print(i, href[32:], response.status_code)
    sleep(1)

infos = []
for bs in bss:
    for rf in bs.find('aside').find_all('img', alt='R&F-Only.png'):
        rf.string = 'R&F'
    for gs in bs.find('aside').find_all('img', alt='GS-Only.png'):
        gs.string = 'GS'
        
    info = list(bs.find('aside').stripped_strings)
    
    if 'Infrastructure' in info:
        inf = info.index('Infrastructure') + 1
        eff = info.index('Effects')
        info[inf:eff] = [', '.join(info[inf:eff])]
        
    keys = [j for j, i in enumerate(info)
            if i in ['Building', 'Introduced in', 'Unlocked by', 'Cost', 'Requires', 'Effects', 'Unique to']]
    keys = [0] + keys + [None]

    infos.append([' '.join(info[k: keys[i + 1]]) for i, k in enumerate(keys[:-1])])

def extract(unit, phrase):
    s = phrase.split()
    if 'Building' in phrase:
        index[unit]['Era'] = phrase.rstrip(' .').replace('Building of the ', '')
    if 'Unique to' in phrase:
        index[unit]['Unique to'] = s[s.index('Replaces') + 1]
        index[unit]['Replaces'] = ' '.join(s[s.index('Replaces') + 2:])
    if 'Requires' in phrase:
        if 'Infrastructure' in phrase:
            index[unit]['District'] = ' '.join(s[s.index('District') + 1: s.index('Infrastructure')])
            index[unit]['Infrastructure'] = ' '.join(s[s.index('Infrastructure') + 1:])
        else: index[unit]['District'] = ' '.join(s[s.index('District') + 1:])
    if 'Unlocked by' in phrase:
        index[unit]['Unlocked by'] = ' '.join(s[s.index('by') + 1:])
    if 'Cost' in phrase:
        s = [c for i, c in enumerate(s) if c != 'GS' and s[i - 1] != 'GS']
        vals = [i for i in s if i.isnumeric()]
        costs = [i for i in s[1:] if i.strip('.').isalpha()]
        index[unit]['Cost'] = ', '.join(['{}: {}'.format(cost, val) for cost, val in list(zip(costs, vals))]) 
    if 'Effects' in phrase:
        eff = phrase.replace('Effects ', '').replace(' .', '.').replace(' ,', ',')
        if '(' in eff:
            eff = eff[:eff.index('(')] + eff[eff.index(')') + 1:]
        index[unit]['Effects'] = eff

index = dict()

for bd in infos:
    index[bd[0]] = dict()
    for spec in bd[1:]:
        extract(bd[0], spec)

bds = pd.DataFrame.from_dict(index, 'index')
bds.index.name = 'Building'
bds.to_csv('Buildings.csv')

# ============
# Policy Cards
pols_url = 'https://civilization.fandom.com/wiki/List_of_policy_cards_in_Civ6'
response = requests.get(pols_url)
bs = BeautifulSoup(response.text, 'html.parser')

lines = []
for tr in bs.find_all('table')[0].find_all('tr')[1:]:
    if not (tr.td.img and (tr.td.img['alt'] == 'GS-Only.png' or tr.td.img['alt'] == 'R&F-Only.png')):
        tds = tr.find_all('td')
        
        card = tds[0].text.strip()
        card = card[:card.index('[')].strip() if '[' in card else card
        
        typ = [i.strip() for i in tds[1].text.strip().split('\n')][0]
        
        desc = [i for i in tds[2].text.strip().split('\n')][0]
        desc = desc.replace(' ( 5%)', '').replace('  ', ' ')
        
        rest = [i.text.strip() for i in tds[3:]]
        lines.append([card] + [typ] + [desc] + rest)

cols = ['Policy', 'Type', 'Notes', 'Supersedes', 'Obsoleted by', 'Civic', 'Era']
pols = pd.DataFrame(lines, columns=cols)

pols[(pols == '') | (pols == 'None')] = None
pols.to_csv('./data/Policies.csv', index=False)

# ============
# Improvements
ipv_url = 'https://civilization.fandom.com/wiki/List_of_improvements_in_Civ6'
response = requests.get(ipv_url)
bs = BeautifulSoup(response.text, 'html.parser')

tbl = bs.find('table')
for rf in bs.find_all('img', alt='R&F-Only.png'):
    rf.string = 'R&F'
for gs in bs.find_all('img', alt='GS-Only.png'):
    gs.string = 'GS'

lines = []
for tr in tbl.find_all('tr')[1:]:
    if not ('GS' in tr.td.text or 'R&F' in tr.td.text):
        tds = tr.find_all('td')
        
        ipv = tds[0].text.strip()
        req = tds[1].text.strip()
        
        where = list(tds[2].stripped_strings)
        where = ', '.join(where)
        where = (where.replace('on,', 'on')
                 .replace(', with,', ' with')
                 .replace(', Rainforest, (, GS, only) (, Mercantilism, )', ''))
        
        rsr = list(tds[3].stripped_strings)
        rsr = [i for i in rsr if i not in ['Amber', 'Olives', 'Turtles', 'Minimum', 'Appeal', 'of Breathtaking (4+)']]
        rsr = ', '.join(rsr)
        
        notes = tds[4].text.strip().split('\n')
        gs = [notes.index(i) for i in notes if 'GS' in i]
        gs = gs[0] if gs else None
        notes = notes[:gs]
        notes = ', '.join(notes)
        notes = (notes.replace('fortification.Built', 'fortification., Built')
                 .replace('-1 Appeal+3 Aircraft CapacityBuilt', '-1 Appeal, +3 Aircraft Capacity., Built')
                 .replace('Vanilla and R&F, ', '')
                 .replace(' (Vanilla and R&F only)', '')
                 .replace('  ', ' '))
        
        plun = tds[5].text.strip()
        lines.append([ipv] + [req] + [where] + [rsr] + [notes] + [plun])

cols = ['Improvement', 'Requires', 'Placement', 'Resource', 'Notes', 'Plunder']
gens = {l[0]: dict(zip(cols[1:], l[1:])) for l in  lines}

tbls = bs.find_all('table')

lines = []
for tr in tbls[1].find_all('tr')[1:]:
    if 'GS' not in tr.td.text:
        tds = tr.find_all('td')
        
        ipv = tds[0].text.strip()
        cs = tds[1].text.strip()
        res = tds[2].text.strip()
        note = [i.replace('  ', ' ').replace(' (Vanilla & R&F)', '') for i in tds[3].text.split('\n') if i and 'GS' not in i]
        note = ', '.join(note)
        plun = tds[4].text.strip()
        lines.append([ipv] + [cs] + [res] + [note] + [plun])

cols = ['Improvement', 'Unique to', 'Placement', 'Notes', 'Plunder']
cts = {l[0]: dict(zip(cols[1:], l[1:])) for l in  lines}

lines = []
for tr in tbls[2].find_all('tr')[1:]:
    if 'GS' not in tr.td.text and 'R&F' not in tr.td.text:
        tds = tr.find_all('td')
        
        ipv = list(tds[0].stripped_strings)[0]
        civ = tds[1].text.strip()
        req = tds[2].text.strip()
        
        res = tds[3].text.strip()
        res = res.strip('.') + '.' if res else ''
        
        note = tds[4].text.strip().split('\n')
        note = ['GS:' if (note + [''])[j + 1] == '+2  Faith' else i.strip() for j, i in enumerate(note)]
        note = note[:note.index('GS:')] if 'GS:' in note else note
        note = ' '.join(note).replace('  ', ' ').replace('\xa0', ' ')
        note = '+'.join([i for i in note.split('+') if 'GS' not in i])
        note = note.replace('Vanilla and R&F', '').replace('(+1', '+1').strip(': ')
        
        plun = tds[5].text.strip()
        lines.append([ipv] + [civ] + [req] + [res] + [note] + [plun])
        
cols = ['Improvement', 'Unique to', 'Requires', 'Placement', 'Notes', 'Plunder']
uniq = {l[0]: dict(zip(cols[1:], l[1:])) for l in  lines}

ipvsd = {**gens, **cts, ** uniq}

ipvs = pd.DataFrame.from_dict(ipvsd, 'index')
ipvs.index.name = 'Improvement'
ipvs.columns = ['Requires', 'Placement', 'Resource', 'Effects', 'Plunder', 'Unique to']

ipvs[(ipvs == '') | (ipvs == 'None')] = None
ipvs.to_csv('Improvements.csv')

# =====
# Units
unit_url = 'https://civilization.fandom.com/wiki/List_of_units_in_Civ6'
response = requests.get(unit_url)
bs = BeautifulSoup(response.text, 'html.parser')

for rf in bs.find_all('img', alt='R&F-Only.png'):
    rf.string = 'R&F'
for gs in bs.find_all('img', alt='GS-Only.png'):
    gs.string = 'GS'

tbls = bs.find_all('table', limit=3)[1:]

hrefs = []
for tbl in tbls:
    for tr in tbl.find_all('tr')[1:]:
        for a in tr.find_all('a'):
            if (not a.text # href from imgs only
                and a.attrs['href'] not in hrefs
                and a.attrs['href'].startswith('/wiki/')):
                hrefs.append(a.attrs['href'])

unit_url = 'https://civilization.fandom.com/wiki/List_of_units_in_Civ6/By_class'
response = requests.get(unit_url)
bs = BeautifulSoup(response.text, 'html.parser')

for rf in bs.find_all('img', alt='R&F-Only.png'):
    rf.string = 'R&F'
for gs in bs.find_all('img', alt='GS-Only.png'):
    gs.string = 'GS'
                
base = 'https://civilization.fandom.com'
cvns = [i.a['href'] for i in bs.find('h2').find_next('h2').find_all_next('li', limit=6) if 'GS' not in i.text]
hrefs = [base + href for href in hrefs + cvns]

from time import sleep

bss = []
for i, href in enumerate(hrefs):
    response = requests.get(href)
    bs = BeautifulSoup(response.text, 'html.parser')
    bss.append(bs)
    print(i, href[32:], response.status_code)
    sleep(1)

infos = []
for bs in bss:
    for rf in bs.find('aside').find_all('img', alt='R&F-Only.png'):
        rf.string = 'R&F'
    for gs in bs.find('aside').find_all('img', alt='GS-Only.png'):
        gs.string = 'GS'
        
    info = list(bs.find('aside').stripped_strings)
    if 'Upgrades to' in info:
        upi = info.index('Upgrades to') + 1
        notei = info.index('Notes')
        info[upi: notei] = [', '.join(info[upi: notei])]
    keys = [j for j, i in enumerate(info)
            if i in ['Portrait', 'Introduced in', 'Unlocked by', 'Cost', 'Upgrades to', 'Stats', 'Notes', 'Resources', 'Unique to']]
    keys = [0] + keys + [None]

    infos.append([' '.join(info[k: keys[i + 1]]) for i, k in enumerate(keys[:-1])])

soups = dict(zip([i[32:] for i in hrefs], infos))

def extract(unit, phrase):
    s = phrase.split()
    if 'Portrait' in phrase:
        s = phrase.rstrip(' .').replace('Portrait Icon ', '').split(' unit of the ')
        index[unit]['Type'] = s[0]
        index[unit]['Era'] = s[1]
    if 'Unique to' in phrase:
        if 'Replaces' in phrase:
            index[unit]['Unique to'] = ' '.join(s[s.index('Replaces') + 1: -1])
            index[unit]['Replaces'] = s[-1]
        else: index[unit]['Unique to'] = s[-1]
    if 'Unlocked by' in phrase:
        index[unit]['Unlocked by'] = ' '.join(s[s.index('by') + 1:]).str.strip(' .')
    if 'Resources' in phrase:
        if 'GS' in phrase:
            if s[s.index('Resource') + 1] != 'GS':
                index[unit]['Resource'] = s[-2]
        else: index[unit]['Resource'] = s[-1]
    if 'Upgrades to' in phrase:
        s = phrase.replace('Upgrades to ', '').split(', ')
        index[unit]['Upgrades to'] = ', '.join([u for u in s if u in names])
    if 'Stats' in phrase:
        vals = [i for i in s if i.isnumeric()]
        stats = [i for i in s[1:] if i.isalpha()]
        if 'Build' in stats:
            b = stats.index('Build')
            stats[b: b + 2] = ['Build charges']
        index[unit]['Stats'] = ', '.join(['{}: {}'.format(stat, val) for stat, val in list(zip(stats, vals))]) 
    if 'Cost' in phrase:
        s = [c for i, c in enumerate(s) if c != 'GS' and s[i - 1] != 'GS']
        vals = [i for i in s if i.isnumeric()]
        costs = [i for i in s[1:] if i.strip('.').isalpha()]
        index[unit]['Cost'] = ', '.join(['{}: {}'.format(cost, val) for cost, val in list(zip(costs, vals))]) 
    if 'Notes' in phrase:
        index[unit]['Notes'] = phrase.replace('Notes ', '').replace(' .', '.')

index = dict()
units = [i for i in soups.values() if not ('Gathering Storm' in i[2] or 'Rise and Fall' in i[2])]
names = [i[0] for i in units]

for specs in units:
    index[specs[0]] = dict()
    for spec in specs[1:]:
        extract(specs[0], spec)

units = pd.DataFrame.from_dict(index, 'index')
units.index.name = 'Unit'
units.to_csv('Units.csv')

# =======
# Wonders
wds_url = 'https://civilization.fandom.com/wiki/List_of_wonders_in_Civ6'
response = requests.get(wds_url)
bs = BeautifulSoup(response.text, 'html.parser')

lines = []
for tr in bs.find_all('table')[0].find_all('tr')[1:]:
    imgs = tr.td.find_all('img')
    if not (len(imgs) > 1 and (imgs[1]['alt'] == 'GS-Only.png' or imgs[1]['alt'] == 'R&F-Only.png')):
        ls = []
        for td in tr.find_all('td')[:-2]:
            l = [i.text for i in td.find_all('a') if i.text and '[' not in i.text]
            ls.append(', '.join(l))
        ls = ls[:-1] + [tr.find_all('td')[3].text.strip()]
        
        p = ['' if i.img and ('RF' in i.img['alt'] or 'GS' in i.img['alt']) and 'Vanilla' not in i.text
             else i.text
             for i in tr.find_all('td')[-2].find('ul').find_all('li')]
        p = [i for i in p if i]
        p = ', '.join(p)
        p = p.replace('Vanilla and', 'Vanilla and R&F:').replace('  ', ' ')
        ls.append(p)
        
        q = tr.find_all('td')[-1].text.strip().split('\n')[0].replace('[5]', '').replace('[7]', '').replace('  ', ' ')
        ls.append(q)
        lines.append(ls)
        
cols = ['Wonder', 'Era', 'Requires', 'Cost', 'Effects', 'Placement']
wds = pd.DataFrame(lines, columns=cols).set_index('Wonder')
wds.loc['Hagia Sophia', 'Requires'] = 'Education'
wds['Era'] = wds['Era'] + ' Era'
wds[(wds == 'None') | (wds == '')] = None
wds.to_csv('Wonders.csv')

# ========
# Projects
projs_url = 'https://civilization.fandom.com/wiki/List_of_projects_in_Civ6'
response = requests.get(projs_url)
bs = BeautifulSoup(response.text, 'html.parser')

lines = []
for tbl in bs.find_all('table')[:-1]:
    for tr in tbl.find_all('tr')[1:]:
        imgs = tr.td.find_all('img')
        if not (len(imgs) > 1 and (imgs[1]['alt'] == 'GS-Only.png' or imgs[1]['alt'] == 'R&F-Only.png')):
            tds = tr.find_all('td')
            proj = tds[0].text.strip()
            proj = proj[:proj.index('[')] if '[' in proj else proj
            
            req = tds[1].text.strip()
            req = req[:req.index(' (')].strip() if '(' in req else req
            req = req.replace('\n', ', ').replace('Completed ', '')
            req = [i for i in req.split(' or ') if i not in ['Suguba', 'Ikanda', 'Cothon']]
            req = (' or '.join(req).replace(', Copacabana', '')
                   .str.replace(' or', ',').str.replace(',,', ',').str.replace('  ', ' ')
                   .str.strip(', ').str.replace('Seowon, ', ''))
            
            eff = tds[2].text.strip()
            eff = eff.replace('[1]', '').replace('  ', ' ').replace(' ( Powers city while ongoing)', '')
            eff = eff.split('\n')[:2]
            eff = '. '.join(eff)
            
            lines.append([proj] + [req] + [eff])
            
cols = ['Project', 'Requires', 'Effects']
projs = pd.DataFrame(lines, columns=cols)
projs.loc[0, 'Requires'] = None
projs = projs.set_index('Project').drop('Court Festival')

projs[(projs == '') | (projs == 'None')] = None
projs.to_csv('Projects.csv')

# =========
# Districts
dist_url = 'https://civilization.fandom.com/wiki/List_of_districts_in_Civ6'
response = requests.get(dist_url)
bs = BeautifulSoup(response.text, 'html.parser')

lines = []
for tr in bs.find_all('table')[0].find_all('tr')[1:]:
    imgs = tr.td.find_all('img')
    if not (len(imgs) > 1 and (imgs[1]['alt'] == 'GS-Only.png' or imgs[1]['alt'] == 'R&F-Only.png')):
        ls = []
        for td in tr.find_all('td')[:-1]:
            l = ['R&F' if i.img and 'R&F' in i.img['alt'] # R&F
                 else 'GS' if i.img and 'GS' in i.img['alt'] # GS
                 else i.img['alt'].strip('\.png') if i.img and 'Civ6' in i.img['alt'] # country
                 else i.text
                 for i in td.find_all('a')]
            l = [i for i in l if i]
            l = ['' if 'R&F' == (l + [''])[j + 1] or 'R&F' == i
                         or 'GS' == (l + [''])[j + 1] or 'GS' == i
                         or ('Civ6' in i and (l[j - 1] == 'R&F' or (l[j - 1] == 'GS')))
                 else i
                 for j, i in enumerate(l)]
            l = [i for i in l if i]
            l = [i + ' ({})'.format(l[j + 1].strip(' (Civ6)')) if 'Civ6' in (l + [''])[j + 1]
                 else '' if 'Civ6' in i
                 else i
                 for j, i in enumerate(l)]
            l = [i for i in l if i]
            l = ', '.join(l)
            ls.append(l)
        p = tr.find_all('td')[-1].text.strip()
        p = p.replace('\n', ' ').replace('\xa0', ' ').replace('(Vanilla and )', '').replace(' ,', ',').replace('( +', '(+').replace('  ', ' ').str.replace(' (Vanilla only)', '').str.replace(' (see below for )', '')
        ls.append(p)
        lines.append(ls)
        
cols = [i.strip() for i in bs.find_all('table')[0].tr.text.split('\n\n')]
dists = pd.DataFrame(lines, columns=cols).set_index('District')

dists[(dists == 'None') | (dists == '')] = None

uniqs = (dists['Unique District']
         .fillna('')
         .str.split(', ', expand=True)
         .stack()
         .reset_index(-1, drop=True)
         .str.strip(')')
         .str.split(' \(', expand=True)
         .dropna()
         .reset_index())

uniqs.columns = ['Replaces', 'District', 'Unique']
uniqs.set_index('District', inplace=True)
dists = pd.concat([dists, uniqs], sort=False).drop('Unique District', axis=1)
dists.columns = ['Buildings', 'Effects', 'Replaces', 'Unique to']
dists.to_csv('./Districts.csv')

# =============
# Civilizations
civz_url = 'https://civilization.fandom.com/wiki/Civilizations_(Civ6)'
response = requests.get(civz_url)
bs = BeautifulSoup(response.text, 'html.parser')

lines = []
for tr in bs.find_all('table')[0].find_all('tr')[1:]:
    imgs = tr.td.find_all('img')
    if not (len(imgs) > 1 and (imgs[1]['alt'] == 'GS-Only.png' or imgs[1]['alt'] == 'R&F-Only.png')):
        ls = []
        for td in tr.find_all('td'):
            l = ['' if i.img and ('R&F' in i.img['alt'] or 'GS' in i.img['alt'])
                 else i.text
                 for i in td.find_all('a')]
            l = [i for i in l if i and '[' not in i]
            l = ', '.join(l)
            ls.append(l)
        if len(ls) > 1:
            del ls[2]
            lines.append(ls)
        
cols = [i.strip() for i in bs.find_all('table')[0].tr.text.split('\n\n')]
del cols[2]
civzs = pd.DataFrame(lines, columns=cols).set_index('Civilization')
civzs.loc['Greek', 'Leader(s)'] = 'Pericles or Gorgo'

civzs[(civzs == 'None') | (civzs == '')] = None
civzs.to_csv('Civilizations.csv')

# ===========
# Governments
gov_url = 'https://civilization.fandom.com/wiki/Government_(Civ6)'
response = requests.get(gov_url)
bs = BeautifulSoup(response.text, 'html.parser')

for rf in bs.find('table').find_all('img', alt='R&F-Only.png'):
    rf.string = 'R&F'
for gs in bs.find('table').find_all('img', alt='GS-Only.png'):
    gs.string = 'GS'

lines = []
for tr in bs.find('table').find_all('tr')[1:]:
    l = ' '.join(list(tr.stripped_strings))
    if 'slots)' in l:
        era = l[:l.index(' (')] + ' Era'
        if 'Medieval' in era:
            mix = l[:l.index(' (')] + ' Era'
        slot = [i for i in l if i.isnumeric()][0]
    if sum([i.isnumeric() for i in l]) == 4:
        l = list(tr.stripped_strings)
        gov, civ = l[0], l[1]
        slots = zip(['Military', 'Economic', 'Diplomatic', 'Wildcard'], l[-4:])
        slots = ', '.join(['{}: {}'.format(s, v) for s, v in slots])
        if 'Chiefdom' in gov:
            lines.append([gov] + [civ] + [era] + [slot] + [slots] + [''] * 2)
        if civ in ['Exploration', 'Reformed Church']:
            era = mix.split('/')[1]
        elif 'Divine Right' in civ:
            era = mix.split('/')[0] + ' Era'
    if 'Effects' in l:
        l = tr.text.strip().replace('  ', ' ').split('\n')
        l = [i for i in l if not ('R&F' in i or 'GS' in i)]
        l = ' '.join(l)
        eff = l.replace('Effects: ', '')
    if 'Legacy Bonus' in l:
        l = tr.text.strip().replace('  ', ' ')
        bonus = l.replace('Legacy Bonus: ', '')
        lines.append([gov] + [civ] + [era] + [slot] + [slots] + [eff] + [bonus])    

cols = ['Government', 'Requires', 'Era', 'nSlots', 'Slots', 'Effects', 'Legacy Bonus']
govs = pd.DataFrame(lines, columns=cols)
govs[(govs == '') | (govs == 'None')] = None
govs.to_csv('Governments.csv', index=False)