(() => {
  'use strict';

  const $ = id => document.getElementById(id);
  const escapeHtml = value => String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
  const card = (label, value, note = '') => `<article class="result-card"><span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong>${note ? `<small>${escapeHtml(note)}</small>` : ''}</article>`;

  async function fetchJson(url) {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`${url}: HTTP ${response.status}`);
    return response.json();
  }

  async function fetchJsonl(url) {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`${url}: HTTP ${response.status}`);
    const text = await response.text();
    return text.split(/\r?\n/).filter(line => line.trim()).map(line => JSON.parse(line));
  }

  function fmt(value, digits = 3) {
    if (value === null || value === undefined || Number.isNaN(Number(value))) return '—';
    return Number(value).toFixed(digits);
  }

  async function loadSemanticAtlas() {
    try {
      const [coverage, registry, molecular, survival, sync] = await Promise.all([
        fetchJson('../semantic_cards/SEMANTIC_CARD_COVERAGE_V0_14A1.json'),
        fetchJson('../semantic_cards/ENTITY_REGISTRY_CURRENT.json'),
        fetchJsonl('../semantic_cards/MOLECULAR_STATE_RELAXATION_V0_14A1.jsonl'),
        fetchJson('../benchmarks/MOLECULAR_STATE_RELAXATION_ACTIVATED_SURVIVAL_MATRIX_V0_14A1_PARTIAL.json'),
        fetchJson('../semantic_cards/SURFACE_SYNC_CURRENT.json'),
      ]);

      const populations = registry.generated_entity_populations;
      const modelCard = molecular.find(record => record.card_id === 'MODEL:MOLECULAR_STATE_RELAXATION:v0.14A1');
      const formulaCards = new Map(
        molecular.filter(record => record.entity_level === 'molecular_formula_screen').map(record => [record.identity.formula, record])
      );

      $('semantic-summary').innerHTML = [
        card('neutral atom bases', 36, 'H→Kr canonical base coverage'),
        card('compound candidates', populations.compound_relation_candidates_v0_1, 'deterministic v0.1 generated entities'),
        card('relational states', populations.relational_state_candidates_v0_13, '9 formulae × 3 unranked states'),
        card('molecular cards', populations.molecular_v0_14A1, 'one model card + nine formula cards'),
        card('molecular execution', `${modelCard.physical_control.completed_formulae}/${modelCard.physical_control.expected_formulae}`, `${modelCard.physical_control.completed_starts}/${modelCard.physical_control.expected_starts} frozen starts`),
        card('surface checkpoint', sync.scientific_checkpoint, sync.status),
      ].join('');

      $('stage-list').innerHTML = coverage.stages.map(stage =>
        card(`${stage.version} · ${stage.entity_level}`, stage.card_id, stage.epistemic_status)
      ).join('');

      const formulaOrder = ['NeF2','NeCl2','NeBr2','ArF2','ArCl2','ArBr2','KrF2','KrCl2','KrBr2'];
      $('formula-grid').innerHTML = formulaOrder.map(formula => {
        const record = formulaCards.get(formula);
        const cell = survival.cells[formula];
        const execution = record?.physical_control?.execution_status ?? 'MISSING_CARD';
        const gap = cell?.activated_to_lowest_weak_gap_kcal_mol;
        const activated = cell?.activated_successful;
        const starts = cell?.activated_starts;
        const note = execution === 'MISSING_EXECUTION_NOT_CHEMICAL_FAIL'
          ? 'No chemistry result imputed.'
          : `activated survival ${activated}/${starts}; gap to lowest weak = ${fmt(gap, 3)} kcal/mol`;
        return card(formula, execution, note);
      }).join('');

      const boundary = sync.current_boundary;
      $('boundary-list').innerHTML = [
        card('ArBr₂', boundary.ArBr2),
        card('Hessian admission', boundary.hessian_admission),
        card('ground-state ranking', boundary.ground_state_ranking),
        card('geometry-only topology', boundary.geometry_only_topology_assignment),
        card('survival matrix', survival.status, 'descriptive only; no fit and no threshold'),
        card('TIR / affective semantics', 'UNASSIGNED', 'explicit provenance required before assignment'),
      ].join('');

      $('semantic-data-status').textContent = 'Data: repository semantic surfaces loaded';
    } catch (error) {
      console.error(error);
      $('semantic-data-status').textContent = 'Data: unavailable — serve from repository root via HTTP';
      $('semantic-summary').innerHTML = card('semantic atlas', 'UNAVAILABLE', error.message);
    }
  }

  loadSemanticAtlas();
})();
