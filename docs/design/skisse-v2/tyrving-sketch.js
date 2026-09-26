/* Skisse-prototype: et utvalg av Tyrving 2014-parametre (fra athletics_scoring) og samme regler.
   Det ferdige grensesnittet skal kalle API-et, ikke regne selv (B-9). */
(function () {
  var DATA = {"G17":[{"id":"sprint_60m","name":"60 m","impl":null,"ft":"simple_quotient","m":"time","res":0.01,"min":false,"man":true,"p":{"h1000":7.3,"quotient":2.7}},{"id":"sprint_100m","name":"100 m","impl":null,"ft":"simple_quotient","m":"time","res":0.01,"min":false,"man":true,"p":{"h1000":11.5,"quotient":1.7}},{"id":"middle_600m","name":"600 m","impl":null,"ft":"simple_quotient","m":"time","res":0.1,"min":true,"man":false,"p":{"h1000":84,"quotient":2.6}},{"id":"middle_800m","name":"800 m","impl":null,"ft":"simple_quotient","m":"time","res":0.1,"min":true,"man":false,"p":{"h1000":117.5,"quotient":1.8}},{"id":"hurdles_110m","name":"110 m hekk","impl":"91,4cm/9,14m","ft":"simple_quotient","m":"time","res":0.01,"min":false,"man":true,"p":{"h1000":15.3,"quotient":1}},{"id":"hurdles_110m","name":"110 m hekk","impl":"100,0cm/9,14m","ft":"simple_quotient","m":"time","res":0.01,"min":false,"man":true,"p":{"h1000":15.8,"quotient":1}},{"id":"high_jump","name":"Høyde","impl":null,"ft":"simple_quotient","m":"distance","res":0.01,"min":false,"man":false,"p":{"h1000":1.93,"quotient":7}},{"id":"long_jump","name":"Lengde","impl":null,"ft":"simple_quotient","m":"distance","res":0.01,"min":false,"man":false,"p":{"h1000":6.6,"quotient":2}},{"id":"shot_put","name":"Kule","impl":"5kg","ft":"three_interval","m":"distance","res":0.01,"min":false,"man":false,"p":{"h1000":15.8,"f1":0.3,"f2":0.6,"f3":1.2}},{"id":"javelin","name":"Spyd","impl":"0,7kg","ft":"three_interval","m":"distance","res":0.01,"min":false,"man":false,"p":{"h1000":60,"f1":0.1,"f2":0.2,"f3":0.4}}],"J17":[{"id":"sprint_60m","name":"60 m","impl":null,"ft":"simple_quotient","m":"time","res":0.01,"min":false,"man":true,"p":{"h1000":8,"quotient":2.7}},{"id":"sprint_100m","name":"100 m","impl":null,"ft":"simple_quotient","m":"time","res":0.01,"min":false,"man":true,"p":{"h1000":12.6,"quotient":1.6}},{"id":"middle_600m","name":"600 m","impl":null,"ft":"simple_quotient","m":"time","res":0.1,"min":true,"man":false,"p":{"h1000":96,"quotient":2.4}},{"id":"middle_800m","name":"800 m","impl":null,"ft":"simple_quotient","m":"time","res":0.1,"min":true,"man":false,"p":{"h1000":134,"quotient":1.5}},{"id":"high_jump","name":"Høyde","impl":null,"ft":"simple_quotient","m":"distance","res":0.01,"min":false,"man":false,"p":{"h1000":1.66,"quotient":7.5}},{"id":"long_jump","name":"Lengde","impl":null,"ft":"simple_quotient","m":"distance","res":0.01,"min":false,"man":false,"p":{"h1000":5.55,"quotient":2.1}},{"id":"shot_put","name":"Kule","impl":"3kg","ft":"three_interval","m":"distance","res":0.01,"min":false,"man":false,"p":{"h1000":12.6,"f1":0.3,"f2":0.6,"f3":1.2}},{"id":"javelin","name":"Spyd","impl":"0,5kg","ft":"three_interval","m":"distance","res":0.01,"min":false,"man":false,"p":{"h1000":42,"f1":0.13,"f2":0.25,"f3":0.5}}],"G15":[{"id":"sprint_60m","name":"60 m","impl":null,"ft":"simple_quotient","m":"time","res":0.01,"min":false,"man":true,"p":{"h1000":7.55,"quotient":2.7}},{"id":"sprint_100m","name":"100 m","impl":null,"ft":"simple_quotient","m":"time","res":0.01,"min":false,"man":true,"p":{"h1000":11.95,"quotient":1.7}},{"id":"middle_600m","name":"600 m","impl":null,"ft":"simple_quotient","m":"time","res":0.1,"min":true,"man":false,"p":{"h1000":88.5,"quotient":2.6}},{"id":"middle_800m","name":"800 m","impl":null,"ft":"simple_quotient","m":"time","res":0.1,"min":true,"man":false,"p":{"h1000":124,"quotient":1.8}},{"id":"high_jump","name":"Høyde","impl":null,"ft":"simple_quotient","m":"distance","res":0.01,"min":false,"man":false,"p":{"h1000":1.8,"quotient":7}},{"id":"long_jump","name":"Lengde","impl":null,"ft":"simple_quotient","m":"distance","res":0.01,"min":false,"man":false,"p":{"h1000":6.15,"quotient":2}},{"id":"shot_put","name":"Kule","impl":"4kg","ft":"three_interval","m":"distance","res":0.01,"min":false,"man":false,"p":{"h1000":15.3,"f1":0.3,"f2":0.6,"f3":1.2}},{"id":"javelin","name":"Spyd","impl":"0,6kg","ft":"three_interval","m":"distance","res":0.01,"min":false,"man":false,"p":{"h1000":52,"f1":0.1,"f2":0.2,"f3":0.4}}],"J15":[{"id":"sprint_60m","name":"60 m","impl":null,"ft":"simple_quotient","m":"time","res":0.01,"min":false,"man":true,"p":{"h1000":8.15,"quotient":2.7}},{"id":"sprint_100m","name":"100 m","impl":null,"ft":"simple_quotient","m":"time","res":0.01,"min":false,"man":true,"p":{"h1000":12.9,"quotient":1.6}},{"id":"middle_600m","name":"600 m","impl":null,"ft":"simple_quotient","m":"time","res":0.1,"min":true,"man":false,"p":{"h1000":98.5,"quotient":2.4}},{"id":"middle_800m","name":"800 m","impl":null,"ft":"simple_quotient","m":"time","res":0.1,"min":true,"man":false,"p":{"h1000":138.5,"quotient":1.5}},{"id":"high_jump","name":"Høyde","impl":null,"ft":"simple_quotient","m":"distance","res":0.01,"min":false,"man":false,"p":{"h1000":1.61,"quotient":7.5}},{"id":"long_jump","name":"Lengde","impl":null,"ft":"simple_quotient","m":"distance","res":0.01,"min":false,"man":false,"p":{"h1000":5.36,"quotient":2.1}},{"id":"shot_put","name":"Kule","impl":"3kg","ft":"three_interval","m":"distance","res":0.01,"min":false,"man":false,"p":{"h1000":11.4,"f1":0.3,"f2":0.6,"f3":1.2}},{"id":"javelin","name":"Spyd","impl":"0,5kg","ft":"three_interval","m":"distance","res":0.01,"min":false,"man":false,"p":{"h1000":38.0,"f1":0.13,"f2":0.25,"f3":0.5}}],"G13":[{"id":"sprint_60m","name":"60 m","impl":null,"ft":"simple_quotient","m":"time","res":0.01,"min":false,"man":true,"p":{"h1000":8,"quotient":2.7}},{"id":"sprint_100m","name":"100 m","impl":null,"ft":"simple_quotient","m":"time","res":0.01,"min":false,"man":true,"p":{"h1000":12.8,"quotient":1.7}},{"id":"middle_600m","name":"600 m","impl":null,"ft":"simple_quotient","m":"time","res":0.1,"min":true,"man":false,"p":{"h1000":94.5,"quotient":2.6}},{"id":"hurdles_60m","name":"60 m hekk","impl":"76,2cm/7,5m","ft":"simple_quotient","m":"time","res":0.01,"min":false,"man":true,"p":{"h1000":9.8,"quotient":2}},{"id":"high_jump","name":"Høyde","impl":null,"ft":"simple_quotient","m":"distance","res":0.01,"min":false,"man":false,"p":{"h1000":1.61,"quotient":7}},{"id":"long_jump","name":"Lengde","impl":null,"ft":"simple_quotient","m":"distance","res":0.01,"min":false,"man":false,"p":{"h1000":5.35,"quotient":2}},{"id":"shot_put","name":"Kule","impl":"3kg","ft":"three_interval","m":"distance","res":0.01,"min":false,"man":false,"p":{"h1000":13.5,"f1":0.3,"f2":0.6,"f3":1.2}},{"id":"javelin","name":"Spyd","impl":"0,4kg","ft":"three_interval","m":"distance","res":0.01,"min":false,"man":false,"p":{"h1000":45,"f1":0.1,"f2":0.2,"f3":0.4}}],"J13":[{"id":"sprint_60m","name":"60 m","impl":null,"ft":"simple_quotient","m":"time","res":0.01,"min":false,"man":true,"p":{"h1000":8.4,"quotient":2.7}},{"id":"sprint_100m","name":"100 m","impl":null,"ft":"simple_quotient","m":"time","res":0.01,"min":false,"man":true,"p":{"h1000":13.4,"quotient":1.6}},{"id":"middle_600m","name":"600 m","impl":null,"ft":"simple_quotient","m":"time","res":0.1,"min":true,"man":false,"p":{"h1000":102,"quotient":2.4}},{"id":"hurdles_60m","name":"60 m hekk","impl":"76,2cm/7,5m","ft":"simple_quotient","m":"time","res":0.01,"min":false,"man":true,"p":{"h1000":10.1,"quotient":1.9}},{"id":"high_jump","name":"Høyde","impl":null,"ft":"simple_quotient","m":"distance","res":0.01,"min":false,"man":false,"p":{"h1000":1.52,"quotient":7.5}},{"id":"long_jump","name":"Lengde","impl":null,"ft":"simple_quotient","m":"distance","res":0.01,"min":false,"man":false,"p":{"h1000":5,"quotient":2.1}},{"id":"shot_put","name":"Kule","impl":"2kg","ft":"three_interval","m":"distance","res":0.01,"min":false,"man":false,"p":{"h1000":11.2,"f1":0.3,"f2":0.6,"f3":1.2}},{"id":"javelin","name":"Spyd","impl":"0,4kg","ft":"three_interval","m":"distance","res":0.01,"min":false,"man":false,"p":{"h1000":36,"f1":0.13,"f2":0.25,"f3":0.5}}],"G11":[{"id":"sprint_40m","name":"40 m","impl":null,"ft":"simple_quotient","m":"time","res":0.01,"min":false,"man":false,"p":{"h1000":6.4,"quotient":3.5}},{"id":"sprint_60m","name":"60 m","impl":null,"ft":"simple_quotient","m":"time","res":0.01,"min":false,"man":true,"p":{"h1000":8.8,"quotient":2.7}},{"id":"middle_600m","name":"600 m","impl":null,"ft":"simple_quotient","m":"time","res":0.1,"min":true,"man":false,"p":{"h1000":105,"quotient":2.6}},{"id":"hurdles_60m","name":"60 m hekk","impl":"68,0cm/6,5m","ft":"simple_quotient","m":"time","res":0.01,"min":false,"man":true,"p":{"h1000":10.5,"quotient":2}},{"id":"high_jump","name":"Høyde","impl":null,"ft":"simple_quotient","m":"distance","res":0.01,"min":false,"man":false,"p":{"h1000":1.38,"quotient":7}},{"id":"long_jump","name":"Lengde","impl":null,"ft":"simple_quotient","m":"distance","res":0.01,"min":false,"man":false,"p":{"h1000":4.55,"quotient":2}},{"id":"shot_put","name":"Kule","impl":"2kg","ft":"three_interval","m":"distance","res":0.01,"min":false,"man":false,"p":{"h1000":10.5,"f1":0.3,"f2":0.6,"f3":1.2}},{"id":"javelin","name":"Spyd","impl":"0,4kg","ft":"three_interval","m":"distance","res":0.01,"min":false,"man":false,"p":{"h1000":32,"f1":0.1,"f2":0.2,"f3":0.4}}],"J11":[{"id":"sprint_40m","name":"40 m","impl":null,"ft":"simple_quotient","m":"time","res":0.01,"min":false,"man":false,"p":{"h1000":6.4,"quotient":3.5}},{"id":"sprint_60m","name":"60 m","impl":null,"ft":"simple_quotient","m":"time","res":0.01,"min":false,"man":true,"p":{"h1000":8.85,"quotient":2.7}},{"id":"middle_600m","name":"600 m","impl":null,"ft":"simple_quotient","m":"time","res":0.1,"min":true,"man":false,"p":{"h1000":110,"quotient":2.4}},{"id":"hurdles_60m","name":"60 m hekk","impl":"68,0cm/6,5m","ft":"simple_quotient","m":"time","res":0.01,"min":false,"man":true,"p":{"h1000":10.9,"quotient":1.9}},{"id":"high_jump","name":"Høyde","impl":null,"ft":"simple_quotient","m":"distance","res":0.01,"min":false,"man":false,"p":{"h1000":1.34,"quotient":7.5}},{"id":"long_jump","name":"Lengde","impl":null,"ft":"simple_quotient","m":"distance","res":0.01,"min":false,"man":false,"p":{"h1000":4.35,"quotient":2.1}},{"id":"shot_put","name":"Kule","impl":"2kg","ft":"three_interval","m":"distance","res":0.01,"min":false,"man":false,"p":{"h1000":8.8,"f1":0.3,"f2":0.6,"f3":1.2}},{"id":"javelin","name":"Spyd","impl":"0,4kg","ft":"three_interval","m":"distance","res":0.01,"min":false,"man":false,"p":{"h1000":27,"f1":0.13,"f2":0.25,"f3":0.5}}]};
  var MANUAL = { 60: 20, 80: 20, 300: 20, 100: 24, 110: 24, 200: 24, 400: 14 }; // hundredeler
  // Rimelig område, relativt til 1000p-nivået. Utenfor vises ikke poeng (typisk underveis i inntastingen).
  var RANGE = { time: [0.6, 3.0], distance: [0.2, 1.6] };
  function fmtValue(e, cents) {
    if (e.m === 'distance') return fmt((cents / 100).toFixed(2)) + ' m';
    if (e.min) return Math.floor(cents / 6000) + ':' + fmt(((cents % 6000) / 100).toFixed(1)).padStart(4, '0');
    return fmt((cents / 100).toFixed(2)) + ' s';
  }
  function rangeOf(e) {
    var r = RANGE[e.m], h = e.p.h1000 * 100;
    var lo = Math.ceil(h * r[0]), hi = Math.floor(h * r[1]);
    if (e.m === 'time' && e.min) { lo = Math.ceil(lo / 10) * 10; hi = Math.floor(hi / 10) * 10; }
    return { lo: lo, hi: hi, text: fmtValue(e, lo).replace(/ [ms]$/, '') + '–' + fmtValue(e, hi) };
  }
  function fmt(n) { return String(n).replace('.', window.APP_DECIMAL || ','); }
  function trim(x) { var s = x.toFixed(4).replace(/0+$/, '').replace(/\.$/, ''); return fmt(s); }
  function toCents(text) {
    var s = String(text == null ? '' : text).trim().replace(',', '.');
    if (!/^\d+(\.\d+)?$/.test(s)) return null;
    var parts = s.split('.');
    var dec = ((parts[1] || '') + '00').slice(0, 2);
    return parseInt(parts[0], 10) * 100 + parseInt(dec, 10);
  }
  function key(e) { return e.id + '|' + (e.impl || ''); }
  function distanceOf(id) { var m = id.match(/_(\d+)m$/); return m ? parseInt(m[1], 10) : null; }
  function implLabel(impl) { return impl ? impl.replace(/\//g, ' / ').replace(/kg/g, ' kg').replace(/cm/g, ' cm').replace(/(\d)m\b/g, '$1 m') : ''; }
  function inputHint(e) {
    if (e.m === 'distance') return 'Meter med centimeter, f.eks. 5,20';
    if (e.min) return 'Tideler. Hundredeler strykes (2:04,56 regnes som 2:04,5)';
    return 'Sekunder med hundredeler, f.eks. ' + fmt(e.p.h1000.toFixed(2));
  }
  function calc(e, v1, v2, manual) {
    var cents;
    if (e.m === 'distance') { cents = toCents(v1); }
    else if (e.min) {
      var mins = String(v1 || '').trim() === '' ? 0 : parseInt(v1, 10);
      var secs = toCents(v2);
      if (isNaN(mins) || secs === null) return { ok: false, error: 'Tast inn minutter og sekunder' };
      cents = mins * 6000 + secs;
    } else { cents = toCents(v1); }
    if (cents === null || cents <= 0) return { ok: false, error: 'Tast inn et resultat' };
    var range = rangeOf(e);
    var plausible = cents >= range.lo && cents <= range.hi;
    var steps = [];
    if (e.m === 'time' && manual && e.man) {
      var add = MANUAL[distanceOf(e.id)];
      cents += add;
      steps.push((window.APP_LANG === 'en' ? 'Hand timing: +' : 'Manuell tid: +') + fmt((add / 100).toFixed(2)) + ' s');
    }
    if (e.m === 'time' && e.min) {
      var before = cents; cents = Math.floor(cents / 10) * 10;
      if (before !== cents) steps.push(window.APP_LANG === 'en' ? 'Hundredths dropped' : 'Hundredeler strøket');
    }
    var p = e.p, scaleUnits, h, r, P10k, detail;
    if (e.ft === 'three_interval') {
      var H = Math.round(p.h1000 * 1000), R = cents * 10, E = H * 8 / 10;   // tusendels meter
      var f1 = Math.round(p.f1 * 1000), f2 = Math.round(p.f2 * 1000), f3 = Math.round(p.f3 * 1000);
      var Hc = Math.round(p.h1000 * 100), Rc = cents, Ec = Hc * 0.8;
      if (R >= H) { P10k = 1000 * 10000 + (R - H) * f1; detail = '1000 + (' + Rc + ' − ' + Hc + ') × ' + fmt(p.f1); }
      else if (R >= E) { P10k = 1000 * 10000 - (H - R) * f2; detail = '1000 − (' + Hc + ' − ' + Rc + ') × ' + fmt(p.f2); }
      else { P10k = 1000 * 10000 - ((H - E) * f2 + (E - R) * f3); detail = '1000 − ((' + Hc + ' − ' + fmt(Ec) + ') × ' + fmt(p.f2) + ' + (' + fmt(Ec) + ' − ' + Rc + ') × ' + fmt(p.f3) + ')'; }
      P10k = P10k / 10000;
    } else {
      var q = Math.round(p.quotient * 1000);
      if (e.m === 'time' && e.min) { h = Math.round(p.h1000 * 10); r = cents / 10; }
      else { h = Math.round(p.h1000 * 100); r = cents; }
      var sign = e.m === 'time' ? 1 : -1;
      var raw = 1000 * 1000 + sign * (h - r) * q;
      P10k = raw / 1000;
      detail = '1000 ' + (sign > 0 ? '+' : '−') + ' (' + h + ' − ' + r + ') × ' + fmt(p.quotient);
    }
    var points = Math.max(0, Math.floor(P10k + 1e-9));
    var used = e.m === 'distance' ? fmt((cents / 100).toFixed(2)) + ' m'
      : e.min ? Math.floor(cents / 6000) + ':' + fmt(((cents % 6000) / 100).toFixed(1)).padStart(4, '0')
      : fmt((cents / 100).toFixed(2)) + ' s';
    return { ok: true, points: points, detail: detail + ' = ' + trim(P10k) + ' → ' + points, used: used, steps: steps, plausible: plausible, range: range.text };
  }
  window.TYRV = { DATA: DATA, key: key, calc: calc, implLabel: implLabel, inputHint: inputHint, fmt: fmt, rangeOf: rangeOf };
})();
