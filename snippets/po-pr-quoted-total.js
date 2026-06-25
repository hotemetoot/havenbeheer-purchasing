const _ = ctx.libs.lodash;
const { React } = ctx.libs;
const { Card, Statistic } = ctx.libs.antd;

// Parent PO: detail page → ctx.record; row popup → ctx.popup.record
const po = (await ctx.getVar('ctx.record')) ?? (await ctx.getVar('ctx.popup.record'));
const poId = po?.id;

// nl-NL / Suriname style: 12.345,67  (Intl is NOT in the sandbox — format manually)
const fmt = (n) => {
  const [int, dec] = (Number(n) || 0).toFixed(2).split('.');
  return int.replace(/\B(?=(\d{3})+(?!\d))/g, '.') + ',' + dec;
};

function QuotedTotal() {
  const [pr, setPr] = React.useState(null);   // { total, currency } | null while loading
  React.useEffect(() => {
    let alive = true;
    (async () => {
      if (!poId) { if (alive) setPr({ total: 0, currency: '' }); return; }
      try {
        // Walk PO → linked (approved) PR for its originally quoted figure
        const { data } = await ctx.request({
          url: 'purchase_orders:get',
          params: { filterByTk: poId, fields: ['id'], appends: ['purchase_request'] },
          skipNotify: true,
        });
        const r = data?.data?.purchase_request;
        if (alive) setPr({ total: Number(r?.quoted_total) || 0, currency: r?.quoted_currency ?? '' });
      } catch (e) {
        ctx.logger?.error?.('PR quoted-total fetch failed', { err: e });
        if (alive) setPr({ total: 0, currency: '' });
      }
    })();
    return () => { alive = false; };
  }, []);
  return (
    <Card size="small" style={{ marginTop: 0 }}>
      <Statistic
        title={ctx.t('Total quoted (approved PR)')}
        loading={pr === null}
        value={pr?.total ?? 0}
        formatter={(v) => `${fmt(v)} ${pr?.currency ?? ''}`.trim()}
      />
    </Card>
  );
}

ctx.render(<QuotedTotal />);
