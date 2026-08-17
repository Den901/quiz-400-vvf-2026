const idOf = item => String(item?.id ?? '');

const seedNumber = value => {
  let hash = 2166136261;
  for (const char of String(value)) {
    hash ^= char.charCodeAt(0);
    hash = Math.imul(hash, 16777619);
  }
  return hash >>> 0;
};

const seededRandom = seed => {
  let state = seedNumber(seed) || 1;
  return () => {
    state += 0x6D2B79F5;
    let value = state;
    value = Math.imul(value ^ value >>> 15, value | 1);
    value ^= value + Math.imul(value ^ value >>> 7, value | 61);
    return ((value ^ value >>> 14) >>> 0) / 4294967296;
  };
};

const shuffle = (items, seed) => {
  const result = [...items];
  const random = seededRandom(seed);
  for (let index = result.length - 1; index > 0; index -= 1) {
    const other = Math.floor(random() * (index + 1));
    [result[index], result[other]] = [result[other], result[index]];
  }
  return result;
};

const uniqueQuestions = source => {
  const seen = new Set();
  return source.filter(question => {
    const id = idOf(question);
    if (!id || seen.has(id)) return false;
    seen.add(id);
    return true;
  });
};

function migratedSeen(source, rotation) {
  if (Array.isArray(rotation?.seen)) return rotation.seen.map(String);
  if (!rotation?.seed || !Number.isFinite(Number(rotation?.cursor))) return [];
  return shuffle(source, rotation.seed)
    .slice(0, Math.max(0, Number(rotation.cursor)))
    .map(idOf);
}

/**
 * Rotazione senza ripetizioni: ogni domanda viene proposta una sola volta
 * prima di iniziare un nuovo ciclo, anche se la sorgente viene aggiornata.
 */
export function selectRotatingQuestions(source, count, rotation = {}, seed = '') {
  const questions = uniqueQuestions(source);
  const target = Math.min(Math.max(0, Math.floor(Number(count) || 0)), questions.length);
  if (!target) return {selected: [], rotation: {...rotation, version: 2, seen: []}};

  const validIds = new Set(questions.map(idOf));
  const seen = new Set(migratedSeen(questions, rotation).filter(id => validIds.has(id)));
  const used = new Set();
  const selected = [];
  let cycle = Math.max(0, Math.floor(Number(rotation?.cycle) || 0));

  while (selected.length < target) {
    let available = questions.filter(question => !seen.has(idOf(question)) && !used.has(idOf(question)));
    if (!available.length) {
      cycle += 1;
      seen.clear();
      available = questions.filter(question => !used.has(idOf(question)));
      if (!available.length) break;
    }
    const deck = shuffle(available, `${seed}|rotation-cycle-${cycle}|${selected.length}`);
    const take = deck.slice(0, target - selected.length);
    for (const question of take) {
      const id = idOf(question);
      selected.push(question);
      used.add(id);
      seen.add(id);
    }
  }

  return {
    selected,
    rotation: {
      version: 2,
      cycle,
      seen: [...seen],
      size: questions.length,
      updatedAt: new Date().toISOString()
    }
  };
}

const normalizedStatus = status => ['known', 'review', 'unknown'].includes(status) ? status : 'unanswered';

export function applyLearningOutcome(progress, {blank = false, correct = false}, countAttempt = true, at = new Date().toISOString()) {
  const result = progress;
  if (blank) {
    if (countAttempt) result.skipped = (Number(result.skipped) || 0) + 1;
    if (!result.attempts) result.status = 'unanswered';
  } else if (correct) {
    if (countAttempt) {
      result.attempts = (Number(result.attempts) || 0) + 1;
      result.correct = (Number(result.correct) || 0) + 1;
    }
    result.status = 'known';
  } else {
    if (countAttempt) {
      result.attempts = (Number(result.attempts) || 0) + 1;
      result.wrong = (Number(result.wrong) || 0) + 1;
    }
    result.status = 'review';
  }
  result.lastAt = at;
  return result;
}

/**
 * Selezione adattiva. Usa lo stato globale maturato in qualsiasi modalità e
 * mantiene una memoria delle domande deboli già servite nel ciclo corrente.
 */
export function selectAdaptiveQuestions(source, count, bucket = {}, knownRotation = {}, seed = '', statusFor = () => 'unanswered') {
  const questions = uniqueQuestions(source);
  const target = Math.min(Math.max(0, Math.floor(Number(count) || 0)), questions.length);
  if (!target) return {selected: [], bucket: {...bucket, version: 2, servedWeak: []}, knownRotation};

  const statusOf = question => normalizedStatus(statusFor(question));
  const weak = questions.filter(question => statusOf(question) !== 'known');
  const weakIds = new Set(weak.map(idOf));
  let servedWeak = new Set((Array.isArray(bucket?.servedWeak) ? bucket.servedWeak : []).map(String).filter(id => weakIds.has(id)));
  let cycle = Math.max(1, Math.floor(Number(bucket?.cycle) || 1));

  if (weak.length && weak.every(question => servedWeak.has(idOf(question)))) {
    servedWeak = new Set();
    cycle += 1;
  }

  const selected = [];
  const used = new Set();
  const tiers = ['unknown', 'review', 'unanswered'];
  for (const tier of tiers) {
    if (selected.length >= target) break;
    const available = weak.filter(question => statusOf(question) === tier && !servedWeak.has(idOf(question)) && !used.has(idOf(question)));
    const deck = shuffle(available, `${seed}|adaptive-${tier}|cycle-${cycle}`);
    for (const question of deck.slice(0, target - selected.length)) {
      selected.push(question);
      used.add(idOf(question));
    }
  }

  let nextKnownRotation = knownRotation;
  if (selected.length < target) {
    const known = questions.filter(question => statusOf(question) === 'known' && !used.has(idOf(question)));
    const result = selectRotatingQuestions(known, target - selected.length, knownRotation, `${seed}|adaptive-known`);
    selected.push(...result.selected);
    result.selected.forEach(question => used.add(idOf(question)));
    nextKnownRotation = result.rotation;
  }

  // Serve soltanto quando le domande deboli sono meno del numero richiesto.
  if (selected.length < target) {
    const fallback = shuffle(weak.filter(question => !used.has(idOf(question))), `${seed}|adaptive-weak-fill|cycle-${cycle}`);
    selected.push(...fallback.slice(0, target - selected.length));
  }

  for (const question of selected) {
    if (statusOf(question) !== 'known') servedWeak.add(idOf(question));
  }

  return {
    selected,
    bucket: {
      version: 2,
      cycle,
      servedWeak: [...servedWeak],
      size: questions.length,
      updatedAt: new Date().toISOString()
    },
    knownRotation: nextKnownRotation,
    selection: {
      weak: selected.filter(question => statusOf(question) !== 'known').length,
      known: selected.filter(question => statusOf(question) === 'known').length
    }
  };
}

/**
 * Selezione personale condivisa dalle due prove da 40. La memoria comprende
 * tutte le domande già mostrate, anche quando cambiano stato dopo la risposta.
 */
export function selectPersonalizedQuestions(source, count, exposure = {}, seed = '', statusFor = () => 'unanswered', options = {}) {
  const questions = uniqueQuestions(source);
  const target = Math.min(Math.max(0, Math.floor(Number(count) || 0)), questions.length);
  if (!target) return {selected: [], exposure: {...exposure, version: 3, seen: []}};

  const validIds = new Set(questions.map(idOf));
  const seen = new Set((Array.isArray(exposure?.seen) ? exposure.seen : []).map(String).filter(id => validIds.has(id)));
  const used = new Set();
  const selected = [];
  let cycle = Math.max(1, Math.floor(Number(exposure?.cycle) || 1));
  const statusOf = question => normalizedStatus(statusFor(question));
  const prefers = typeof options.prefer === 'function' ? options.prefer : () => false;

  const append = (pool, label) => {
    if (selected.length >= target) return;
    const available = pool.filter(question => !seen.has(idOf(question)) && !used.has(idOf(question)));
    const preferred = shuffle(available.filter(prefers), `${seed}|${label}|preferred|cycle-${cycle}`);
    const others = shuffle(available.filter(question => !prefers(question)), `${seed}|${label}|other|cycle-${cycle}`);
    for (const question of [...preferred, ...others].slice(0, target - selected.length)) {
      selected.push(question);
      used.add(idOf(question));
    }
  };

  const appendCycle = () => {
    if (options.adaptive) {
      append(questions.filter(question => statusOf(question) === 'unknown'), 'unknown');
      append(questions.filter(question => statusOf(question) === 'review'), 'review');
      append(questions.filter(question => statusOf(question) === 'unanswered'), 'unanswered');
    } else {
      append(questions.filter(question => statusOf(question) !== 'known'), 'weak');
    }
    append(questions.filter(question => statusOf(question) === 'known'), 'known');
  };

  appendCycle();
  if (selected.length < target) {
    cycle += 1;
    seen.clear();
    appendCycle();
  }

  selected.forEach(question => seen.add(idOf(question)));
  return {
    selected,
    exposure: {
      version: 3,
      cycle,
      seen: [...seen],
      size: questions.length,
      updatedAt: new Date().toISOString()
    },
    selection: {
      weak: selected.filter(question => statusOf(question) !== 'known').length,
      known: selected.filter(question => statusOf(question) === 'known').length
    }
  };
}
