// Dati PubChem Periodic Table (PUG-REST), verificati il 25 agosto 2026.
// Campi: Z | massa atomica (u) | stato standard | fusione (K) |
// ebollizione (K) | stati di ossidazione | configurazione elettronica.
const propertyRows = `
1|1.0080|Gas|13.81|20.28|+1, -1|1s1
2|4.00260|Gas|0.95|4.22|0|1s2
3|7.0|Solid|453.65|1615|+1|[He]2s1
4|9.012183|Solid|1560|2744|+2|[He]2s2
5|10.81|Solid|2348|4273|+3|[He]2s2 2p1
6|12.011|Solid|3823|4098|+4, +2, -4|[He]2s2 2p2
7|14.007|Gas|63.15|77.36|+5, +4, +3, +2, +1, -1, -2, -3|[He] 2s2 2p3
8|15.999|Gas|54.36|90.2|-2|[He]2s2 2p4
9|18.99840316|Gas|53.53|85.03|-1|[He]2s2 2p5
10|20.180|Gas|24.56|27.07|0|[He]2s2 2p6
11|22.9897693|Solid|370.95|1156|+1|[Ne]3s1
12|24.305|Solid|923|1363|+2|[Ne]3s2
13|26.981538|Solid|933.437|2792|+3|[Ne]3s2 3p1
14|28.085|Solid|1687|3538|+4, +2, -4|[Ne]3s2 3p2
15|30.97376200|Solid|317.3|553.65|+5, +3, -3|[Ne]3s2 3p3
16|32.07|Solid|388.36|717.75|+6, +4, -2|[Ne]3s2 3p4
17|35.45|Gas|171.65|239.11|+7, +5, +1, -1|[Ne]3s2 3p5
18|39.9|Gas|83.8|87.3|0|[Ne]3s2 3p6
19|39.0983|Solid|336.53|1032|+1|[Ar]4s1
20|40.08|Solid|1115|1757|+2|[Ar]4s2
21|44.95591|Solid|1814|3109|+3|[Ar]4s2 3d1
22|47.867|Solid|1941|3560|+4, +3, +2|[Ar]4s2 3d2
23|50.9415|Solid|2183|3680|+5, +4, +3, +2|[Ar]4s2 3d3
24|51.996|Solid|2180|2944|+6, +3, +2|[Ar]3d5 4s1
25|54.93804|Solid|1519|2334|+7, +4, +3, +2|[Ar]4s2 3d5
26|55.84|Solid|1811|3134|+3, +2|[Ar]4s2 3d6
27|58.93319|Solid|1768|3200|+3, +2|[Ar]4s2 3d7
28|58.693|Solid|1728|3186|+3, +2|[Ar]4s2 3d8
29|63.55|Solid|1357.77|2835|+2, +1|[Ar]4s1 3d10
30|65.4|Solid|692.68|1180|+2|[Ar]4s2 3d10
31|69.723|Solid|302.91|2477|+3|[Ar]4s2 3d10 4p1
32|72.63|Solid|1211.4|3106|+4, +2|[Ar]4s2 3d10 4p2
33|74.92159|Solid|1090|887|+5, +3, -3|[Ar]4s2 3d10 4p3
34|78.97|Solid|493.65|958|+6, +4, -2|[Ar]4s2 3d10 4p4
35|79.90|Liquid|265.95|331.95|+5, +1, -1|[Ar]4s2 3d10 4p5
36|83.80|Gas|115.79|119.93|0|[Ar]4s2 3d10 4p6
37|85.468|Solid|312.46|961|+1|[Kr]5s1
38|87.62|Solid|1050|1655|+2|[Kr]5s2
39|88.90584|Solid|1795|3618|+3|[Kr]5s2 4d1
40|91.22|Solid|2128|4682|+4|[Kr]5s2 4d2
41|92.90637|Solid|2750|5017|+5, +3|[Kr]5s1 4d4
42|95.95|Solid|2896|4912|+6|[Kr]5s1 4d5
43|96.90636|Solid|2430|4538|+7, +6, +4|[Kr]5s2 4d5
44|101.1|Solid|2607|4423|+3|[Kr]5s1 4d7
45|102.9055|Solid|2237|3968|+3|[Kr]5s1 4d8
46|106.42|Solid|1828.05|3236|+3, +2|[Kr]4d10
47|107.868|Solid|1234.93|2435|+1|[Kr]5s1 4d10
48|112.41|Solid|594.22|1040|+2|[Kr]5s2 4d10
49|114.818|Solid|429.75|2345|+3|[Kr]5s2 4d10 5p1
50|118.71|Solid|505.08|2875|+4, +2|[Kr]5s2 4d10 5p2
51|121.760|Solid|903.78|1860|+5, +3, -3|[Kr]5s2 4d10 5p3
52|127.6|Solid|722.66|1261|+6, +4, -2|[Kr]5s2 4d10 5p4
53|126.9045|Solid|386.85|457.55|+7, +5, +1, -1|[Kr]5s2 4d10 5p5
54|131.29|Gas|161.36|165.03|0|[Kr]5s2 4d10 5p6
55|132.9054520|Solid|301.59|944|+1|[Xe]6s1
56|137.33|Solid|1000|2170|+2|[Xe]6s2
57|138.9055|Solid|1191|3737|+3|[Xe]6s2 5d1
58|140.116|Solid|1071|3697|+4, +3|[Xe]6s2 4f1 5d1
59|140.90766|Solid|1204|3793|+3|[Xe]6s2 4f3
60|144.24|Solid|1294|3347|+3|[Xe]6s2 4f4
61|144.91276|Solid|1315|3273|+3|[Xe]6s2 4f5
62|150.4|Solid|1347|2067|+3, +2|[Xe]6s2 4f6
63|151.964|Solid|1095|1802|+3, +2|[Xe]6s2 4f7
64|157.25|Solid|1586|3546|+3|[Xe]6s2 4f7 5d1
65|158.92535|Solid|1629|3503|+3|[Xe]6s2 4f9
66|162.500|Solid|1685|2840|+3|[Xe]6s2 4f10
67|164.93033|Solid|1747|2973|+3|[Xe]6s2 4f11
68|167.26|Solid|1802|3141|+3|[Xe]6s2 4f12
69|168.93422|Solid|1818|2223|+3|[Xe]6s2 4f13
70|173.05|Solid|1092|1469|+3, +2|[Xe]6s2 4f14
71|174.9667|Solid|1936|3675|+3|[Xe]6s2 4f14 5d1
72|178.49|Solid|2506|4876|+4|[Xe]6s2 4f14 5d2
73|180.9479|Solid|3290|5731|+5|[Xe]6s2 4f14 5d3
74|183.84|Solid|3695|5828|+6|[Xe]6s2 4f14 5d4
75|186.207|Solid|3459|5869|+7, +6, +4|[Xe]6s2 4f14 5d5
76|190.2|Solid|3306|5285|+4, +3|[Xe]6s2 4f14 5d6
77|192.22|Solid|2719|4701|+4, +3|[Xe]6s2 4f14 5d7
78|195.08|Solid|2041.55|4098|+4, +2|[Xe]6s1 4f14 5d9
79|196.96657|Solid|1337.33|3129|+3, +1|[Xe]6s1 4f14 5d10
80|200.59|Liquid|234.32|629.88|+2, +1|[Xe]6s2 4f14 5d10
81|204.383|Solid|577|1746|+3, +1|[Xe]6s2 4f14 5d10 6p1
82|207|Solid|600.61|2022|+4, +2|[Xe]6s2 4f14 5d10 6p2
83|208.98040|Solid|544.55|1837|+5, +3|[Xe]6s2 4f14 5d10 6p3
84|208.98243|Solid|527|1235|+4, +2|[Xe]6s2 4f14 5d10 6p4
85|209.98715|Solid|575||7, 5, 3, 1, -1|[Xe]6s2 4f14 5d10 6p5
86|222.01758|Gas|202|211.45|0|[Xe]6s2 4f14 5d10 6p6
87|223.01973|Solid|300||+1|[Rn]7s1
88|226.02541|Solid|973|1413|+2|[Rn]7s2
89|227.02775|Solid|1324|3471|+3|[Rn]7s2 6d1
90|232.038|Solid|2023|5061|+4|[Rn]7s2 6d2
91|231.03588|Solid|1845||+5, +4|[Rn]7s2 5f2 6d1
92|238.0289|Solid|1408|4404|+6, +5, +4, +3|[Rn]7s2 5f3 6d1
93|237.048172|Solid|917|4175|+6, +5, +4, +3|[Rn]7s2 5f4 6d1
94|244.06420|Solid|913|3501|+6, +5, +4, +3|[Rn]7s2 5f6
95|243.061380|Solid|1449|2284|+6, +5, +4, +3|[Rn]7s2 5f7
96|247.07035|Solid|1618|3400|+3|[Rn]7s2 5f7 6d1
97|247.07031|Solid|1323||+4, +3|[Rn]7s2 5f9
98|251.07959|Solid|1173||+3|[Rn]7s2 5f10
99|252.0830|Solid|1133||+3|[Rn]7s2 5f11
100|257.09511|Solid|1800||+3|[Rn] 5f12 7s2
101|258.09843|Solid|1100||+3, +2|[Rn]7s2 5f13
102|259.10100|Solid|1100||+3, +2|[Rn]7s2 5f14
103|266.120|Solid|1900||+3|[Rn]7s2 5f14 6d1
104|267.122|Solid|||+4|[Rn]7s2 5f14 6d2
105|268.126|Solid|||5, 4, 3|[Rn]7s2 5f14 6d3
106|269.128|Solid|||6, 5, 4, 3, 0|[Rn]7s2 5f14 6d4
107|270.133|Solid|||7, 5, 4, 3|[Rn]7s2 5f14 6d5
108|269.1336|Solid|||8, 6, 5, 4, 3, 2|[Rn]7s2 5f14 6d6
109|277.154|Solid|||9, 8, 6, 4, 3, 1|[Rn]7s2 5f14 6d7 (calculated)
110|282.166|Expected to be a Solid|||8, 6, 4, 2, 0|[Rn]7s2 5f14 6d8 (predicted)
111|282.169|Expected to be a Solid|||5, 3, 1, -1|[Rn]7s2 5f14 6d9 (predicted)
112|286.179|Expected to be a Solid|||2, 1, 0|[Rn]7s2 5f14 6d10 (predicted)
113|286.182|Expected to be a Solid||||[Rn]5f14 6d10 7s2 7p1 (predicted)
114|290.192|Expected to be a Solid|||6, 4, 2, 1, 0|[Rn]7s2 7p2 5f14 6d10 (predicted)
115|290.196|Expected to be a Solid|||3, 1|[Rn]7s2 7p3 5f14 6d10 (predicted)
116|293.205|Expected to be a Solid|||+4, +2, -2|[Rn]7s2 7p4 5f14 6d10 (predicted)
117|294.211|Expected to be a Solid|||+5, +3, +1, -1|[Rn]7s2 7p5 5f14 6d10 (predicted)
118|295.216|Expected to be a Gas|||+6, +4, +2, +1, 0, -1|[Rn]7s2 7p6 5f14 6d10 (predicted)
`;

const stateLabels = {
  Gas: 'Gassoso',
  Solid: 'Solido',
  Liquid: 'Liquido',
  'Expected to be a Solid': 'Solido (previsto)',
  'Expected to be a Gas': 'Gassoso (previsto)'
};

const valencesFromOxidation = oxidationStates => {
  if (!oxidationStates) return [];
  const values = [...new Set((oxidationStates.match(/[-+]?\d+/g) || []).map(value => Math.abs(Number(value))))];
  return values.sort((a, b) => a - b);
};

export const elementPropertiesByAtomicNumber = new Map(propertyRows.trim().split('\n').map(row => {
  const [number, atomicMass, rawState, melting, boiling, oxidationStates, electronConfiguration] = row.split('|');
  const atomicNumber = Number(number);
  return [atomicNumber, {
    atomicMass,
    standardState: stateLabels[rawState] || rawState || 'Non determinato',
    stateIsPredicted: rawState.startsWith('Expected'),
    meltingKelvin: melting ? Number(melting) : null,
    boilingKelvin: boiling ? Number(boiling) : null,
    oxidationStates: oxidationStates || '',
    valences: valencesFromOxidation(oxidationStates),
    electronConfiguration,
    artificial: atomicNumber === 43 || atomicNumber === 61 || atomicNumber >= 93
  }];
}));
