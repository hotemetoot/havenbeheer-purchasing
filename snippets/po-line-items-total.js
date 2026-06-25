// PO Line Items — running total block (JS Block / RunJS)
// Placement: bottom of the PO detail popup's "Line Items" tab, below the lines table.
// Shows Σ(po_lines.line_total) + the PO currency (PR-copied, D46).
// Refresh: reactive MultiRecordResource — wire the add-line / edit-line / delete-line
//   form Submits' "After successful submission → Refresh data blocks" to target this block,
//   and its 'refresh' handler recomputes the sum. (Fallback: poll via setInterval — see below.)
// Canonical copy lives here because RunJS is NOT version-controlled (it's UI config).
// Built 2026-06-24. Verified working in the live app (incl. manual refresh).

const _ = ctx.libs.lodash;
const { React } = ctx.libs;
const { Card, Statistic } = ctx.libs.antd;

// Parent PO: detail page → ctx.record; row popup → ctx.popup.record
const po = (await ctx.getVar('ctx.record')) ?? (await ctx.getVar('ctx.popup.record'));
const poId = po?.id;
let currency = po?.currency;                       // PO currency = PR-copied (D46)

if (poId && !currency) {                           // fallback if the record didn't carry currency
  try {
    const { data } = await ctx.request({
      url: 'purchase_orders:get',
      params: { filterByTk: poId, fields: ['id', 'currency'] },
      skipNotify: true,
    });
    currency = data?.data?.currency;
  } catch (e) { ctx.logger?.error?.('PO header fetch failed', { err: e }); }
}

// nl-NL / Suriname style: 12.345,67  (Intl is NOT in the RunJS sandbox — format manually)
const fmt = (n) => {
  const [int, dec] = (Number(n) || 0).toFixed(2).split('.');
  return int.replace(/\B(?=(\d{3})+(?!\d))/g, '.') + ',' + dec;
};

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
  return (
    <Card size="small" style={{ marginTop: 8 }}>
      <Statistic
        title={ctx.t('Total of all line items')}
        loading={sum === null}
        value={sum ?? 0}
        formatter={(v) => `${fmt(v)} ${currency ?? ''}`.trim()}
      />
    </Card>
  );
}

ctx.render(<LinesTotal />);
