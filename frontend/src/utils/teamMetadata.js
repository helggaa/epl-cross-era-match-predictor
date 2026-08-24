// Team branding metadata & iconic season nicknames

export const TEAM_METADATA = {
  'Arsenal': {
    primaryColor: '#EF0107',
    secondaryColor: '#063672',
    accentColor: '#9C824A',
    short: 'ARS',
    stadium: 'Emirates Stadium / Highbury',
    seasons: {
      '2003-2004': 'The Invincibles (Undefeated Champions)',
      '1997-1998': 'Wenger League & FA Cup Double',
      '2001-2002': 'Double Winners',
      '2022-2023': '84 Pts Title Contenders',
      '2023-2024': '89 Pts Runners-up',
      '2025-2026': 'Current Season',
    }
  },
  'Liverpool': {
    primaryColor: '#C8102E',
    secondaryColor: '#00B2A9',
    accentColor: '#F6EB61',
    short: 'LIV',
    stadium: 'Anfield',
    seasons: {
      '2019-2020': '99 Pts Premier League Champions',
      '2018-2019': '97 Pts & European Champions',
      '2021-2022': '92 Pts Season',
      '2013-2014': '101 Goals Scored SAS Campaign',
      '2008-2009': 'Torres & Gerrard Runners-up',
    }
  },
  'Manchester City': {
    primaryColor: '#6CABDD',
    secondaryColor: '#1C2C5B',
    accentColor: '#FFC659',
    short: 'MCI',
    stadium: 'Etihad Stadium',
    seasons: {
      '2017-2018': '100 Pts Centurions',
      '2018-2019': '98 Pts Domestic Treble',
      '2022-2023': 'Continental Treble Champions',
      '2023-2024': 'Historic 4-in-a-Row Champions',
      '2011-2012': 'Aguero 93:20 Title Season',
      '2013-2014': '102 Goals Title Season',
    }
  },
  'Man City': {
    primaryColor: '#6CABDD',
    secondaryColor: '#1C2C5B',
    accentColor: '#FFC659',
    short: 'MCI',
    stadium: 'Etihad Stadium',
    seasons: {
      '2017-2018': '100 Pts Centurions',
      '2018-2019': '98 Pts Domestic Treble',
      '2022-2023': 'Continental Treble Champions',
      '2023-2024': 'Historic 4-in-a-Row Champions',
      '2011-2012': 'Aguero 93:20 Title Season',
      '2025-2026': 'Current Season',
    }
  },
  'Manchester United': {
    primaryColor: '#DA291C',
    secondaryColor: '#FBE122',
    accentColor: '#000000',
    short: 'MUN',
    stadium: 'Old Trafford',
    seasons: {
      '1998-1999': 'Historic Treble Season',
      '2007-2008': 'Ronaldo 42-Goal & UCL Double',
      '1993-1994': 'Cantona League & Cup Double',
      '1999-2000': '97 Goals Title Campaign',
      '2006-2007': 'Rooney & Ronaldo Champions',
      '2012-2013': 'Ferguson 13th Title (Van Persie)',
    }
  },
  'Man United': {
    primaryColor: '#DA291C',
    secondaryColor: '#FBE122',
    accentColor: '#000000',
    short: 'MUN',
    stadium: 'Old Trafford',
    seasons: {
      '1998-1999': 'Historic Treble Season',
      '2007-2008': 'Ronaldo 42-Goal & UCL Double',
      '1993-1994': 'Cantona League & Cup Double',
      '1999-2000': '97 Goals Title Campaign',
      '2006-2007': 'Rooney & Ronaldo Champions',
      '2012-2013': 'Ferguson 13th Title (Van Persie)',
    }
  },
  'Chelsea': {
    primaryColor: '#034694',
    secondaryColor: '#EE242C',
    accentColor: '#DBA111',
    short: 'CHE',
    stadium: 'Stamford Bridge',
    seasons: {
      '2004-2005': '15 Goals Conceded Record Defense',
      '2005-2006': 'Back-to-Back Title Champions',
      '2009-2010': 'Ancelotti 103 Goals Record',
      '2014-2015': 'Mourinho Title Champions',
      '2016-2017': 'Conte 30-Win 3-4-3 Title',
    }
  },
  'Tottenham Hotspur': {
    primaryColor: '#132257',
    secondaryColor: '#FFFFFF',
    accentColor: '#7F9BB8',
    short: 'TOT',
    stadium: 'Tottenham Hotspur Stadium',
    seasons: {
      '2016-2017': '86 Pts Undefeated Home Record',
      '2015-2016': 'Pochettino Title Contenders',
      '2018-2019': 'Champions League Finalists',
    }
  },
  'Newcastle United': {
    primaryColor: '#241F20',
    secondaryColor: '#41B6E6',
    accentColor: '#F1BE48',
    short: 'NEW',
    stadium: 'St James\' Park',
    seasons: {
      '1995-1996': 'Keegan "The Entertainers"',
      '2001-2002': 'Sir Bobby Robson Campaign',
      '2022-2023': 'Champions League Qualification',
    }
  },
  'Aston Villa': {
    primaryColor: '#670E36',
    secondaryColor: '#95BFE5',
    accentColor: '#FEE12B',
    short: 'AVL',
    stadium: 'Villa Park',
    seasons: {
      '2023-2024': 'Emery Top 4 Qualification',
      '1992-1993': 'Inaugural Title Runners-up',
    }
  },
  'Leicester City': {
    primaryColor: '#003090',
    secondaryColor: '#FDBE11',
    accentColor: '#FFFFFF',
    short: 'LEI',
    stadium: 'King Power Stadium',
    seasons: {
      '2015-2016': '5000-1 Title Winning Campaign',
      '2019-2020': 'Vardy Golden Boot Season',
    }
  },
  'Blackburn Rovers': {
    primaryColor: '#005CA9',
    secondaryColor: '#E03A3E',
    accentColor: '#FFFFFF',
    short: 'BLA',
    stadium: 'Ewood Park',
    seasons: {
      '1994-1995': 'Shearer & Sutton SAS Title',
    }
  }
};

export const PRESET_MATCHUPS = [
  {
    id: 'invincibles-vs-centurions',
    title: 'The Invincibles vs The Centurions',
    subtitle: 'Arsenal 03-04 vs Man City 17-18',
    badge: 'All-Time Greats',
    teamA: 'Arsenal',
    seasonA: '2003-2004',
    teamB: 'Man City',
    seasonB: '2017-2018',
  },
  {
    id: 'treble-clash',
    title: 'Fergie Treble vs Pep Treble',
    subtitle: 'Man United 98-99 vs Man City 22-23',
    badge: 'Treble Winners',
    teamA: 'Man United',
    seasonA: '1998-1999',
    teamB: 'Man City',
    seasonB: '2022-2023',
  },
  {
    id: 'fortress-clash',
    title: '15-Goal Defense vs 99 Pts Attack',
    subtitle: 'Chelsea 04-05 vs Liverpool 19-20',
    badge: 'Defense vs Attack',
    teamA: 'Chelsea',
    seasonA: '2004-2005',
    teamB: 'Liverpool',
    seasonB: '2019-2020',
  },
  {
    id: 'miracle-vs-invincible',
    title: '5000-1 Miracle vs The Invincibles',
    subtitle: 'Leicester 15-16 vs Arsenal 03-04',
    badge: 'Fairy Tale vs Invincibles',
    teamA: 'Leicester City',
    seasonA: '2015-2016',
    teamB: 'Arsenal',
    seasonB: '2003-2004',
  },
  {
    id: 'ronaldo-vs-suarez',
    title: 'Ronaldo Double vs Suarez SAS',
    subtitle: 'Man United 07-08 vs Liverpool 13-14',
    badge: 'Peak Individual Eras',
    teamA: 'Man United',
    seasonA: '2007-2008',
    teamB: 'Liverpool',
    seasonB: '2013-2014',
  }
];

export function getTeamMeta(teamName) {
  if (!teamName) return { primaryColor: '#2563eb', secondaryColor: '#1e293b', short: 'PL' };
  for (const [name, meta] of Object.entries(TEAM_METADATA)) {
    if (teamName.toLowerCase().includes(name.toLowerCase()) || name.toLowerCase().includes(teamName.toLowerCase())) {
      return meta;
    }
  }
  return {
    primaryColor: '#1e293b',
    secondaryColor: '#0f172a',
    accentColor: '#38bdf8',
    short: teamName.slice(0, 3).toUpperCase(),
    stadium: 'Premier League Ground',
    seasons: {}
  };
}

export function getSeasonNickname(teamName, season) {
  const meta = getTeamMeta(teamName);
  if (meta && meta.seasons && meta.seasons[season]) {
    return meta.seasons[season];
  }
  const year = parseInt(season?.split('-')[0] || '2000', 10);
  if (year >= 2017) return 'Modern Tactical Era';
  if (year >= 2004) return 'Post-Invincibles Era';
  return 'Early Premier League Era';
}
