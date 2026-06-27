// PO Line Items — running total + PR-budget check block (JS Block / RunJS)
// Placement: bottom of the PO detail popup's "Line Items" tab, below the lines table.
// Shows Σ(po_lines.line_total) + the PO currency (PR-copied, D46), the approved PR
//   ceiling (purchase_request.quoted_total), and a red over-budget warning when
//   Σ line_total > quoted_total (strict >, matching the Issue-gate cap — D52).
// Refresh: reactive MultiRecordResource — wire the add-line / edit-line / delete-line
//   form Submits' "After successful submission → Refresh data blocks" to target this block,
//   and its 'refresh' handler recomputes the sum. (Fallback: poll via setInterval — see below.)
// Canonical copy lives here because RunJS is NOT version-controlled (it's UI config).
// Built 2026-06-24. PR-total + over-budget warning added 2026-06-27.

const _ = ctx.libs.lodash;
const { React } = ctx.libs;
const { Card, Statistic } = ctx.libs.antd;
const { ExclamationCircleFilled } = ctx.libs.antdIcons;

// Parent PO: detail page → ctx.record; row popup → ctx.popup.record
const po = (await ctx.getVar('ctx.record')) ?? (await ctx.getVar('ctx.popup.record'));
const poId = po?.id;
let currency = po?.currency;                        // PO currency = PR-copied (D46)
let quotedTotal = po?.purchase_request?.quoted_total ?? null;  // approved PR ceiling

// Always resolve the PR ceiling (the PO record rarely carries the relation); also
// backfill currency in the same round-trip if it wasn't on the record.
if (poId && (quotedTotal === null || !currency)) {
  try {
    const { data } = await ctx.request({
      url: 'purchase_orders:get',
      params: {
        filterByTk: poId,
        fields: ['id', 'currency'],
        appends: ['purchase_request'],
      },
      skipNotify: true,
    });
    currency = currency ?? data?.data?.currency;
    quotedTotal = quotedTotal ?? data?.data?.purchase_request?.quoted_total ?? null;
  } catch (e) { ctx.logger?.error?.('PO header fetch failed', { err: e }); }
}

const hasCeiling = Number.isFinite(Number(quotedTotal));
const ceiling = hasCeiling ? Number(quotedTotal) : null;

// nl-NL / Suriname style: 12.345,67  (Intl is NOT in the RunJS sandbox — format manually)
const fmt = (n) => {
  const [int, dec] = (Number(n) || 0).toFixed(2).split('.');
  return int.replace(/\B(?=(\d{3})+(?!\d))/g, '.') + ',' + dec;
};
const withCcy = (v) => `${fmt(v)} ${currency ?? ''}`.trim();

const sumOf = (rows) => _.sumBy(rows ?? [], (r) => Number(r.line_total) || 0);

// Reactive resource → an external "refresh data blocks" action re-runs the sum
ctx.initResource('MultiRecordResource');
ctx.resource.setResourceName('po_lines');
ctx.resource.setFilter({ purchase_order: { id: poId } });
ctx.resource.setFields(['line_total']);
ctx.resource.setPageSize(500);                     // lists default to ~20 — avoid silent truncation

function LinesTotal() {
  const [sum, setSum] = React.useState(null);
  React.useEffect(() => {
    const onRefresh = () => setSum(sumOf(ctx.resource.getData()));
    ctx.resource.on('refresh', onRefresh);
    if (poId) ctx.resource.refresh(); else setSum(0);
    // Fallback if this block can't be selected as a refresh target:
    //   const t = setInterval(() => poId && ctx.resource.refresh(), 1500);
    //   return () => { clearInterval(t); ctx.resource.off?.('refresh', onRefresh); };
    return () => ctx.resource.off?.('refresh', onRefresh);
  }, []);

  // strict > matches the Issue-gate cap (D52): spending exactly the PR amount is allowed
  const overBudget = hasCeiling && sum !== null && sum > ceiling;
  const overBy = overBudget ? sum - ceiling : 0;

  return (
    <Card size="small" style={{ marginTop: 8 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 32, flexWrap: 'wrap' }}>
        <Statistic
          title={ctx.t('Approved PR total')}
          value={hasCeiling ? ceiling : '—'}
          formatter={(v) => (hasCeiling ? withCcy(v) : '—')}
        />
        <Statistic
          title={ctx.t('Total of all line items')}
          loading={sum === null}
          value={sum ?? 0}
          valueStyle={overBudget ? { color: '#cf1322' } : undefined}
          prefix={overBudget ? <ExclamationCircleFilled style={{ color: '#cf1322' }} /> : null}
          formatter={(v) => withCcy(v)}
        />
        {overBudget && (
          <div style={{ color: '#cf1322', flex: 1, minWidth: 200 }}>
            <div style={{ fontWeight: 500 }}>{ctx.t('Line items exceed the approved PR total')}</div>
            <div>{`${ctx.t('Over by')} ${withCcy(overBy)}. ${ctx.t('This PO cannot be issued until the total is at or below the approved amount.')}`}</div>
          </div>
        )}
      </div>
    </Card>
  );
}

ctx.render(<LinesTotal />);
